"""Behavioral tests for the read-only loader over the hook-event store.

Every test builds its own small database in `tmp_path` and reads that. The real
store at `~/.local/share/claude-measure/events.db` is live and is never touched
by the suite — a test that read it would drift with whatever the machine was
doing while it ran.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from dev_playbook.measure import store

SCHEMA = """
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    received_at TEXT,
    event TEXT,
    session_id TEXT,
    prompt_id TEXT,
    payload TEXT
)
"""


def a_payload(event: str, **fields: object) -> dict:
    """One hook payload with the envelope every real row carries."""
    return {
        "hook_event_name": event,
        "session_id": "5b1f",
        "transcript_path": "/home/geoff/.claude/projects/p/5b1f.jsonl",
        "cwd": "/home/geoff/workspace/dev-playbook",
        **fields,
    }


def a_store(path: Path, rows: list[tuple[str, object]]) -> Path:
    """Write a store at `path` from (received_at, payload) pairs; return the path.

    The payload goes in as text, so a test can store one that is not JSON at
    all — the hook does exactly that with stdin it cannot parse. Promoted
    columns are left NULL: they are convenience copies, and the loader is meant
    to read the payload instead.
    """
    connection = sqlite3.connect(path)
    connection.execute(SCHEMA)
    for received_at, payload in rows:
        text = payload if isinstance(payload, str) else json.dumps(payload)
        connection.execute(
            "INSERT INTO events (received_at, payload) VALUES (?, ?)",
            (received_at, text),
        )
    connection.commit()
    connection.close()
    return path


# --- the shape that comes out ----------------------------------------------


def test_load_events_returns_one_row_per_stored_event(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [
            ("2026-07-28T19:32:33.244361+00:00", a_payload("SessionStart")),
            ("2026-07-28T19:33:01.000000+00:00", a_payload("UserPromptSubmit")),
            ("2026-07-28T19:35:12.500000+00:00", a_payload("Stop")),
        ],
    )

    events = store.load_events(db)

    assert len(events) == 3
    assert list(events["event"]) == ["SessionStart", "UserPromptSubmit", "Stop"]


def test_load_events_promotes_the_fields_every_payload_carries(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:33:01.000000+00:00", a_payload("Stop", prompt_id="p-1"))],
    )

    row = store.load_events(db).iloc[0]

    assert row["event"] == "Stop"
    assert row["session_id"] == "5b1f"
    assert row["prompt_id"] == "p-1"
    assert row["cwd"] == "/home/geoff/workspace/dev-playbook"
    assert row["transcript_path"] == "/home/geoff/.claude/projects/p/5b1f.jsonl"


def test_load_events_reads_the_payload_not_the_promoted_columns(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:33:01.000000+00:00", a_payload("Notification"))],
    )
    connection = sqlite3.connect(db)
    connection.execute("UPDATE events SET event = 'Stop', session_id = 'wrong'")
    connection.commit()
    connection.close()

    row = store.load_events(db).iloc[0]

    assert row["event"] == "Notification"
    assert row["session_id"] == "5b1f"


def test_load_events_parses_received_at_as_a_utc_timestamp(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:32:33.244361+00:00", a_payload("SessionStart"))],
    )

    received_at = store.load_events(db)["received_at"]

    assert received_at.iloc[0] == pd.Timestamp("2026-07-28T19:32:33.244361Z")
    assert str(received_at.dtype) == "datetime64[us, UTC]"


def test_load_events_orders_rows_by_insertion_id(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [
            ("2026-07-28T19:40:00.000000+00:00", a_payload("SessionStart")),
            ("2026-07-28T19:31:00.000000+00:00", a_payload("Stop")),
        ],
    )

    events = store.load_events(db)

    assert list(events["id"]) == [1, 2]
    assert list(events["event"]) == ["SessionStart", "Stop"]


def test_load_events_keeps_the_parsed_payload_for_event_specific_fields(
    tmp_path: Path,
) -> None:
    db = a_store(
        tmp_path / "events.db",
        [
            (
                "2026-07-28T19:33:01.000000+00:00",
                a_payload(
                    "PostToolUse",
                    tool_name="Read",
                    duration_ms=12,
                    tool_input={"file_path": "/repo/src/a.py"},
                ),
            )
        ],
    )

    payload = store.load_events(db).iloc[0]["payload"]

    assert payload["tool_name"] == "Read"
    assert payload["duration_ms"] == 12
    assert payload["tool_input"] == {"file_path": "/repo/src/a.py"}


def test_load_events_returns_the_full_schema_for_an_empty_store(tmp_path: Path) -> None:
    db = a_store(tmp_path / "events.db", [])

    events = store.load_events(db)

    assert len(events) == 0
    assert list(events.columns) == [
        "id",
        "received_at",
        "payload",
        "event",
        "session_id",
        "prompt_id",
        "cwd",
        "transcript_path",
    ]


# --- what the store is allowed to be missing --------------------------------


def test_load_events_accepts_an_event_that_precedes_any_prompt(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:32:33.244361+00:00", a_payload("SessionStart"))],
    )

    row = store.load_events(db).iloc[0]

    assert row["prompt_id"] is None


def test_load_events_accepts_a_row_written_before_capture_kept_file_paths(
    tmp_path: Path,
) -> None:
    db = a_store(
        tmp_path / "events.db",
        [
            (
                "2026-07-28T19:33:01.000000+00:00",
                a_payload("PostToolUse", tool_name="Read", duration_ms=12),
            )
        ],
    )

    payload = store.load_events(db).iloc[0]["payload"]

    assert "tool_input" not in payload


# --- what it refuses --------------------------------------------------------


def test_load_events_refuses_a_payload_that_is_not_json(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:33:01.000000+00:00", '{"hook_event_name": "Stop", trunc')],
    )

    with pytest.raises(store.StoreError, match="row 1"):
        store.load_events(db)


def test_load_events_refuses_a_payload_that_is_not_an_object(tmp_path: Path) -> None:
    db = a_store(
        tmp_path / "events.db",
        [("2026-07-28T19:33:01.000000+00:00", ["Stop", "5b1f"])],
    )

    with pytest.raises(store.StoreError, match="not an object"):
        store.load_events(db)


def test_load_events_refuses_a_payload_missing_a_field_every_row_carries(
    tmp_path: Path,
) -> None:
    payload = a_payload("Stop")
    del payload["cwd"]
    db = a_store(tmp_path / "events.db", [("2026-07-28T19:33:01+00:00", payload)])

    with pytest.raises(store.StoreError, match="cwd"):
        store.load_events(db)


def test_load_events_neither_opens_nor_creates_a_store_that_is_absent(
    tmp_path: Path,
) -> None:
    absent = tmp_path / "events.db"

    with pytest.raises(sqlite3.OperationalError):
        store.load_events(absent)

    assert not absent.exists()
