"""The host side of measurement: a receiver a sandboxed run sends its rows to.

Inside the container the measure-event hook has no store to write — the
container's filesystem is thrown away with the container. It sends each row
here instead, over TCP, and this inserts it into a real database on the host as
the user. See MEASUREMENT-OPTIONS.md for why TCP rather than a unix socket.

The container learns where to send by a one-line file mounted read-only at
SINK_INSIDE. Its presence is also what tells the hook it is sandboxed, so a
run without this mount writes SQLite exactly as a host session does.
"""

import contextlib
import json
import socket
import sqlite3
import tempfile
import threading
from pathlib import Path

from probe import podman

# The address the container uses to mean "the host's loopback". pasta's
# --map-host-loopback wires it to the host's 127.0.0.1, so a listener bound
# there is reachable from inside without ever appearing on the LAN. Link-local
# by convention; the value itself is arbitrary.
HOST_ALIAS = "169.254.1.2"

# What a run needs on its command line for that mapping to exist.
NETWORK = f"pasta:--map-host-loopback={HOST_ALIAS}"

# Where the hook looks for the sink file: $HOME/.local/share/claude-measure.
SINK_INSIDE = "/home/geoff/.local/share/claude-measure/sink"

# The real store, the same path measure-event writes from a host session. The
# receiver writes here because that is the whole point: a sandboxed run's
# events belong in the machine's measurement data, beside every other row.
DB_PATH = Path("~/.local/share/claude-measure/events.db").expanduser()

# These must match INSERT in dotfiles/dot-claude/hooks/measure-event, because
# what arrives is that hook's row_values() verbatim. A column added there is
# added here in the same edit.
SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    received_at TEXT,
    event TEXT,
    session_id TEXT,
    prompt_id TEXT,
    payload TEXT
)
"""

INSERT = """
INSERT INTO events (received_at, event, session_id, prompt_id, payload)
VALUES (?, ?, ?, ?, ?)
"""

# How long the accept loop waits before checking whether it has been asked to
# stop. Only the shutdown delay, so it is short.
POLL_SECONDS = 0.2

# How long one connection may take to deliver its row. The sender is on this
# machine's loopback; anything slower than this is a sender that died mid-row.
READ_TIMEOUT_SECONDS = 10.0


class Receiver:
    """A listener on the host's loopback, inserting every row that arrives.

    Hooks run async, so several rows can be in flight at once: each connection
    is served by its own thread, and one lock serializes the inserts. SQLite
    would serialize them anyway; the lock is what makes that visible.
    """

    def __init__(self, db_path: Path):
        """Bind the listener and pick a free port, without accepting yet."""
        self.db_path = db_path
        self.listener = socket.create_server(("127.0.0.1", 0))
        self.listener.settimeout(POLL_SECONDS)
        self.port = self.listener.getsockname()[1]
        self.rows = 0
        self.failures: list[BaseException] = []
        self._writing = threading.Lock()
        self._stop = threading.Event()
        self._servers: list[threading.Thread] = []
        self._accepting = threading.Thread(target=self._accept_loop, daemon=True)

    def start(self) -> None:
        """Begin accepting. The database and table are created here, not per row.

        WAL for the same reason measure-event asks for it: concurrent sessions
        write this store while reports read it. Persistent, so on the real
        database this reads back the mode it already has — it matters only for
        a database created from nothing, like the rehearsal's.
        """
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(SCHEMA)
        self._accepting.start()

    def _accept_loop(self) -> None:
        """Hand every connection to its own thread until asked to stop."""
        while not self._stop.is_set():
            try:
                conn, _ = self.listener.accept()
            except TimeoutError:
                continue
            server = threading.Thread(target=self._serve, args=(conn,), daemon=True)
            server.start()
            self._servers.append(server)

    def _serve(self, conn: socket.socket) -> None:
        """Read one row off one connection and insert it.

        The sender closes its write half when the row is complete, so the
        message ends at end-of-stream — nothing to frame and nothing to parse
        incrementally.

        A failure is kept rather than raised: this is not the run's thread, and
        an exception here would vanish. stop() raises it where it can be seen.
        """
        try:
            with conn:
                conn.settimeout(READ_TIMEOUT_SECONDS)
                chunks = []
                while chunk := conn.recv(65536):
                    chunks.append(chunk)
            row = json.loads(b"".join(chunks).decode("utf-8"))
            with self._writing:
                with sqlite3.connect(self.db_path) as connection:
                    connection.execute(INSERT, row)
                self.rows += 1
        except BaseException as error:
            self.failures.append(error)

    def stop(self) -> None:
        """Stop accepting, finish the rows already in flight, and report failures."""
        self._stop.set()
        self._accepting.join(timeout=POLL_SECONDS * 10)
        for server in self._servers:
            server.join(timeout=READ_TIMEOUT_SECONDS)
        self.listener.close()
        if self.failures:
            raise RuntimeError(
                f"{len(self.failures)} row(s) failed"
            ) from self.failures[0]

    def sink_line(self) -> str:
        """The one line the container reads to find this receiver."""
        return f"{HOST_ALIAS} {self.port}\n"


@contextlib.contextmanager
def receiving(db_path: Path = DB_PATH):
    """A running receiver, and the mount that points a container at it.

    The sink file is generated per run in a temporary directory and deleted on
    the way out, so no original is exposed — the mount rule from
    NOTES.md, the same reason the credential is mounted as a copy.
    """
    receiver = Receiver(db_path)
    with tempfile.TemporaryDirectory() as scratch:
        sink = Path(scratch) / "sink"
        sink.write_text(receiver.sink_line())
        receiver.start()
        try:
            yield receiver, podman.Mount(sink, Path(SINK_INSIDE))
        finally:
            receiver.stop()
