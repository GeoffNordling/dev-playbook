"""Behavioral tests for the gaps between turns and the presence fitted over them.

Gap lengths are chosen, not derived: a frame is built through `a_timed_frame`
with each event placed at a named second, so an expected duration is arithmetic
a reader can do in their head rather than a restatement of the extraction.

The mixture is exercised on samples with a working mode of about a minute and an
away mode of hours, the shape the real store shows. What is asserted about it is
what a presence probability has to do — fall as the gap lengthens, sit near one
for a short gap and near zero for an overnight one — never the parameters EM
happens to land on.
"""

import pandas as pd
import pytest
from measure_fakes import a_payload, a_timed_frame, at

from dev_playbook.measure import intervals, presence

# A working mode around a minute and an away mode of hours, the two the store
# shows, with enough of each to clear the fitter's floor.
BIMODAL_GAPS = [55.0, 62.0, 70.0, 78.0, 95.0, 4800.0, 7200.0, 9000.0, 12000.0, 16000.0]


def a_turn(
    second: float, prompt: str, session: str = "5b1f"
) -> list[tuple[float, dict]]:
    """A submit at `second` and the `Stop` that closes it one second later."""
    return [
        (
            second,
            a_payload(
                "UserPromptSubmit", session=session, prompt_id=prompt, prompt="go"
            ),
        ),
        (
            second + 1,
            a_payload(
                "Stop", session=session, prompt_id=prompt, last_assistant_message="k"
            ),
        ),
    ]


def turns_gapped_by(gaps: list[float], session: str = "5b1f") -> pd.DataFrame:
    """A session of one-second turns separated by `gaps`, in seconds."""
    timed: list[tuple[float, dict]] = []
    second = 1.0
    for index, gap in enumerate([0.0, *gaps]):
        second += gap
        timed.extend(a_turn(second, f"p-{index}", session=session))
        second += 1
    return a_timed_frame(timed)


# --- finding the gaps ---------------------------------------------------------


def test_a_stop_and_the_next_submit_bound_one_gap() -> None:
    events = a_timed_frame([*a_turn(1, "p-1"), *a_turn(300, "p-2")])

    gaps = presence.stop_gaps(events)

    assert len(gaps) == 1
    assert gaps.iloc[0]["start"] == at(2)
    assert gaps.iloc[0]["end"] == at(300)
    assert gaps.iloc[0]["seconds"] == 298.0


def test_a_gap_carries_the_session_it_belongs_to() -> None:
    events = a_timed_frame(
        [*a_turn(1, "p-1", session="abc"), *a_turn(60, "p-2", "abc")]
    )

    assert presence.stop_gaps(events).iloc[0]["session_id"] == "abc"


def test_a_stop_with_another_stop_before_the_next_submit_starts_no_gap() -> None:
    events = a_timed_frame(
        [
            *a_turn(1, "p-1"),
            # A second turn ran inside the wider span, so only its own tail is
            # one uninterrupted idle stretch.
            *a_turn(100, "p-2"),
            *a_turn(500, "p-3"),
        ]
    )

    gaps = presence.stop_gaps(events)

    assert list(gaps["start"]) == [at(2), at(101)]
    assert list(gaps["seconds"]) == [98.0, 399.0]


def test_a_stop_that_no_submit_follows_starts_no_gap() -> None:
    events = a_timed_frame(a_turn(1, "p-1"))

    assert presence.stop_gaps(events).empty


def test_a_gap_never_runs_from_one_session_into_another() -> None:
    events = a_timed_frame(
        [*a_turn(1, "p-1", session="abc"), *a_turn(300, "p-2", session="def")]
    )

    assert presence.stop_gaps(events).empty


def test_a_submit_arriving_before_the_stop_it_follows_is_an_error() -> None:
    events = a_timed_frame([*a_turn(100, "p-1"), *a_turn(50, "p-2")])

    with pytest.raises(presence.PresenceError, match="precedes the Stop"):
        presence.stop_gaps(events)


def test_a_frame_with_no_gaps_still_carries_the_gap_columns() -> None:
    events = a_timed_frame([(1, a_payload("SessionStart", source="startup"))])

    gaps = presence.stop_gaps(events)

    assert list(gaps.columns) == ["start", "end", "session_id", "seconds"]
    assert gaps["seconds"].dtype == "float64"


# --- fitting the model --------------------------------------------------------


def test_the_two_fitted_modes_sit_on_the_two_the_gaps_were_drawn_from() -> None:
    fit = presence.fit_presence(BIMODAL_GAPS)

    assert 50 < fit.present.median_seconds < 100
    assert 4800 < fit.absent.median_seconds < 16000


def test_the_two_fitted_weights_split_the_gaps_between_the_modes() -> None:
    fit = presence.fit_presence(BIMODAL_GAPS)

    assert fit.present.weight == pytest.approx(0.5, abs=0.05)
    assert fit.present.weight + fit.absent.weight == pytest.approx(1.0)


def test_presence_falls_as_the_gap_lengthens() -> None:
    fit = presence.fit_presence(BIMODAL_GAPS)

    probabilities = [fit.presence(seconds) for seconds in (1, 60, 600, 3600, 86400)]

    assert probabilities == sorted(probabilities, reverse=True)


def test_a_gap_of_seconds_reads_as_present_and_one_of_a_day_as_absent() -> None:
    fit = presence.fit_presence(BIMODAL_GAPS)

    assert fit.presence(5) > 0.99
    assert fit.presence(86400) < 0.01


def test_presence_reaches_even_odds_between_the_two_modes() -> None:
    fit = presence.fit_presence(BIMODAL_GAPS)

    assert (
        fit.present.median_seconds < fit.crossover_seconds < fit.absent.median_seconds
    )
    assert fit.presence(fit.crossover_seconds) == pytest.approx(0.5)


def test_the_same_gaps_fit_the_same_model_twice() -> None:
    first = presence.fit_presence(BIMODAL_GAPS)

    assert presence.fit_presence(list(reversed(BIMODAL_GAPS))) == first


def test_the_summary_names_both_modes_and_the_gaps_they_were_fitted_to() -> None:
    summary = presence.fit_presence(BIMODAL_GAPS).summary()

    assert "10 gaps" in summary
    assert "working mode" in summary
    assert "away mode" in summary


def test_too_few_gaps_to_fit_is_an_error() -> None:
    with pytest.raises(presence.PresenceError, match="too few"):
        presence.fit_presence(BIMODAL_GAPS[:9])


def test_a_gap_of_no_length_is_an_error() -> None:
    with pytest.raises(presence.PresenceError, match="must be positive"):
        presence.fit_presence([0.0, *BIMODAL_GAPS])


def test_gaps_that_are_all_the_same_length_are_an_error() -> None:
    with pytest.raises(presence.PresenceError, match="the same length"):
        presence.fit_presence([90.0] * 12)


def test_a_fit_that_has_not_settled_is_not_reported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(presence, "MAX_ITERATIONS", 1)

    with pytest.raises(presence.PresenceError, match="no start converged"):
        presence.fit_presence(BIMODAL_GAPS)


# --- the graded interval rows -------------------------------------------------


def test_every_gap_becomes_one_graded_row_in_the_interval_schema() -> None:
    events = turns_gapped_by(BIMODAL_GAPS)

    frame = presence.presence_intervals(events).frame

    assert len(frame) == len(BIMODAL_GAPS)
    assert list(frame.columns) == list(intervals.INTERVAL_COLUMNS)
    assert set(frame["state"]) == {"human_present"}


def test_a_graded_row_carries_a_confidence_that_follows_its_own_gap() -> None:
    events = turns_gapped_by(BIMODAL_GAPS)

    frame = presence.presence_intervals(events).frame

    assert frame.iloc[0]["confidence"] > 0.9
    assert frame.iloc[-1]["confidence"] < 0.1
    assert list(frame["confidence"]) == sorted(frame["confidence"], reverse=True)


def test_the_rows_come_back_with_the_model_that_graded_them() -> None:
    events = turns_gapped_by(BIMODAL_GAPS)

    result = presence.presence_intervals(events)

    assert result.fit.gaps == len(BIMODAL_GAPS)
    assert result.fit.present.median_seconds < result.fit.absent.median_seconds


def test_graded_rows_and_the_turns_they_follow_do_not_overlap() -> None:
    events = turns_gapped_by(BIMODAL_GAPS)

    turns = intervals.turn_intervals(events).frame
    graded = presence.presence_intervals(events).frame
    together = pd.concat([turns, graded]).sort_values("start")

    assert all(
        end <= start
        for end, start in zip(together["end"][:-1], together["start"][1:], strict=True)
    )


# --- grading an interrupted turn ----------------------------------------------


def _bimodal_gaps() -> list[float]:
    """Gaps shaped like the store's own: many short, a few overnight.

    Spread rather than repeated, because a component of identical lengths has no
    variance and the fit has nothing to estimate.
    """
    working = [40.0 + index * 7 for index in range(40)]
    away = [30000.0 + index * 900 for index in range(8)]
    return working + away


def test_a_short_interrupt_keeps_its_confidence() -> None:
    fit = presence.fit_presence(_bimodal_gaps())
    frame = intervals.interval_frame(
        [
            {
                "start": at(0),
                "end": at(30),
                "state": intervals.INTERRUPTED,
                "session_id": "one",
                "confidence": 1.0,
            }
        ]
    )

    graded = presence.grade_interrupts(frame, fit)

    assert graded["confidence"][0] > 0.9


def test_an_interrupt_that_swallowed_a_night_falls_to_near_zero() -> None:
    fit = presence.fit_presence(_bimodal_gaps())
    frame = intervals.interval_frame(
        [
            {
                "start": at(0),
                "end": at(15.7 * 60 * 60),
                "state": intervals.INTERRUPTED,
                "session_id": "one",
                "confidence": 1.0,
            }
        ]
    )

    graded = presence.grade_interrupts(frame, fit)

    assert graded["confidence"][0] < 0.1


def test_every_other_state_is_left_alone() -> None:
    fit = presence.fit_presence(_bimodal_gaps())
    frame = intervals.interval_frame(
        [
            {
                "start": at(0),
                "end": at(15.7 * 60 * 60),
                "state": intervals.CLAUDE_ACTIVE,
                "session_id": "one",
                "confidence": 1.0,
            },
            {
                "start": at(0),
                "end": at(15.7 * 60 * 60),
                "state": intervals.DORMANT,
                "session_id": "one",
                "confidence": 1.0,
            },
        ]
    )

    graded = presence.grade_interrupts(frame, fit)

    assert list(graded["confidence"]) == [1.0, 1.0]


def test_an_empty_table_grades_to_itself() -> None:
    fit = presence.fit_presence(_bimodal_gaps())
    frame = intervals.interval_frame([])

    assert presence.grade_interrupts(frame, fit).empty
