"""Behavioral tests for the global level of the interval table.

Interval rows are written out here rather than derived from events: the
derivations have their own suites, and what this one is about is how rows of
several sessions combine into rows of the machine. Bounds are `at(N)` seconds,
so every expectation names a clock time.
"""

import pandas as pd
import pytest
from measure_fakes import a_frame, a_payload, at

from dev_playbook.measure import intervals, rollup


def an_interval(
    start: float,
    end: float,
    state: str = "claude_active",
    session: str = "one",
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


def a_turn(prompt: str, session: str) -> list[dict]:
    """A submit and the `Stop` that closes it, as consecutive payloads."""
    return [
        a_payload("UserPromptSubmit", session=session, prompt_id=prompt, prompt="go"),
        a_payload(
            "Stop", session=session, prompt_id=prompt, last_assistant_message="k"
        ),
    ]


# --- a moment any session claims ----------------------------------------------


def test_two_sessions_working_over_the_same_stretch_become_one_span() -> None:
    table = intervals.interval_frame(
        [an_interval(1, 5, session="one"), an_interval(3, 8, session="two")]
    )

    frame = rollup.union_intervals(table, "claude_active")

    assert len(frame) == 1
    assert frame.iloc[0]["start"] == at(1)
    assert frame.iloc[0]["end"] == at(8)


def test_sessions_that_never_overlap_stay_separate_spans() -> None:
    table = intervals.interval_frame(
        [an_interval(1, 2, session="one"), an_interval(5, 6, session="two")]
    )

    frame = rollup.union_intervals(table, "claude_active")

    assert list(frame["start"]) == [at(1), at(5)]
    assert list(frame["end"]) == [at(2), at(6)]


def test_spans_that_touch_end_to_end_read_as_one_stretch() -> None:
    table = intervals.interval_frame(
        [an_interval(1, 3, session="one"), an_interval(3, 5, session="two")]
    )

    frame = rollup.union_intervals(table, "claude_active")

    assert list(frame["start"]) == [at(1)]
    assert list(frame["end"]) == [at(5)]


def test_a_global_row_names_the_state_it_was_asked_for_and_no_session() -> None:
    table = intervals.interval_frame([an_interval(1, 2)])

    row = rollup.union_intervals(table, "human_present").iloc[0]

    assert row["state"] == "human_present"
    assert pd.isna(row["session_id"])


def test_a_zero_length_row_covers_no_moment() -> None:
    table = intervals.interval_frame([an_interval(4, 4)])

    assert len(rollup.union_intervals(table, "claude_active")) == 0


# --- graded rows combining ----------------------------------------------------


def test_where_two_half_beliefs_overlap_the_machine_believes_more() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 3, "human_present", session="one", confidence=0.5),
            an_interval(2, 4, "human_present", session="two", confidence=0.5),
        ]
    )

    frame = rollup.union_intervals(table, "human_present")

    assert list(frame["start"]) == [at(1), at(2), at(3)]
    assert list(frame["confidence"]) == [0.5, 0.75, 0.5]


def test_a_moment_one_session_is_certain_of_stays_certain() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 4, "human_present", session="one", confidence=1.0),
            an_interval(2, 3, "human_present", session="two", confidence=0.5),
        ]
    )

    frame = rollup.union_intervals(table, "human_present")

    assert list(frame["confidence"]) == [1.0]
    assert list(frame["end"]) == [at(4)]


def test_one_session_claiming_a_moment_twice_is_refused() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 5, "human_present", session="one", confidence=0.5),
            an_interval(3, 7, "human_present", session="one", confidence=0.5),
        ]
    )

    with pytest.raises(rollup.RollupError, match="one"):
        rollup.union_intervals(table, "human_present")


# --- a moment every session claims ---------------------------------------------


def test_the_machine_is_dormant_only_where_every_session_is() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 4, "dormant", session="one"),
            an_interval(3, 6, "dormant", session="two"),
        ]
    )

    frame = rollup.global_intervals(table)

    assert list(frame["state"]) == ["dormant"]
    assert list(frame["start"]) == [at(3)]
    assert list(frame["end"]) == [at(4)]


def test_a_session_that_ran_the_whole_window_keeps_the_machine_awake() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 4, "dormant", session="one"),
            an_interval(3, 6, "dormant", session="two"),
            an_interval(1, 9, "claude_active", session="three"),
        ]
    )

    frame = rollup.global_intervals(table)

    assert list(frame["state"]) == ["claude_active"]


# --- the whole table rolled up -------------------------------------------------


def test_every_state_in_the_table_comes_back_rolled_up() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 3, "claude_active", session="one"),
            an_interval(3, 6, "human_present", session="one", confidence=0.4),
            an_interval(2, 5, "interrupted", session="two"),
        ]
    )

    frame = rollup.global_intervals(table)

    assert sorted(set(frame["state"])) == [
        "claude_active",
        "human_present",
        "interrupted",
    ]
    assert frame["session_id"].isna().all()


def test_the_global_table_is_ordered_oldest_first() -> None:
    table = intervals.interval_frame(
        [
            an_interval(5, 6, "human_present", session="two", confidence=0.2),
            an_interval(1, 2, "claude_active", session="one"),
        ]
    )

    frame = rollup.global_intervals(table)

    assert list(frame["start"]) == [at(1), at(5)]


def test_an_empty_table_rolls_up_to_an_empty_table() -> None:
    frame = rollup.global_intervals(intervals.interval_frame([]))

    assert len(frame) == 0
    assert list(frame.columns) == list(intervals.INTERVAL_COLUMNS)


# --- what the two levels total to ----------------------------------------------


def test_state_seconds_sums_the_wall_clock_of_each_state() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 3, "claude_active", session="one"),
            an_interval(4, 9, "claude_active", session="two"),
            an_interval(3, 4, "human_present", session="one", confidence=0.5),
        ]
    )

    totals = rollup.state_seconds(table)

    assert totals["claude_active"] == 7.0
    assert totals["human_present"] == 1.0


def test_expected_seconds_weights_a_graded_row_by_its_confidence() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 3, "claude_active", session="one"),
            an_interval(3, 7, "human_present", session="one", confidence=0.25),
        ]
    )

    totals = rollup.expected_seconds(table)

    assert totals["claude_active"] == 2.0
    assert totals["human_present"] == 1.0


def test_both_levels_agree_on_claude_active_time_when_sessions_do_not_overlap() -> None:
    events = a_frame([*a_turn("p-1", session="one"), *a_turn("p-2", session="two")])
    table = intervals.definitive_intervals(events).frame

    session_level = rollup.state_seconds(table)
    global_level = rollup.state_seconds(rollup.global_intervals(table))

    assert session_level["claude_active"] == global_level["claude_active"]


def test_the_machines_active_time_is_the_clock_and_not_the_sum() -> None:
    table = intervals.interval_frame(
        [
            an_interval(1, 5, "claude_active", session="one"),
            an_interval(3, 7, "claude_active", session="two"),
        ]
    )

    assert rollup.state_seconds(table)["claude_active"] == 8.0
    assert rollup.state_seconds(rollup.global_intervals(table))["claude_active"] == 6.0
