"""The global level: the same interval table, re-cut across the machine.

A session row answers "was this session mid-turn?". A global row answers "was
any session mid-turn?", which is the question the machine's utilization turns
on: one active terminal is work in progress whatever the other five are doing
([Measurement Prototype](/docs/measurement-prototype.md), assumptions 2 and 4).

Both levels are that one table grouped differently, which is what stops them
from disagreeing. Nothing here reads events. The rollup takes the frame the
definitive and graded stages built and cuts it at every bound, so a change to
how a turn or a gap is derived reaches the global level with no second
derivation to keep in step.

Each state combines by its own rule, because the states claim different things:

- **Union** for `claude_active`, `interrupted` and `human_present`: a moment
  belongs to the machine's state if any session claims it.
- **Intersection** for `dormant`: one session being dormant says nothing about
  the machine, which is dormant only when every session is (assumption 3).

Overlapping graded rows combine by complement — `1 - (1 - a)(1 - b)` — which is
assumption 8's global form: presence is one minus the chance every session was
absent at once. That treats the sessions as independent evidence, and they are
not. Two terminals idle through the same two hours are usually one human away
once, not two chances they were there, and the complement reads them as the
latter and lifts the confidence. Rows carrying 1.0 are unaffected by it, so the
presence rows are the only ones exposed. This is the same optimism the doc's
assumption 8 records at the global level, kept visible rather than corrected
here — correcting it needs a model of how sessions share a human, which the
store has nothing to fit.

A global row carries no `session_id`. It is about the machine, and any id on it
would name a session that does not own it.
"""

import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import pairwise

import pandas as pd

from dev_playbook.measure.intervals import DORMANT, interval_frame

# A global row belongs to the machine rather than to any one session.
GLOBAL_SESSION = None


class RollupError(Exception):
    """An interval frame this module will not roll up.

    Raised rather than worked around: two rows of one state overlapping inside a
    single session would be combined as two independent claims on the same
    moment, which lifts the confidence above what the evidence supports and
    looks like nothing but a slightly higher number.
    """


@dataclass(frozen=True)
class _Claim:
    """One row's claim on a moment: the session that made it, and how strongly."""

    session_id: str
    confidence: float


@dataclass(frozen=True)
class _Segment:
    """A span with a fixed set of claims: no row starts or ends inside it."""

    start: pd.Timestamp
    end: pd.Timestamp
    claims: tuple[_Claim, ...]


def union_intervals(frame: pd.DataFrame, state: str) -> pd.DataFrame:
    """Every moment any row of `frame` covers, as global rows of `state`.

    Overlapping rows merge into one span. Where they overlap the confidences
    combine by complement, so a moment two sessions each half-believe reads
    stronger than either alone; rows at 1.0 merge into plain spans of 1.0.
    """
    _refuse_double_claims(frame)
    return interval_frame(
        _merged(
            _global_row(
                state,
                segment,
                1 - math.prod(1 - claim.confidence for claim in segment.claims),
            )
            for segment in _segments(frame)
        )
    )


def intersect_intervals(frame: pd.DataFrame, state: str, sessions: int) -> pd.DataFrame:
    """Every moment all `sessions` cover at once, as global rows of `state`.

    `sessions` is how many sessions the machine ran, not how many appear in
    `frame`: a session with no row here covers nothing, and a moment it does not
    cover is not a moment they all do. Pass it from the whole interval table.
    """
    _refuse_double_claims(frame)
    return interval_frame(
        _merged(
            _global_row(
                state,
                segment,
                math.prod(claim.confidence for claim in segment.claims),
            )
            for segment in _segments(frame)
            if len({claim.session_id for claim in segment.claims}) == sessions
        )
    )


def global_intervals(frame: pd.DataFrame) -> pd.DataFrame:
    """The whole interval table rolled up across the machine, oldest first.

    Every state in the frame comes back, each combined by its own rule. The
    session count the dormant intersection needs is taken from the frame itself,
    so a session that ran the whole window — and therefore has no dormant row of
    its own — still keeps the machine out of dormancy.
    """
    sessions = frame["session_id"].nunique()
    rolled = [
        intersect_intervals(rows, state, sessions)
        if state == DORMANT
        else union_intervals(rows, state)
        for state, rows in frame.groupby("state")
    ]
    if not rolled:
        return interval_frame([])
    return (
        pd.concat(rolled)
        .sort_values(["start", "state"], kind="stable")
        .reset_index(drop=True)
    )


def state_seconds(frame: pd.DataFrame) -> pd.Series:
    """Wall-clock seconds per state, confidence ignored.

    What the table claims. For a global frame that is the machine's time in each
    state; for a session frame it is the sum over sessions, which runs past the
    clock when sessions overlap.
    """
    seconds = (frame["end"] - frame["start"]).dt.total_seconds()
    return seconds.groupby(frame["state"]).sum()


def expected_seconds(frame: pd.DataFrame) -> pd.Series:
    """Confidence-weighted seconds per state.

    What the table expects. Identical to `state_seconds` for the observed rows,
    which all carry 1.0, and the honest number for the graded ones: 128 hours of
    gaps at their fitted probabilities are about 36 expected present hours.
    """
    weighted = (frame["end"] - frame["start"]).dt.total_seconds() * frame["confidence"]
    return weighted.groupby(frame["state"]).sum()


# --- cutting the table at every bound -----------------------------------------


def _segments(frame: pd.DataFrame) -> Iterator[_Segment]:
    """The frame cut at every bound of every row, covered spans only.

    Between two consecutive bounds nothing starts or ends, so the set of rows
    covering that span is fixed and its combined confidence is one number. A
    zero-length row is left out: it covers no moment, so no span of the
    machine's time turns on it.
    """
    opened: dict[pd.Timestamp, list[_Claim]] = {}
    closed: dict[pd.Timestamp, list[_Claim]] = {}
    for row in frame.itertuples():
        if row.start >= row.end:
            continue
        claim = _Claim(row.session_id, row.confidence)
        opened.setdefault(row.start, []).append(claim)
        closed.setdefault(row.end, []).append(claim)

    active: list[_Claim] = []
    for left, right in pairwise(sorted(opened.keys() | closed.keys())):
        for claim in closed.get(left, ()):
            # Claims are compared by value, and two equal claims are
            # interchangeable in the arithmetic, so which copy goes is moot.
            active.remove(claim)
        active.extend(opened.get(left, ()))
        if active:
            yield _Segment(left, right, tuple(active))


def _global_row(state: str, segment: _Segment, confidence: float) -> dict:
    """One interval row over `segment`, belonging to the machine."""
    return {
        "start": segment.start,
        "end": segment.end,
        "state": state,
        "session_id": GLOBAL_SESSION,
        "confidence": confidence,
    }


def _merged(rows: Iterable[dict]) -> Iterator[dict]:
    """Touching rows of equal confidence joined into one.

    The sweep cuts at every bound of every session, so sessions overlapping end
    to end arrive as a string of touching segments. Left alone, one continuous
    stretch of Claude-active time would read on the timeline as a dozen bars
    with nothing between them.
    """
    current: dict | None = None
    for row in rows:
        if (
            current is not None
            and current["end"] == row["start"]
            and current["confidence"] == row["confidence"]
        ):
            current["end"] = row["end"]
            continue
        if current is not None:
            yield current
        current = row
    if current is not None:
        yield current


def _refuse_double_claims(frame: pd.DataFrame) -> None:
    """Refuse a frame in which one session claims the same moment twice.

    Rows of one state tile within a session rather than overlap — a turn runs
    submit to `Stop`, the gap after it runs `Stop` to the next submit — so an
    overlap means rows of two states, or of two runs, arrived together. Combining
    them would read one session's single claim as two independent ones.
    """
    for session, rows in frame.groupby("session_id"):
        ordered = rows.sort_values("start")
        reach = ordered["end"].cummax()
        if (ordered["start"].to_numpy()[1:] < reach.to_numpy()[:-1]).any():
            raise RollupError(f"session {session} claims the same moment twice")
