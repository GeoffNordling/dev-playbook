"""The host end of the hook logging: rows from a container into the event store.

The user's hooks inside a container cannot reach the host's measurement
database, so each one sends its row over TCP instead. The receiver listens on
the host's 127.0.0.1 at a free port and writes a one-line sink file,
``169.254.1.2 <port>``, which the container mounts; the container's network
maps 169.254.1.2 to the host's loopback. Every row that arrives is inserted
into the real store, as the hook would have inserted it on the host.

One receiver serves one call: started before the container, stopped after.
"""

import json
import socket
import sqlite3
import threading
from pathlib import Path

HOST_ALIAS = "169.254.1.2"
"""The address the container reaches the host's loopback at."""
NETWORK = f"pasta:--map-host-loopback={HOST_ALIAS}"
"""The podman network option that makes that address work."""
EVENTS_DB = Path("~/.local/share/claude-measure/events.db").expanduser()
INSERT = (
    "INSERT INTO events (received_at, event, session_id, prompt_id, payload)"
    " VALUES (?, ?, ?, ?, ?)"
)


class ReceiverFault(Exception):
    """A row reached the receiver and was not stored."""


class Receiver:
    """Listen for hook rows until stopped; ``stop`` fails loud on a lost row."""

    def __init__(self, sink: Path, db: Path) -> None:
        """Bind a free port and write the sink file naming it."""
        self.db = db
        self.rows = 0
        self.failures: list[BaseException] = []
        self.lock = threading.Lock()
        self.done = threading.Event()
        self.servers: list[threading.Thread] = []
        self.listener = socket.create_server(("127.0.0.1", 0))
        self.listener.settimeout(0.2)
        sink.write_text(f"{HOST_ALIAS} {self.listener.getsockname()[1]}\n")
        self.thread = threading.Thread(target=self.accept, daemon=True)
        self.thread.start()

    def accept(self) -> None:
        """Take connections until stopped, one thread for each."""
        while not self.done.is_set():
            try:
                conn, _ = self.listener.accept()
            except TimeoutError:
                continue
            server = threading.Thread(target=self.serve, args=(conn,), daemon=True)
            server.start()
            self.servers.append(server)

    def serve(self, conn: socket.socket) -> None:
        """Read one row from a connection and insert it into the store."""
        try:
            with conn:
                conn.settimeout(10)
                chunks = []
                while chunk := conn.recv(65536):
                    chunks.append(chunk)
            row = json.loads(b"".join(chunks).decode())
            with self.lock, sqlite3.connect(self.db) as db:
                db.execute(INSERT, row)
                self.rows += 1
        except BaseException as error:  # noqa: BLE001 - stop() reports every loss
            with self.lock:
                self.failures.append(error)

    def stop(self) -> int:
        """Stop listening, finish every open row, and return how many were stored."""
        self.done.set()
        self.thread.join()
        for server in self.servers:
            server.join(timeout=10)
        self.listener.close()
        if hung := sum(server.is_alive() for server in self.servers):
            raise ReceiverFault(f"{hung} hook rows still arriving after 10 seconds")
        if self.failures:
            raise ReceiverFault(
                f"{len(self.failures)} hook rows lost: {self.failures[0]!r}"
            )
        return self.rows
