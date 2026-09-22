"""The helpers `tests/conftest.py` held for the factory's test modules.

Moved here whole on 2026-09-20 with the modules that import them; the modules
also import `init_repo` and `commit_all` from the shared `tests/conftest.py`,
which stayed.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, NamedTuple


class StoredRow(NamedTuple):
    """One run-ledger row as a factory test reads it back out of the store."""

    kind: str
    node: str | None
    session_id: str | None
    payload: dict[str, Any]


def ledger_rows(db: Path) -> list[StoredRow]:
    """Every row the run ledger holds, in write order; none before it exists.

    Read with SQL rather than through ``dev_playbook.factory.ledger``: that
    module's own reads answer questions about open windows and live jobs, and a
    test asking what was written needs the rows themselves.
    """
    if not db.exists():
        return []
    with sqlite3.connect(db) as connection:
        rows = connection.execute(
            "SELECT kind, node, session_id, payload FROM ledger ORDER BY id"
        ).fetchall()
    return [
        StoredRow(kind, node, session_id, json.loads(payload))
        for kind, node, session_id, payload in rows
    ]


def write_definition(directory: Path, stem: str, frontmatter: dict[str, Any]) -> Path:
    """Write one agent definition, its frontmatter rendered as YAML."""
    body = "\n".join(f"{key}: {value}" for key, value in frontmatter.items())
    path = directory / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{body}\n---\n\nThe node's instructions.\n")
    return path


def process_state(pid: int) -> str | None:
    """The single-letter process-table state of ``pid``, or None once it is gone.

    Read from ``/proc`` rather than asked with ``os.kill(pid, 0)``: a signal
    probe answers "alive" for a zombie, and a child whose launcher was destroyed
    is reparented, so it is a zombie until the reaper collects it. What these
    tests measure is that it stopped running, which the state letter says and
    the signal probe does not.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # The comm field is parenthesized and may hold spaces of its own, so the
    # split starts after the last ')' rather than at the second field.
    return stat.rpartition(")")[2].split()[0]
