"""Behavioral tests for the definitive rows of the interval table.

Every expected bound is written as `at(N)` — the second the Nth payload of the
frame lands on — so the assertion names a clock time rather than recomputing
the derivation under test.
"""

import pandas as pd
import pytest
from measure_fakes import a_frame, a_payload, at

from dev_playbook.measure import intervals


def a_turn(prompt: str, session: str = "5b1f") -> list[dict]:
    """A submit and the `Stop` that closes it, as consecutive payloads."""
    return [
        a_payload("UserPromptSubmit", session=session, prompt_id=prompt, prompt="go"),
        a_payload(
            "Stop", session=session, prompt_id=prompt, last_assistant_message="k"
        ),
    ]


# --- turns that ended in a Stop ----------------------------------------------


def test_a_submit_and_its_stop_become_one_claude_active_row() -> None:
    events = a_frame(a_turn("p-1"))

    frame = intervals.turn_intervals(events).frame

    assert len(frame) == 1
    assert frame.iloc[0]["state"] == "claude_active"
    assert frame.iloc[0]["start"] == at(1)
    assert frame.iloc[0]["end"] == at(2)


def test_a_claude_active_row_carries_its_session_and_full_confidence() -> None:
    events = a_frame(a_turn("p-1", session="abc"))

    row = intervals.turn_intervals(events).frame.iloc[0]

    assert row["session_id"] == "abc"
    assert row["confidence"] == 1.0


def test_a_turn_is_closed_by_the_stop_sharing_its_prompt_id_not_the_next_one() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
            a_payload("Stop", prompt_id="p-0", last_assistant_message="earlier turn"),
            a_payload("Stop", prompt_id="p-1", last_assistant_message="k"),
        ]
    )

    frame = intervals.turn_intervals(events).frame

    assert list(frame["end"]) == [at(3)]


def test_a_stop_matching_no_submit_produces_no_row() -> None:
    events = a_frame(
        [a_payload("Stop", prompt_id="p-9", last_assistant_message="orphan")]
    )

    result = intervals.turn_intervals(events)

    assert len(result.frame) == 0
    assert result.unresolved == 0


# --- turns an interrupt ended ------------------------------------------------


def test_a_submit_with_no_stop_ends_at_the_next_submit_in_its_session() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
            a_payload("UserPromptSubmit", prompt_id="p-2", prompt="no, stop"),
            a_payload("Stop", prompt_id="p-2", last_assistant_message="k"),
        ]
    )

    row = intervals.turn_intervals(events).frame.iloc[0]

    assert row["state"] == "interrupted"
    assert row["start"] == at(1)
    assert row["end"] == at(2)


def test_an_interrupted_turn_carries_full_confidence() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
            a_payload("UserPromptSubmit", prompt_id="p-2", prompt="no, stop"),
        ]
    )

    assert intervals.turn_intervals(events).frame.iloc[0]["confidence"] == 1.0


def test_a_submit_is_not_closed_by_a_submit_in_another_session() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", session="one", prompt_id="p-1", prompt="go"),
            a_payload("UserPromptSubmit", session="two", prompt_id="p-2", prompt="hi"),
            a_payload(
                "Stop", session="two", prompt_id="p-2", last_assistant_message="k"
            ),
        ]
    )

    result = intervals.turn_intervals(events)

    assert list(result.frame["session_id"]) == ["two"]
    assert result.unresolved == 1


def test_a_submit_with_no_stop_and_nothing_after_it_is_counted_unresolved() -> None:
    events = a_frame([a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go")])

    result = intervals.turn_intervals(events)

    assert len(result.frame) == 0
    assert result.unresolved == 1


# --- frames that will not derive ---------------------------------------------


def test_two_stops_for_one_prompt_id_are_refused() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
            a_payload("Stop", prompt_id="p-1", last_assistant_message="k"),
            a_payload("Stop", prompt_id="p-1", last_assistant_message="k again"),
        ]
    )

    with pytest.raises(intervals.IntervalError, match="p-1"):
        intervals.turn_intervals(events)


def test_a_stop_arriving_before_its_submit_is_refused() -> None:
    events = a_frame(
        [
            a_payload("Stop", prompt_id="p-1", last_assistant_message="k"),
            a_payload("UserPromptSubmit", prompt_id="p-1", prompt="go"),
        ]
    )

    with pytest.raises(intervals.IntervalError, match="end before they start"):
        intervals.turn_intervals(events)


def test_an_event_outside_the_given_window_is_refused() -> None:
    events = a_frame(a_turn("p-1"))

    with pytest.raises(intervals.IntervalError, match="outside"):
        intervals.dormant_intervals(events, (at(0), at(1)))


# --- the spans a session did not exist for ------------------------------------


def test_a_session_starting_after_the_window_is_dormant_until_its_first_event() -> None:
    events = a_frame(a_turn("p-1"))

    frame = intervals.dormant_intervals(events, (at(0), at(2)))

    assert len(frame) == 1
    assert frame.iloc[0]["state"] == "dormant"
    assert frame.iloc[0]["start"] == at(0)
    assert frame.iloc[0]["end"] == at(1)


def test_a_session_ending_before_the_window_is_dormant_from_its_last_event() -> None:
    events = a_frame(a_turn("p-1"))

    frame = intervals.dormant_intervals(events, (at(1), at(9)))

    assert list(frame["start"]) == [at(2)]
    assert list(frame["end"]) == [at(9)]


def test_a_session_spanning_the_whole_window_is_never_dormant() -> None:
    events = a_frame(a_turn("p-1"))

    frame = intervals.dormant_intervals(events, (at(1), at(2)))

    assert len(frame) == 0


def test_each_session_gets_its_own_dormant_spans() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", session="one", prompt_id="p-1", prompt="go"),
            a_payload("UserPromptSubmit", session="two", prompt_id="p-2", prompt="hi"),
        ]
    )

    frame = intervals.dormant_intervals(events, (at(1), at(2)))

    assert list(frame["session_id"]) == ["one", "two"]
    assert list(frame["start"]) == [at(1), at(1)]
    assert list(frame["end"]) == [at(2), at(2)]


# --- the whole definitive table ----------------------------------------------


def test_the_table_carries_the_interval_schema() -> None:
    table = intervals.definitive_intervals(a_frame(a_turn("p-1")))

    assert list(table.frame.columns) == [
        "start",
        "end",
        "state",
        "session_id",
        "confidence",
    ]


def test_an_empty_window_derives_an_empty_table() -> None:
    table = intervals.definitive_intervals(a_frame([]))

    assert len(table.frame) == 0
    assert table.unresolved == 0
    assert list(table.frame.columns) == list(intervals.INTERVAL_COLUMNS)


def test_the_frames_own_span_is_the_window_when_none_is_chosen() -> None:
    events = a_frame(
        [
            a_payload("UserPromptSubmit", session="one", prompt_id="p-1", prompt="go"),
            a_payload("UserPromptSubmit", session="two", prompt_id="p-2", prompt="hi"),
            a_payload(
                "Stop", session="two", prompt_id="p-2", last_assistant_message="k"
            ),
            a_payload(
                "Stop", session="one", prompt_id="p-1", last_assistant_message="k"
            ),
        ]
    )

    frame = intervals.definitive_intervals(events).frame
    dormant = frame[frame["state"] == "dormant"]

    assert list(dormant["session_id"]) == ["two", "two"]
    assert list(dormant["start"]) == [at(1), at(3)]
    assert list(dormant["end"]) == [at(2), at(4)]


def test_a_chosen_window_widens_the_dormant_spans() -> None:
    events = a_frame(a_turn("p-1"))

    frame = intervals.definitive_intervals(events, (at(0), at(9))).frame

    assert list(frame["state"]) == ["dormant", "claude_active", "dormant"]
    assert list(frame["start"]) == [at(0), at(1), at(2)]


def test_the_table_is_ordered_oldest_first() -> None:
    events = a_frame([*a_turn("p-1", session="one"), *a_turn("p-2", session="two")])

    frame = intervals.definitive_intervals(events).frame

    assert list(frame["start"]) == sorted(frame["start"])


def test_unresolved_turns_are_reported_through_the_whole_table() -> None:
    events = a_frame(
        [
            *a_turn("p-1"),
            a_payload("UserPromptSubmit", prompt_id="p-2", prompt="still going"),
        ]
    )

    table = intervals.definitive_intervals(events)

    assert table.unresolved == 1
    assert list(table.frame["state"]) == ["claude_active"]


def test_interval_frame_types_its_bounds_even_with_no_rows() -> None:
    frame = intervals.interval_frame([])

    assert frame["start"].dtype == pd.DatetimeTZDtype("us", "UTC")
    assert frame["confidence"].dtype == "float64"
