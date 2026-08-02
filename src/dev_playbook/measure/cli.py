"""The one command that runs the measurement pipeline over a window.

Everything the other modules build is assembled here in one pass: the store is
read, the rows are cleaned, the events are attributed, the interval table is
derived — definitive rows and graded ones — and the table is drawn to a
self-contained HTML page ([Measurement Prototype](/docs/measurement-prototype.md)).

Nothing is persisted but the page. The interval table is recomputed from the
store on every run, because the derivation is still moving and a stale table
would be believed.

Two things the run prints alongside the page, and would be dishonest without:

- **What it threw away.** Each cleaning reports its own removed count, so a
  reader sees the blind spots the picture was drawn around rather than a total
  that looks complete.
- **The model behind the faint bars.** Presence is a fitted probability, and a
  confidence of 0.31 on a two-hour gap means nothing without the fit that
  assigned it. The fitted parameters print with the totals.

The totals print at both levels — the sum over sessions and the machine's own
clock — from the one table, which is what stops the two from disagreeing.
"""

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from dev_playbook.measure import clean, intervals, presence, rollup, store, timeline
from dev_playbook.measure.attribute import WORKSPACE, AttributionError, attributed
from dev_playbook.measure.presence import human_seconds

# The four cleanings, in the order they must run: ghost sessions are only
# visible once the pseudo-prompts that keep them looking alive are gone.
CLEANINGS = (
    clean.collapse_expansions,
    clean.drop_phantom_subagent_stops,
    clean.drop_task_notifications,
    clean.drop_ghost_sessions,
)

# The store keeps time in UTC, and so does everything derived from it. A bound
# typed without a zone is read as UTC rather than as the reader's local time:
# guessing the zone would shift a window by hours without saying so.
UTC = "UTC"

# The totals table: one block per level, and for each state its wall clock and
# what that clock is worth once confidence is applied. The level is a column
# rather than two separate tables so the same state can be read across it.
LEVEL_HEADINGS = ("level", "state", "wall", "expected")
LEVEL_WIDTH = 10
STATE_WIDTH = 15
SECONDS_WIDTH = 10

SESSION_LEVEL = "sessions"
MACHINE_LEVEL = "machine"

EPILOG = """\
examples:
  the whole store      measure-timeline activity.html
  since a moment       measure-timeline activity.html --since 2026-07-30
  a closed window      measure-timeline activity.html --since 2026-07-30T08:00 --until 2026-07-31
  by what was worked   measure-timeline activity.html --lane repo

Bounds are UTC. The page inlines plotly and is a few megabytes; it opens with
no network.
"""


class PipelineError(Exception):
    """A run this command will not make.

    Raised for the shapes that would otherwise produce an empty or misleading
    page — a window holding no events, or one whose bounds are the wrong way
    round.
    """


@dataclass(frozen=True)
class Run:
    """One pass of the pipeline: what was read, what was derived, what it rests on.

    Kept whole so the report is a function of the run rather than something
    printed as the pipeline goes, which would make the numbers unavailable to
    any other caller.
    """

    window: tuple[pd.Timestamp, pd.Timestamp]
    stored: int
    windowed: int
    cleanings: tuple[clean.Cleaning, ...]
    events: pd.DataFrame
    table: pd.DataFrame
    unresolved: int
    fit: presence.MixtureFit


def timestamp(text: str) -> pd.Timestamp:
    """A window bound as the store keeps time — UTC, whatever the text said.

    A date, a date and time, or either with an offset. An offset is honoured
    and converted; text without one is UTC, as the help says.
    """
    moment = pd.Timestamp(text)
    if moment.tzinfo is None:
        return moment.tz_localize(UTC)
    return moment.tz_convert(UTC)


def windowed(
    events: pd.DataFrame,
    since: pd.Timestamp | None = None,
    until: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp]]:
    """The events inside the window, and the window itself.

    An omitted bound falls back to the store's own edge — a caller that named
    no window is asking about everything there is. That is a real state rather
    than a papered-over default: the whole store is the window then, and
    dormancy is measured against it.

    The window is cut before the rows are cleaned, which is the order the
    cleanings were written for: each one treats a pair the window split as a
    fact about the window rather than a defect.
    """
    if events.empty:
        raise PipelineError("the store holds no events")
    first, last = events["received_at"].min(), events["received_at"].max()
    start = first if since is None else since
    end = last if until is None else until
    if start > end:
        # Both a backwards pair of bounds and a single bound past the store's
        # own edge land here, and the store's span is what tells the two apart.
        raise PipelineError(
            f"the window {start} to {end} is empty; the store runs {first} to {last}"
        )
    inside = events[
        (events["received_at"] >= start) & (events["received_at"] <= end)
    ].reset_index(drop=True)
    if inside.empty:
        raise PipelineError(f"no events between {start} and {end}")
    return inside, (start, end)


def cleaned(events: pd.DataFrame) -> tuple[pd.DataFrame, tuple[clean.Cleaning, ...]]:
    """The events with all four cleanings applied, and what each one took out."""
    frame = events
    applied = []
    for technique in CLEANINGS:
        cleaning = technique(frame)
        frame = cleaning.frame
        applied.append(cleaning)
    return frame, tuple(applied)


def pipeline(
    db_path: Path = store.DEFAULT_STORE,
    since: pd.Timestamp | None = None,
    until: pd.Timestamp | None = None,
    workspace: Path = WORKSPACE,
) -> Run:
    """The whole derivation, from the store to one interval table.

    The definitive rows and the graded ones go into the same frame, sorted
    together: they are one table, and the levels and the view all read it.
    """
    events = store.load_events(db_path)
    inside, window = windowed(events, since, until)
    rows, cleanings = cleaned(inside)
    rows = attributed(rows, workspace=workspace)
    definitive = intervals.definitive_intervals(rows, window)
    graded = presence.presence_intervals(rows)
    table = (
        pd.concat(
            [presence.grade_interrupts(definitive.frame, graded.fit), graded.frame]
        )
        .sort_values(["start", "session_id"], kind="stable")
        .reset_index(drop=True)
    )
    return Run(
        window=window,
        stored=len(events),
        windowed=len(inside),
        cleanings=cleanings,
        events=rows,
        table=table,
        unresolved=definitive.unresolved,
        fit=graded.fit,
    )


def report(run: Run) -> str:
    """The run as text: the window, what was dropped, the fit, and both levels."""
    start, end = run.window
    lines = [
        f"window {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M} UTC "
        f"({human_seconds((end - start).total_seconds())})",
        f"{run.stored} rows in the store, {run.windowed} in the window",
        *(
            f"  -{cleaning.removed} rows: {cleaning.technique}"
            for cleaning in run.cleanings
        ),
        f"{len(run.events)} events over "
        f"{run.events['session_id'].nunique()} sessions, "
        f"{len(run.table)} intervals",
    ]
    if run.unresolved:
        # Not a failure: a session mid-turn when the window closed has a submit
        # nothing closes. It contributes no row, so the totals below are short
        # by whatever those turns ran for, and saying so is the only way a
        # reader can tell a lower bound from a total.
        lines.append(
            f"{run.unresolved} turns are still open, so Claude-active time is "
            f"a lower bound"
        )
    return "\n".join([*lines, run.fit.summary(), *_levels(run.table)])


def main(argv: list[str], workspace: Path = WORKSPACE) -> int:
    """Run the pipeline over the chosen window and write the page; nonzero on error.

    Every error this raises is a legible one — a missing store, an empty
    window, a window too quiet to fit a mixture over — so it is reported as one
    line on stderr rather than a traceback the reader has to read backwards.
    """
    args = _parse_args(argv)
    try:
        run = pipeline(Path(args.db), args.since, args.until, workspace=workspace)
        path = timeline.write_timeline(
            timeline.laned(run.table, args.lane, run.events),
            Path(args.output),
            args.title or _title(args.lane, run.window),
            args.zone,
        )
    except (
        AttributionError,
        PipelineError,
        intervals.IntervalError,
        presence.PresenceError,
        rollup.RollupError,
        sqlite3.Error,
        store.StoreError,
        timeline.TimelineError,
    ) as error:
        print(f"measure-timeline: {error}", file=sys.stderr)
        return 1
    print(report(run))
    print(f"wrote {path}")
    return 0


def run_cli() -> int:
    """Console-script entry point: run the command over this process's own argv."""
    return main(sys.argv[1:])


# --- the parts of the report ---------------------------------------------------


def _levels(table: pd.DataFrame) -> list[str]:
    """Both levels of the one table, state by state, in seconds a human reads.

    The session block sums the sessions and so runs past the clock when they
    overlap — 62 sessions dormant through the same night is 62 dormant nights
    there and one on the machine's own clock. The distance between the blocks
    is what the level costs, which is what having two levels is for.

    A state the machine never reached has no row in its block: `dormant` goes
    when some session existed at every moment, and no line is a truer answer
    than a zero would be.
    """
    level_heading, state_heading, *total_headings = LEVEL_HEADINGS
    rows = [
        f"{level_heading:<{LEVEL_WIDTH}}{state_heading:<{STATE_WIDTH}}"
        + "".join(f"{heading:>{SECONDS_WIDTH}}" for heading in total_headings)
    ]
    for name, frame in (
        (SESSION_LEVEL, table),
        (MACHINE_LEVEL, rollup.global_intervals(table)),
    ):
        wall = rollup.state_seconds(frame)
        expected = rollup.expected_seconds(frame)
        rows.extend(
            f"{name:<{LEVEL_WIDTH}}{state:<{STATE_WIDTH}}"
            + "".join(
                f"{human_seconds(total[state]):>{SECONDS_WIDTH}}"
                for total in (wall, expected)
            )
            for state in sorted(wall.index)
        )
    return rows


def _title(lane: str, window: tuple[pd.Timestamp, pd.Timestamp]) -> str:
    """The page's own title when the caller named none: what it shows, and when."""
    start, end = window
    return (
        f"{timeline.DEFAULT_TITLE} by {lane} — "
        f"{start:%d %b %H:%M} to {end:%d %b %H:%M} UTC"
    )


# --- the command line ----------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse argv into the window, the lane, and where the page goes."""
    parser = argparse.ArgumentParser(
        prog="measure-timeline",
        description="Draw the Claude Code hook-event store as a timeline.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("output", help="the HTML file to write")
    parser.add_argument(
        "--since",
        type=timestamp,
        metavar="WHEN",
        help="the window's start, UTC (default: the store's first event)",
    )
    parser.add_argument(
        "--until",
        type=timestamp,
        metavar="WHEN",
        help="the window's end, UTC (default: the store's last event)",
    )
    parser.add_argument(
        "--lane",
        choices=timeline.LANE_KEYS,
        default=timeline.SESSION_LANE,
        help="what each lane of the picture is (default: %(default)s)",
    )
    parser.add_argument(
        "--zone",
        default=timeline.DISPLAY_ZONE,
        help="the time zone the picture is drawn in (default: %(default)s)",
    )
    parser.add_argument(
        "--title",
        help="the page's title (default: names the lane key and the window)",
    )
    parser.add_argument(
        "--db",
        default=str(store.DEFAULT_STORE),
        metavar="PATH",
        help="the event store to read (default: %(default)s)",
    )
    return parser.parse_args(argv)
