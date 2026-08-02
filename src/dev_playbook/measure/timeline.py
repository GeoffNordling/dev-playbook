"""The timeline view: the interval table drawn against the clock.

One picture of the whole table — time left to right, one lane per session
stacked down the page, a bar wherever a row claims a span
([Measurement Prototype](/docs/measurement-prototype.md)). Nothing is drawn
between the bars, so a silent stretch reads as the silence it is rather than as
a lane that happens to be a paler shade of busy.

Three decisions carry most of what the picture says:

- **Confidence is thickness, and opacity too.** A `claude_active` row is an
  event pair and draws solid and full height; a graded row draws thinner and
  fainter the less the model backs it. Thickness is the one that matters. A bar
  is as wide as its span, so an overnight gap the model puts at 0.6 % is twenty
  times the width of a real turn and would otherwise dominate a picture it
  contributes eight minutes of expected time to. Grading the height puts visual
  weight back on `duration × confidence`, which is where the meaning is. Both
  have floors, because "we think nobody was here" and "nothing exists here" must
  not look the same.
- **Dormant rows are drawn but hidden.** A session is dormant for most of any
  wide window, so drawing dormancy by default paints the whole page and buries
  the activity. The trace is built and left switched off in the legend, one
  click from view.
- **Lanes are a parameter.** The same table pivots to a repo, an issue or a
  skill lane without a second derivation — the picture then answers "what was
  worked on" instead of "which terminal was busy".

The pivot needs a rule, because attribution belongs to an event row and a lane
belongs to an interval, and an interval spans many rows. The rule is what was
**in force at the interval's start**: the latest event of that session, at or
before the start, that named anything. A row naming several issues puts its
interval in every one of their lanes, so **lane totals do not add up to the
table's total** — the picture is for reading, and [`rollup`](rollup.py) is for
totalling. Bars sharing a lane overlay rather than stack, so a repo lane fed by
six sessions reads as the union of their activity, which is the question a repo
lane is asking.

**The clock is local, and says so.** The store is UTC throughout, which is right
for storage and wrong for a picture a human reads against their own day: a bar
at 02:00 means something different from one at 14:00, and only local time says
which. Timestamps are converted to the display zone for drawing, every tick
carries its day of the week, and the axis names the zone. Night is shaded behind
the bars, so a stretch of silence reads as "asleep" rather than as "idle".

The output is one self-contained HTML file: plotly.js is inlined rather than
fetched from a CDN, so the file opens from a laptop with no network and keeps
working when the CDN version moves on. It costs about four megabytes.
"""

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go

from dev_playbook.measure.attribute import ATTRIBUTION_COLUMNS
from dev_playbook.measure.intervals import CLAUDE_ACTIVE, DORMANT, INTERRUPTED
from dev_playbook.measure.presence import HUMAN_PRESENT, human_seconds

# The lane keys: the sessions themselves, or any column
# [`attribute`](attribute.py) adds to the events.
SESSION_LANE = "session"
LANE_KEYS = (SESSION_LANE, *ATTRIBUTION_COLUMNS)

# A row with no session belongs to the machine — that is what the global rollup
# produces — so under the session key it gets a lane of its own.
MACHINE_LANE = "machine"

# Where a session's time goes when nothing in it named the thing being pivoted
# to. Named rather than dropped: an hour nobody can attribute is a fact about
# the attribution, and a picture that quietly omits it overstates coverage.
UNATTRIBUTED_LANE = "(unattributed)"

# Drawing order, back to front, and therefore legend order. Also the set of
# states this view knows how to colour: anything else is refused rather than
# drawn in a default grey that would read as dormancy.
STATE_COLOURS = {
    DORMANT: (148, 163, 184),
    HUMAN_PRESENT: (22, 163, 74),
    INTERRUPTED: (217, 119, 6),
    CLAUDE_ACTIVE: (37, 99, 235),
}

# Switched off in the legend on load. Dormancy covers most of a wide window for
# most sessions, so it would otherwise paint over everything the view is for.
LEGEND_ONLY = (DORMANT,)

# The opacity a confidence of zero still draws at, so an all-but-certain absence
# stays distinguishable from a span the table makes no claim about at all.
MIN_OPACITY = 0.12

# The share of a lane's height a confidence of zero still draws at. A hairline
# rather than nothing, for the same reason the opacity has a floor — but thin
# enough that a 24-hour overnight guess cannot outweigh the turns beside it.
MIN_THICKNESS = 0.06

# The height a full-confidence bar draws at, in lane units. Below 1.0 so that
# neighbouring lanes keep a visible gutter between them.
FULL_THICKNESS = 0.72

# A date axis measures a bar's length in milliseconds.
MILLISECONDS = 1000

# The zone the picture is read in. The store is UTC; this is presentation only.
DISPLAY_ZONE = "America/New_York"

# Weekday, date, and time on every tick. A picture spanning days is read by
# which day as much as by which hour, and a bare "07-31 14:00" makes the reader
# work out the weekday themselves.
TICK_FORMAT = "%a %d %b<br>%H:%M"

# Night, in local hours: the band shaded behind the bars. Not a claim about
# sleep — a backdrop that lets a reader tell an overnight silence from a
# mid-afternoon one without reading the axis.
NIGHT_FROM = 22
NIGHT_TO = 6
NIGHT_COLOUR = "rgba(148, 163, 184, 0.13)"

# Layout, in pixels: the figure grows with the number of lanes so that ten lanes
# and a hundred are both readable, with room at the top for the title and legend.
LANE_HEIGHT = 26
CHROME_HEIGHT = 170
LEFT_MARGIN = 120
LANE_GAP = 0.35

GRID_COLOUR = "#e2e8f0"

DEFAULT_TITLE = "Claude Code activity"


class TimelineError(Exception):
    """A frame this module will not draw.

    Raised rather than worked around: every shape that reaches it would produce
    a picture that looks complete and is wrong — a lane silently missing its
    rows, or a state drawn in a colour that means something else.
    """


@dataclass(frozen=True)
class _History:
    """What one session attributed, and the moment each attribution took effect.

    Kept as two parallel lists in clock order so a lookup is a bisection: an
    interval table asks this question once per row, and a session can carry
    thousands of events.
    """

    at: list[pd.Timestamp]
    values: list[tuple[str, ...]]

    def in_force(self, moment: pd.Timestamp) -> tuple[str, ...]:
        """What this session was attributed to at `moment`, empty if never anything.

        A moment before the session's first attribution takes that first value.
        The fallback is deliberate: a dormant row starts at the edge of the
        window, before the session existed, and the alternative is every
        session's opening stretch landing in the unattributed lane.
        """
        if not self.values:
            return ()
        index = bisect_right(self.at, moment)
        return self.values[index - 1] if index else self.values[0]


def laned(
    frame: pd.DataFrame,
    key: str = SESSION_LANE,
    events: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """`frame` with a `lane` column — one row per lane each interval belongs to.

    `events` is the attributed event frame, and is required for every key but
    `session`, which needs nothing beyond the interval rows themselves. An
    interval naming two issues comes back twice, once in each lane, so the
    result is a view rather than a table to total.
    """
    if key not in LANE_KEYS:
        raise TimelineError(
            f"{key!r} is not a lane key; expected one of {', '.join(LANE_KEYS)}"
        )
    if key == SESSION_LANE:
        return frame.assign(
            lane=frame["session_id"].where(frame["session_id"].notna(), MACHINE_LANE)
        ).reset_index(drop=True)
    if events is None:
        raise TimelineError(
            f"a {key!r} lane needs the attributed events to read it from"
        )
    if frame["session_id"].isna().any():
        raise TimelineError(
            f"rows belonging to the machine rather than a session cannot be "
            f"pivoted to {key!r}: attribution is per session"
        )

    histories = _histories(events, key)
    positions: list[int] = []
    lanes: list[str] = []
    for position, row in enumerate(frame.itertuples()):
        history = histories.get(row.session_id)
        if history is None:
            raise TimelineError(
                f"session {row.session_id} has intervals but no events to attribute them"
            )
        for value in history.in_force(row.start) or (UNATTRIBUTED_LANE,):
            positions.append(position)
            lanes.append(value)
    return frame.iloc[positions].assign(lane=lanes).reset_index(drop=True)


def timeline_figure(
    frame: pd.DataFrame, title: str = DEFAULT_TITLE, zone: str = DISPLAY_ZONE
) -> go.Figure:
    """The laned interval table as a figure: one bar per row, one row of bars per lane.

    Lanes run down the page in the order they first show activity, which puts
    the window's opening lane at the top and reads as the session list growing.

    Drawn against `zone`'s wall clock, not UTC. The conversion happens here and
    nowhere else: the table stays UTC, and only the picture is local.
    """
    if "lane" not in frame.columns:
        raise TimelineError("frame carries no lane column; pass it through laned first")
    unknown = sorted(set(frame["state"]) - set(STATE_COLOURS))
    if unknown:
        raise TimelineError(f"no colour is defined for state {', '.join(unknown)}")

    local = _localised(frame, zone)
    order = _lane_order(local)
    figure = go.Figure(
        [
            _state_bars(state, local[local["state"] == state])
            for state in STATE_COLOURS
            if (local["state"] == state).any()
        ]
    )
    for start, end in _night_bands(local):
        figure.add_vrect(
            x0=start, x1=end, fillcolor=NIGHT_COLOUR, line_width=0, layer="below"
        )
    figure.update_layout(
        title=title,
        barmode="overlay",
        bargap=LANE_GAP,
        height=CHROME_HEIGHT + LANE_HEIGHT * len(order),
        hovermode="closest",
        legend={"orientation": "h", "y": 1.03, "yanchor": "bottom"},
        margin={"l": LEFT_MARGIN, "r": 30, "t": 80, "b": 60},
        plot_bgcolor="white",
        xaxis={
            "type": "date",
            "gridcolor": GRID_COLOUR,
            "showgrid": True,
            "tickformat": TICK_FORMAT,
            "title": {"text": _zone_label(local, zone)},
        },
        yaxis={
            "type": "category",
            "categoryorder": "array",
            "categoryarray": order,
            "autorange": "reversed",
            "showgrid": False,
            # A session lane is labelled with a whole UUID, so the margin below
            # is a floor rather than a width: plotly widens it to whatever the
            # longest label needs.
            "automargin": True,
        },
    )
    return figure


def write_timeline(
    frame: pd.DataFrame,
    path: Path,
    title: str = DEFAULT_TITLE,
    zone: str = DISPLAY_ZONE,
) -> Path:
    """The laned table written to `path` as one self-contained HTML file.

    plotly.js is inlined, so the file is about four megabytes and needs no
    network to open. Returns the path, for a caller that wants to report it.
    """
    path.write_text(
        timeline_figure(frame, title, zone).to_html(include_plotlyjs="inline"),
        encoding="utf-8",
    )
    return path


# --- the local clock ----------------------------------------------------------


def _localised(frame: pd.DataFrame, zone: str) -> pd.DataFrame:
    """`frame` with its bounds moved to `zone`'s wall clock and the offset dropped.

    Dropped rather than carried: plotly renders a tz-aware timestamp by its UTC
    instant, so the only way to draw a local clock is to hand it the local
    reading as if it were naive. Everything downstream of here is presentation.
    """
    try:
        ZoneInfo(zone)
    except Exception as error:
        raise TimelineError(f"{zone!r} is not a time zone: {error}") from error
    moved = frame.copy()
    for column in ("start", "end"):
        moved[column] = frame[column].dt.tz_convert(zone).dt.tz_localize(None)
    return moved


def _zone_label(local: pd.DataFrame, zone: str) -> str:
    """The axis title: the zone, and the abbreviation in force over the window.

    Taken from the window's own first instant rather than from now, so a picture
    of a week in January says EST when it is read in July.
    """
    moment = local["start"].min()
    if pd.isna(moment):
        return zone
    abbreviation = moment.tz_localize(zone).strftime("%Z")
    return f"{zone} ({abbreviation})" if abbreviation else zone


def _night_bands(local: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Every night the window touches, as local-clock spans to shade.

    Emitted one calendar day at a time and clipped to the window, so a window
    opening mid-evening gets the remainder of that night and no more.
    """
    first, last = local["start"].min(), local["end"].max()
    if pd.isna(first) or pd.isna(last):
        return []
    bands = []
    day = first.normalize() - pd.Timedelta(days=1)
    while day <= last.normalize():
        start = day + pd.Timedelta(hours=NIGHT_FROM)
        end = day + pd.Timedelta(days=1, hours=NIGHT_TO)
        if end > first and start < last:
            bands.append((max(start, first), min(end, last)))
        day += pd.Timedelta(days=1)
    return bands


# --- what each session was working on, moment by moment -----------------------


def _histories(events: pd.DataFrame, column: str) -> dict[str, _History]:
    """Each session's attributions in the order they took effect.

    Ordered by `received_at` rather than by `id`, because the question a lookup
    asks is about a moment on the clock: the two orders differ where hooks
    arrived out of order, and a bisection over an unsorted list answers wrongly
    without saying so.
    """
    if column not in events.columns:
        raise TimelineError(
            f"events carry no {column!r} column; run attribute.attributed over them first"
        )
    histories = {}
    for session, rows in events.sort_values(["received_at", "id"]).groupby(
        "session_id"
    ):
        at: list[pd.Timestamp] = []
        values: list[tuple[str, ...]] = []
        for moment, cell in zip(rows["received_at"], rows[column], strict=True):
            named = _named(cell)
            if named:
                at.append(moment)
                values.append(named)
        histories[session] = _History(at, values)
    return histories


def _named(cell: object) -> tuple[str, ...]:
    """What one event row names in a lane column: nothing, one thing, or several.

    The two issue columns hold tuples, because a command line can name several
    issues; `repo` and `skill` hold a name or NA. Both shapes answer as a tuple,
    so the lookup above has one thing to carry.
    """
    if isinstance(cell, tuple):
        return cell
    if pd.isna(cell):
        return ()
    if not isinstance(cell, str):
        raise TimelineError(
            f"a lane value is a name or a tuple of names, not a {type(cell).__name__}"
        )
    return (cell,)


# --- drawing ------------------------------------------------------------------


def _lane_order(frame: pd.DataFrame) -> list[str]:
    """The lanes, earliest first, which is the order they run down the page."""
    return list(frame.groupby("lane")["start"].min().sort_values(kind="stable").index)


def _state_bars(state: str, rows: pd.DataFrame) -> go.Bar:
    """One trace: every interval of `state`, each drawn across the span it claims."""
    seconds = (rows["end"] - rows["start"]).dt.total_seconds()
    return go.Bar(
        name=state,
        base=rows["start"],
        x=seconds * MILLISECONDS,
        y=rows["lane"],
        width=[_thickness(value) for value in rows["confidence"]],
        orientation="h",
        marker={
            "color": [_shade(state, value) for value in rows["confidence"]],
            "line": {"width": 0},
        },
        hovertext=_hover_text(rows),
        hovertemplate="%{hovertext}<extra></extra>",
        visible="legendonly" if state in LEGEND_ONLY else True,
    )


def _shade(state: str, confidence: float) -> str:
    """The state's colour, faded to how strongly the table backs the row."""
    red, green, blue = STATE_COLOURS[state]
    opacity = MIN_OPACITY + (1 - MIN_OPACITY) * confidence
    return f"rgba({red}, {green}, {blue}, {opacity:.3f})"


def _thickness(confidence: float) -> float:
    """How much of its lane a bar fills, in lane units.

    The correction that keeps a long guess from reading as a long fact. Width is
    already spoken for — it is the span — so height is the only channel left to
    carry how much the row is worth, and a reader's eye multiplies the two.
    """
    return FULL_THICKNESS * (MIN_THICKNESS + (1 - MIN_THICKNESS) * confidence)


def _hover_text(rows: pd.DataFrame) -> list[str]:
    """One label per row: what it claims, where, when, for how long, how strongly."""
    return [
        f"<b>{row.state}</b> — {row.lane}<br>"
        f"{row.start:%a %d %b %H:%M:%S} → {row.end:%a %d %b %H:%M:%S}<br>"
        f"{human_seconds((row.end - row.start).total_seconds())} "
        f"at {row.confidence:.0%} confidence"
        for row in rows.itertuples()
    ]
