"""The read-only door onto this machine's hook-event store.

One function matters here: `load_events` turns the `events` table into a tidy
frame with one row per hook event, the fields every payload carries promoted to
columns, and the parsed payload kept alongside for the event-specific fields
later stages read (`tool_name`, `prompt`, `command_name`, and the rest).

Two properties this module exists to guarantee:

- **It never writes.** The connection is opened through a `mode=ro` URI, so a
  stray `INSERT` fails and a missing database raises instead of being created.
  The store is live — other sessions append to it while this reads — and a
  reader that could write it is a reader that could corrupt the only record.
- **It reads the payload, not the promoted columns.** `event`, `session_id` and
  `prompt_id` exist as columns for convenience and are NULL whenever the key
  was absent or arrived as a non-string; the payload text is the authority for
  every field (see [Measurement Prototype](/docs/measurement-prototype.md)).

Row cleaning, interval derivation, and attribution all happen downstream. What
comes out of here is the store as it is, in a shape pandas can work with.
"""

import json
import sqlite3
from pathlib import Path
from urllib.parse import quote

import pandas as pd

DEFAULT_STORE = Path("~/.local/share/claude-measure/events.db")

# The payload key behind each promoted column. `hook_event_name` lands as
# `event` to match the store's own column name for it; the rest keep theirs.
PAYLOAD_KEYS = {
    "event": "hook_event_name",
    "session_id": "session_id",
    "prompt_id": "prompt_id",
    "cwd": "cwd",
    "transcript_path": "transcript_path",
}

# The promoted columns a payload must carry. Every one of the 12,093 rows in
# the store at time of writing has all four as strings; only `prompt_id` is
# legitimately absent (86 rows), because an event can precede any prompt.
REQUIRED_KEYS = ("event", "session_id", "cwd", "transcript_path")

# Oldest first, by insertion order: `id` is the only total order the store has,
# and `received_at` is the hook's arrival time, which concurrent sessions can
# interleave.
SELECT = "SELECT id, received_at, payload FROM events ORDER BY id"

COLUMNS = ("id", "received_at", "payload", *PAYLOAD_KEYS)


class StoreError(Exception):
    """A stored row this loader will not answer for.

    Raised rather than skipped: the hook records what it cannot parse so the
    evidence survives, and a reader that silently dropped those rows would
    report a clean timeline over a store that is not clean.
    """


def read_only_uri(path: Path) -> str:
    """The sqlite URI that opens `path` read-only, with `~` expanded.

    `mode=ro` is what makes a missing store an error instead of a new empty
    database — sqlite's default connect would create the file.
    """
    return f"file:{quote(str(path.expanduser()))}?mode=ro"


def event_row(row_id: int, received_at: str, payload: str) -> dict:
    """One `events` row as a tidy record: promoted fields plus the parsed payload.

    Fails loud twice — on a payload that is not JSON, and on one that parses to
    something other than an object — because both are shapes no downstream
    grouping can honestly account for, and both name the row id so the store
    can be inspected.

    `prompt_id` is the one promoted field allowed to be absent: an event that
    precedes any submission genuinely has none, and a `SessionEnd` fired by a
    UI builtin mints one matching no submission. It lands as None.
    """
    try:
        parsed = json.loads(payload)
    except ValueError as error:
        raise StoreError(f"row {row_id}: payload is not JSON — {error}") from error
    if not isinstance(parsed, dict):
        raise StoreError(
            f"row {row_id}: payload is a JSON {type(parsed).__name__}, not an object"
        )
    record: dict = {"id": row_id, "received_at": received_at, "payload": parsed}
    for column, key in PAYLOAD_KEYS.items():
        value = parsed.get(key)
        record[column] = value if isinstance(value, str) else None
    absent = [key for key in REQUIRED_KEYS if record[key] is None]
    if absent:
        raise StoreError(f"row {row_id}: payload has no {', '.join(absent)}")
    return record


def load_events(db_path: Path = DEFAULT_STORE) -> pd.DataFrame:
    """The whole store as a tidy frame, one row per hook event, oldest first.

    Columns are `id`, `received_at` (UTC-aware), the promoted `event`,
    `session_id`, `prompt_id`, `cwd` and `transcript_path`, and `payload` — the
    parsed dict, carried so a later stage reads an event-specific field without
    parsing the JSON a second time.

    The whole table is read in one pass. At ~12,000 rows and 24 MB that is
    cheaper than any windowing scheme, and it keeps this function honest: it
    answers for the store as it is, and callers filter.
    """
    connection = sqlite3.connect(read_only_uri(db_path), uri=True)
    try:
        rows = connection.execute(SELECT).fetchall()
    finally:
        connection.close()
    frame = pd.DataFrame(
        [event_row(*row) for row in rows], columns=list(COLUMNS), dtype=object
    )
    # Explicit ISO8601: the hook writes microsecond-precision UTC, and letting
    # pandas infer per-column would guess a format from the first row.
    frame["received_at"] = pd.to_datetime(
        frame["received_at"], utc=True, format="ISO8601"
    )
    frame["id"] = frame["id"].astype("int64")
    return frame
