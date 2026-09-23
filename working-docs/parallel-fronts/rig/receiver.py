"""Part 4's hook-event receiver: the prototype's sink.Receiver, standalone.

Binds the host's 127.0.0.1 on a free port, writes the one-line sink file the
sandbox's measure-event reads, and inserts every row that arrives into the
real measurement store. Runs until SIGTERM, then prints how many rows landed.

Usage: python3 receiver.py <sink file to write>
"""

import json
import signal
import socket
import sqlite3
import sys
import threading
from pathlib import Path

HOST_ALIAS = "169.254.1.2"
DB_PATH = Path("~/.local/share/claude-measure/events.db").expanduser()
INSERT = (
    "INSERT INTO events (received_at, event, session_id, prompt_id, payload)"
    " VALUES (?, ?, ?, ?, ?)"
)

sink_file = Path(sys.argv[1])
listener = socket.create_server(("127.0.0.1", 0))
listener.settimeout(0.2)
port = listener.getsockname()[1]
sink_file.write_text(f"{HOST_ALIAS} {port}\n")

lock = threading.Lock()
stop = threading.Event()
rows = 0
failures: list[BaseException] = []
servers: list[threading.Thread] = []


def serve(conn: socket.socket) -> None:
    """Read one row from a connection and insert it into the store."""
    global rows
    try:
        with conn:
            conn.settimeout(10)
            chunks = []
            while chunk := conn.recv(65536):
                chunks.append(chunk)
        row = json.loads(b"".join(chunks).decode())
        with lock:
            with sqlite3.connect(DB_PATH) as db:
                db.execute(INSERT, row)
            rows += 1
    except BaseException as error:
        failures.append(error)


signal.signal(signal.SIGTERM, lambda *_: stop.set())
print(f"receiver on 127.0.0.1:{port}", flush=True)
while not stop.is_set():
    try:
        conn, _ = listener.accept()
    except TimeoutError:
        continue
    thread = threading.Thread(target=serve, args=(conn,), daemon=True)
    thread.start()
    servers.append(thread)
for thread in servers:
    thread.join(timeout=10)
listener.close()
print(f"receiver took {rows} rows, {len(failures)} failures", flush=True)
for failure in failures:
    print(f"  failure: {failure!r}", flush=True)
sys.exit(1 if failures else 0)
