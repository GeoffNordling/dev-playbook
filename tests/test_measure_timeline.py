"""Behavioral tests for the timeline view of the interval table.

Interval rows are written out here, as in the rollup's suite: what this one is
about is which lane a row lands in and how it is drawn, not how the row was
derived. Event rows go through the real attribution, so the lane lookup meets
the column shapes it will meet in a run — a name, an NA, or a tuple of issue
references.

The figure is checked through what a reader would see: which traces exist, how
faint each bar is, where the lanes sit, and whether the page carries plotly or
merely links to it.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest
from measure_fakes import a_payload, a_timed_frame, at

from dev_playbook.measure import attribute, intervals, timeline

WORKSPACE = Path("/home/geoff/workspace")
CHECKOUT = "/home/geoff/workspace/dev-playbook"
OTHER_CHECKOUT = "/home/geoff/workspace/media-tools"


def an_interval(
    start: float,
    end: float,
    state: str = "claude_active",
    session: str | None = "one",
    confidence: float = 1.0,
) -> dict:
    """One interval row, in the shape the derivation stages emit."""
    return {
        "start": at(start),
        "end": at(end),
        "state": state,
        "session_id": session,
        "confidence": confidence,
    }


def a_table(*rows: dict) -> pd.DataFrame:
    """An interval table over the rows given."""
    return intervals.interval_frame(rows)


def attributed(*timed: tuple[float, dict]) -> pd.DataFrame:
    """Event rows carrying the four attribution columns, at the seconds given."""
    return attribute.attributed(a_timed_frame(list(timed)), workspace=WORKSPACE)


def a_bash_row(command: str, session: str = "one", cwd: str = CHECKOUT) -> dict:
    """A `PostToolUse` payload for one Bash command line, as the store keeps it."""
    return a_payload(
        "PostToolUse",
        session=session,
        tool_name="Bash",
        tool_input={"command": command},
        cwd=cwd,
    )


def alpha_of(colour: str) -> float:
    """The opacity of an `rgba(...)` string, which is how confidence is drawn."""
    return float(colour.rsplit(",", 1)[1].strip(" )"))


def trace_named(figure: go.Figure, state: str) -> go.Bar:
    """The one trace drawing `state`."""
    return next(trace for trace in figure.data if trace.name == state)


# --- which lane an interval belongs to ----------------------------------------


def test_each_session_gets_a_lane_of_its_own() -> None:
    table = a_table(an_interval(1, 2, session="one"), an_interval(3, 4, session="two"))

    laned = timeline.laned(table)

    assert list(laned["lane"]) == ["one", "two"]


def test_a_row_belonging_to_no_session_lands_in_the_machine_lane() -> None:
    table = a_table(an_interval(1, 2, session=None))

    laned = timeline.laned(table)

    assert list(laned["lane"]) == [timeline.MACHINE_LANE]


def test_an_interval_takes_the_repo_the_session_was_in_when_it_started() -> None:
    events = attributed(
        (1, a_payload("UserPromptSubmit", session="one", prompt_id="p1", cwd=CHECKOUT)),
        (10, a_payload("Stop", session="one", prompt_id="p1", cwd=OTHER_CHECKOUT)),
    )
    table = a_table(an_interval(2, 3), an_interval(11, 12))

    laned = timeline.laned(table, "repo", events)

    assert list(laned["lane"]) == ["dev-playbook", "media-tools"]


def test_an_interval_starting_before_the_session_did_takes_its_first_attribution() -> (
    None
):
    events = attributed(
        (10, a_payload("UserPromptSubmit", session="one", prompt_id="p1"))
    )
    table = a_table(an_interval(0, 10, state="dormant"))

    laned = timeline.laned(table, "repo", events)

    assert list(laned["lane"]) == ["dev-playbook"]


def test_an_interval_appears_in_every_issue_its_session_named() -> None:
    events = attributed(
        (1, a_bash_row("gh issue view 271 && gh issue view 272")),
    )
    table = a_table(an_interval(2, 3))

    laned = timeline.laned(table, "issue_reads", events)

    assert list(laned["lane"]) == ["dev-playbook#271", "dev-playbook#272"]
    assert list(laned["start"]) == [at(2), at(2)]


def test_reads_and_writes_stay_in_lanes_of_their_own() -> None:
    events = attributed(
        (1, a_bash_row("gh issue view 271")),
        (2, a_bash_row("gh issue comment 272 --body done")),
    )
    table = a_table(an_interval(3, 4))

    reads = timeline.laned(table, "issue_reads", events)
    writes = timeline.laned(table, "issue_writes", events)

    assert list(reads["lane"]) == ["dev-playbook#271"]
    assert list(writes["lane"]) == ["dev-playbook#272"]


def test_a_skill_lane_follows_the_skill_in_force_at_the_start() -> None:
    events = attributed(
        (1, a_payload("UserPromptSubmit", session="one", command_name="build")),
        (10, a_payload("UserPromptSubmit", session="one", command_name="commit")),
    )
    table = a_table(an_interval(2, 3), an_interval(11, 12))

    laned = timeline.laned(table, "skill", events)

    assert list(laned["lane"]) == ["build", "commit"]


def test_a_session_that_named_nothing_lands_in_the_unattributed_lane() -> None:
    events = attributed((1, a_payload("UserPromptSubmit", session="one")))
    table = a_table(an_interval(2, 3))

    laned = timeline.laned(table, "skill", events)

    assert list(laned["lane"]) == [timeline.UNATTRIBUTED_LANE]


def test_a_lane_key_that_names_no_column_is_refused() -> None:
    with pytest.raises(timeline.TimelineError, match="not a lane key"):
        timeline.laned(a_table(an_interval(1, 2)), "hostname")


def test_an_attributed_lane_without_events_to_read_is_refused() -> None:
    with pytest.raises(timeline.TimelineError, match="needs the attributed events"):
        timeline.laned(a_table(an_interval(1, 2)), "repo")


def test_events_that_were_never_attributed_are_refused() -> None:
    events = a_timed_frame([(1, a_payload("UserPromptSubmit", session="one"))])

    with pytest.raises(timeline.TimelineError, match="no 'repo' column"):
        timeline.laned(a_table(an_interval(1, 2)), "repo", events)


def test_a_machine_row_cannot_be_pivoted_to_a_repo() -> None:
    events = attributed((1, a_payload("UserPromptSubmit", session="one")))
    table = a_table(an_interval(1, 2, session=None))

    with pytest.raises(timeline.TimelineError, match="attribution is per session"):
        timeline.laned(table, "repo", events)


def test_an_interval_whose_session_has_no_events_is_refused() -> None:
    events = attributed((1, a_payload("UserPromptSubmit", session="one")))
    table = a_table(an_interval(1, 2, session="two"))

    with pytest.raises(timeline.TimelineError, match="session two has intervals"):
        timeline.laned(table, "repo", events)


# --- how the table is drawn ---------------------------------------------------


def test_each_state_in_the_table_is_drawn_as_its_own_trace() -> None:
    table = a_table(
        an_interval(1, 2),
        an_interval(2, 3, state="interrupted"),
        an_interval(3, 9, state="human_present", confidence=0.4),
    )

    figure = timeline.timeline_figure(timeline.laned(table))

    assert {trace.name for trace in figure.data} == {
        "claude_active",
        "interrupted",
        "human_present",
    }


def test_a_bar_is_drawn_only_where_an_interval_claims_a_span() -> None:
    table = a_table(an_interval(1, 3), an_interval(20, 21))

    figure = timeline.timeline_figure(timeline.laned(table))
    bars = trace_named(figure, "claude_active")

    assert list(pd.to_datetime(bars.base, utc=True)) == [at(1), at(20)]
    assert list(bars.x) == [2000.0, 1000.0]


def test_an_inferred_row_is_drawn_fainter_than_an_observed_one() -> None:
    table = a_table(
        an_interval(1, 2),
        an_interval(2, 9, state="human_present", confidence=0.3),
    )

    figure = timeline.timeline_figure(timeline.laned(table))
    observed = alpha_of(trace_named(figure, "claude_active").marker.color[0])
    inferred = alpha_of(trace_named(figure, "human_present").marker.color[0])

    assert observed == 1.0
    assert inferred < observed


def test_a_row_the_model_all_but_rules_out_is_still_visible() -> None:
    table = a_table(an_interval(1, 9, state="human_present", confidence=0.0))

    figure = timeline.timeline_figure(timeline.laned(table))

    assert alpha_of(trace_named(figure, "human_present").marker.color[0]) > 0


def test_dormancy_is_drawn_but_switched_off_on_load() -> None:
    table = a_table(an_interval(1, 2), an_interval(2, 30, state="dormant"))

    figure = timeline.timeline_figure(timeline.laned(table))

    assert trace_named(figure, "dormant").visible == "legendonly"
    assert trace_named(figure, "claude_active").visible is True


def test_lanes_run_down_the_page_in_the_order_they_first_show_activity() -> None:
    table = a_table(
        an_interval(9, 10, session="late"), an_interval(1, 2, session="early")
    )

    figure = timeline.timeline_figure(timeline.laned(table))

    assert figure.layout.yaxis.categoryarray == ("early", "late")


def test_a_bar_says_what_it_claims_and_how_strongly() -> None:
    table = a_table(an_interval(1, 70, state="human_present", confidence=0.31))

    figure = timeline.timeline_figure(timeline.laned(table))
    hover = trace_named(figure, "human_present").hovertext[0]

    assert "human_present" in hover
    assert "1m 9s" in hover
    assert "31%" in hover


def test_a_state_with_no_colour_of_its_own_is_refused() -> None:
    table = a_table(an_interval(1, 2, state="teleported"))

    with pytest.raises(timeline.TimelineError, match="no colour is defined"):
        timeline.timeline_figure(timeline.laned(table))


def test_a_table_that_was_never_laned_is_refused() -> None:
    with pytest.raises(timeline.TimelineError, match="no lane column"):
        timeline.timeline_figure(a_table(an_interval(1, 2)))


# --- the page it writes -------------------------------------------------------


def test_the_written_page_carries_plotly_rather_than_linking_to_it(
    tmp_path: Path,
) -> None:
    table = a_table(an_interval(1, 2))

    written = timeline.write_timeline(timeline.laned(table), tmp_path / "view.html")
    page = written.read_text(encoding="utf-8")

    assert "<script src=" not in page
    assert "Plotly.newPlot" in page


def test_the_written_page_carries_the_title_it_was_given(tmp_path: Path) -> None:
    table = a_table(an_interval(1, 2))

    timeline.write_timeline(timeline.laned(table), tmp_path / "view.html", "a Tuesday")

    assert "a Tuesday" in (tmp_path / "view.html").read_text(encoding="utf-8")
