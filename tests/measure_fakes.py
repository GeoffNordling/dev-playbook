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


def at(second: float) -> pd.Timestamp:
    """The timestamp `second` seconds into the window.

    `a_frame` lands payloads one second apart starting at `at(1)`, so the Nth
    payload of such a frame — counting from one — is at `at(N)`. A frame built
    by `a_timed_frame` lands each payload at the second it was given.
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
    return a_timed_frame(list(enumerate(payloads, start=1)))


def a_timed_frame(timed: list[tuple[float, dict]]) -> pd.DataFrame:
    """The loader's output shape, each payload landing at the second it is paired with.

    For anything whose derivation turns on how long something took. Ids follow
    list order, which is the store's own total order, so a pair whose seconds
    run backwards is a genuine out-of-order arrival rather than a broken frame.
    """
    records = [
        store.event_row(index, at(second).isoformat(), json.dumps(payload))
        for index, (second, payload) in enumerate(timed, start=1)
    ]
    frame = pd.DataFrame(records, columns=list(store.COLUMNS), dtype=object)
    frame["received_at"] = pd.to_datetime(
        frame["received_at"], utc=True, format="ISO8601"
    )
    frame["id"] = frame["id"].astype("int64")
    return frame
