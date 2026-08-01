"""The interval table, and the rows of it the events state outright.

Every derived number in this prototype is a grouping of one table: `start`,
`end`, `state`, `session_id`, `confidence`. Session level and global level are
that table grouped differently, which is what stops them from disagreeing
([Measurement Prototype](/docs/measurement-prototype.md)).

This module builds the definitive rows — the ones that need no inference:

- **`claude_active`** — a submit and the `Stop` carrying its `prompt_id`. Claude
  Code was working between them, model time and tool time alike.
- **`interrupted`** — a submit whose turn produced no `Stop`, closed at the next
  submit in that session. An ESC interrupt fires no event at all, so the turn
  would otherwise look like it never ended; the following submit is the last
  instant the store can prove Claude was still on it.
- **`dormant`** — the span of the window before a session's first event and
  after its last. The session did not exist then, which is what lets the clock
  run across the whole window rather than only while sessions are open.

`confidence` is how strongly the store backs the row. These rows carry 1.0: an
`interrupted` row's end is an upper bound rather than the interrupt instant, but
its state names that, and the span itself is bounded by two observed events. The
graded rows — a gap between a `Stop` and the next submit, where presence is
fitted rather than seen — come from elsewhere and carry a probability.

**Do not sum `interrupted` into Claude-active time.** Its end is the next
submit, which is the interrupt instant only if the human resubmitted straight
away. Over the whole store the 100 interrupted turns run to a 29-second median
against a 15.7-hour maximum: one turn interrupted before the human left for the
night carries the whole night inside it. The state is kept separate for exactly
that reason. Closing the bound properly needs the same fitting a `Stop`-to-submit
gap gets, because after the interrupt the two are the same unobserved thing.

Two things this module does not do. It does not persist: the derivation changes
as the assumptions are tuned, and a stale table on disk is worse than none. And
it does not clean — feed it the output of [`clean`](clean.py), or ghost sessions
become dormant rows and harness pseudo-prompts become turns.

Pairing is by `prompt_id` alone, never by position: the store carries sessions
with more `Stop` rows than submits, so pairing the Nth with the Nth is wrong. A
`Stop` whose `prompt_id` matches no submit in the frame is expected rather than
alarming — dropping the task-notification pseudo-prompts strands their stops,
and a window can cut between a submit and its stop.
"""

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

SUBMIT = "UserPromptSubmit"
STOP = "Stop"

CLAUDE_ACTIVE = "claude_active"
INTERRUPTED = "interrupted"
DORMANT = "dormant"

# The confidence of a row the events state outright, as against the fitted
# probability a gap row carries.
OBSERVED = 1.0

INTERVAL_COLUMNS = ("start", "end", "state", "session_id", "confidence")

# `state` and `session_id` are left to pandas — a global row's session id is
# absent, and the string dtype it picks handles that. The other three are
# pinned: an empty frame otherwise types its bounds by guesswork, and a
# resolution mismatch against the store's microsecond stamps is silent.
INTERVAL_DTYPES = {
    "start": "datetime64[us, UTC]",
    "end": "datetime64[us, UTC]",
    "confidence": "float64",
}


class IntervalError(Exception):
    """A frame this module will not derive intervals from.

    Raised rather than worked around: every shape that reaches it would
    otherwise produce an interval table that looks complete and is wrong —
    a turn ending before it began subtracts time from a total silently.
    """


@dataclass(frozen=True)
class Intervals:
    """An interval table, and the turns that could not be closed.

    `unresolved` counts submits with neither a `Stop` nor a following submit in
    their session: the last turn of a session that is still running, or one an
    ESC interrupt ended with nothing after it. They contribute no row, so
    Claude-active time is a lower bound by however many this counts.
    """

    frame: pd.DataFrame
    unresolved: int


def interval_frame(rows: Iterable[dict]) -> pd.DataFrame:
    """The interval schema over `rows`, with the bounds and confidence typed.

    The one constructor for interval rows, so every stage that adds rows to the
    table produces the same columns in the same order and the same dtypes,
    including when it produces none.
    """
    return pd.DataFrame(list(rows), columns=list(INTERVAL_COLUMNS)).astype(
        INTERVAL_DTYPES
    )


def turn_intervals(events: pd.DataFrame) -> Intervals:
    """One row per submit: the turn it started, closed by its `Stop` or an interrupt.

    Submits are walked in `id` order, the store's only total order — `received_at`
    is the hook's arrival time, and hooks are asynchronous.
    """
    stops = events[events["event"] == STOP]
    repeated = sorted(set(stops.loc[stops["prompt_id"].duplicated(), "prompt_id"]))
    if repeated:
        raise IntervalError(f"more than one Stop for prompt {', '.join(repeated)}")
    stop_at = dict(zip(stops["prompt_id"], stops["received_at"], strict=True))

    submits = events[events["event"] == SUBMIT].sort_values("id")
    following = submits.groupby("session_id")["received_at"].shift(-1)
    rows = []
    unresolved = 0
    for submit, next_submit in zip(submits.itertuples(), following, strict=True):
        # A submit with no Stop is an interrupted turn, not a missing row: ESC
        # fires nothing, so the absence is the only evidence the interrupt left.
        end = stop_at.get(submit.prompt_id)
        state = CLAUDE_ACTIVE
        if end is None:
            end, state = next_submit, INTERRUPTED
        if pd.isna(end):
            unresolved += 1
            continue
        rows.append(
            {
                "start": submit.received_at,
                "end": end,
                "state": state,
                "session_id": submit.session_id,
                "confidence": OBSERVED,
            }
        )

    frame = interval_frame(rows)
    backwards = frame[frame["end"] < frame["start"]]
    if not backwards.empty:
        raise IntervalError(f"{len(backwards)} turns end before they start")
    return Intervals(frame, unresolved)


def dormant_intervals(
    events: pd.DataFrame, window: tuple[pd.Timestamp, pd.Timestamp]
) -> pd.DataFrame:
    """The spans of `window` each session did not exist for.

    Up to two rows per session — before its first event and after its last.
    A session covering the whole window gets neither.

    `window` must contain every event: dormancy is measured against its edges,
    so a window narrower than the frame would put a session's own activity
    inside a span claiming it did not exist.
    """
    start, end = window
    outside = events[(events["received_at"] < start) | (events["received_at"] > end)]
    if not outside.empty:
        raise IntervalError(f"{len(outside)} events fall outside {start} to {end}")

    bounds = events.groupby("session_id")["received_at"].agg(first="min", last="max")
    rows = []
    for session in bounds.itertuples():
        for span_start, span_end in ((start, session.first), (session.last, end)):
            if span_start < span_end:
                rows.append(
                    {
                        "start": span_start,
                        "end": span_end,
                        "state": DORMANT,
                        "session_id": session.Index,
                        "confidence": OBSERVED,
                    }
                )
    return interval_frame(rows)


def definitive_intervals(
    events: pd.DataFrame, window: tuple[pd.Timestamp, pd.Timestamp] | None = None
) -> Intervals:
    """Every interval row the events state outright, oldest first.

    Pass `window` to measure dormancy against a chosen span. Omitted, the frame's
    own first and last event bound it — a caller that chose no window is asking
    about exactly the events it handed over, and against that window the earliest
    and latest sessions are never dormant.
    """
    turns = turn_intervals(events)
    if window is None:
        window = (events["received_at"].min(), events["received_at"].max())
    frame = pd.concat([turns.frame, dormant_intervals(events, window)])
    return Intervals(
        frame.sort_values(["start", "session_id"], kind="stable").reset_index(
            drop=True
        ),
        turns.unresolved,
    )
