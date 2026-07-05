"""The seen-set: membership-only partition and idempotent recording of keys.

A key is an opaque string the caller computed; this module only remembers which
strings it has been told to remember. It never hashes, reads files, or
canonicalizes, and carries no domain vocabulary.
"""

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import NamedTuple


class Partition(NamedTuple):
    """A batch of keys split by membership in the seen-set."""

    seen: list[str]
    unseen: list[str]


def _store_path() -> Path:
    """Resolve the global seen-set file under the XDG cache directory."""
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"  # XDG default when unset
    return base / "skipcache" / "seen.sqlite"


def _connect() -> sqlite3.Connection:
    """Open the seen-set, creating its directory and single-column schema if absent."""
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY)")
    return conn


def filter(keys: list[str]) -> Partition:
    """Partition keys into those already recorded and those not, preserving order."""
    if not keys:
        return Partition(seen=[], unseen=[])
    placeholders = ",".join("?" * len(keys))
    with closing(_connect()) as conn:
        rows = conn.execute(
            f"SELECT key FROM seen WHERE key IN ({placeholders})", keys
        ).fetchall()
    recorded = {row[0] for row in rows}
    seen = [key for key in keys if key in recorded]
    unseen = [key for key in keys if key not in recorded]
    return Partition(seen=seen, unseen=unseen)


def record(keys: list[str]) -> None:
    """Add exactly these keys to the seen-set; idempotent and persistent."""
    with closing(_connect()) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO seen (key) VALUES (?)", [(key,) for key in keys]
        )
        conn.commit()
