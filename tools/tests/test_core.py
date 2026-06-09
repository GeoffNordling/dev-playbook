"""Tests for workflow_state_data.core — pure timeline-to-record transforms."""

from datetime import datetime

import pytest

from workflow_state_data.core import (
    LabelEvent,
    PersistentDoublePhaseError,
    reconstruct_phase_history,
)


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_single_phase_label_yields_one_open_visit() -> None:
    events = [LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00"))]

    history = reconstruct_phase_history(events, until=ts("2026-01-02T00:00:00+00:00"))

    assert len(history) == 1
    assert history[0].phase == "tdd"
    assert history[0].entered_at == ts("2026-01-01T00:00:00+00:00")
    assert history[0].exited_at is None
    assert history[0].duration_seconds == 86400.0


def test_same_timestamp_swap_closes_old_visit_and_opens_new() -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "code-pr-review"]
    assert history[0].exited_at == ts("2026-01-03T00:00:00+00:00")
    assert history[0].duration_seconds == 2 * 86400.0
    assert history[1].entered_at == ts("2026-01-03T00:00:00+00:00")
    assert history[1].exited_at is None


def test_swap_with_remove_before_add_yields_same_transition() -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "code-pr-review"]
    assert history[0].exited_at == ts("2026-01-03T00:00:00+00:00")
    assert history[1].exited_at is None


def test_metadata_labels_do_not_create_phase_visits() -> None:
    events = [
        LabelEvent("labeled", "mode:direct", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "tests:yes", ts("2026-01-02T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-03T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd"]


def test_unlabel_without_replacement_closes_the_visit() -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-05T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-06T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "build"]
    assert history[0].exited_at == ts("2026-01-02T00:00:00+00:00")
    assert history[1].entered_at == ts("2026-01-05T00:00:00+00:00")


def test_rework_bounce_produces_three_visits() -> None:
    # Modeled on #80's real build → code-pr-review → build bounce.
    events = [
        LabelEvent("labeled", "phase:build", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:build", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent(
            "unlabeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")
        ),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["build", "code-pr-review", "build"]
    assert history[2].exited_at is None


def test_persistent_double_phase_label_fails_loud() -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-02T00:00:00+00:00")),
    ]

    with pytest.raises(PersistentDoublePhaseError):
        reconstruct_phase_history(events, until=ts("2026-01-03T00:00:00+00:00"))
