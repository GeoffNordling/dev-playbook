"""Frame builders shared by the measurement tests.

A frame is built in memory here rather than through a fixture database: the
loader has its own tests, and everything downstream of it is about what it does
with rows, not about how they were read. The one thing borrowed from the loader
is `event_row`, so a frame under test has exactly the shape `load_events`
produces.
"""

import json

import pandas as pd

from dev_playbook.measure import store

BASE = pd.Timestamp("2026-07-28T19:00:00Z")


def at(second: int) -> pd.Timestamp:
    """The timestamp `second` seconds into the window.

    Payloads land one second apart starting at `at(1)`, so the Nth payload of a
    frame — counting from one — is at `at(N)`.
    """
    return BASE + pd.Timedelta(seconds=second)


def a_payload(event: str, session: str = "5b1f", **fields: object) -> dict:
    """One hook payload with the envelope every real row carries."""
    return {
        "hook_event_name": event,
        "session_id": session,
        "transcript_path": f"/home/geoff/.claude/projects/p/{session}.jsonl",
        "cwd": "/home/geoff/workspace/dev-playbook",
        **fields,
    }


def a_frame(payloads: list[dict]) -> pd.DataFrame:
    """The loader's output shape, one row per payload, a second apart in order."""
    records = [
        store.event_row(index, at(index).isoformat(), json.dumps(payload))
        for index, payload in enumerate(payloads, start=1)
    ]
    frame = pd.DataFrame(records, columns=list(store.COLUMNS), dtype=object)
    frame["received_at"] = pd.to_datetime(
        frame["received_at"], utc=True, format="ISO8601"
    )
    frame["id"] = frame["id"].astype("int64")
    return frame
