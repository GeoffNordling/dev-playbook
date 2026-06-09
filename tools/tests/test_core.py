"""Tests for workflow_state_data.core — pure timeline-to-record transforms."""

from datetime import datetime

import pytest

from workflow_state_data.core import (
    IssueData,
    LabelEvent,
    PersistentDoublePhaseError,
    build_record,
    reconstruct_phase_history,
)


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def make_issue(**overrides: object) -> IssueData:
    """An open, in-flight tdd issue; tests override what they exercise."""
    defaults: dict = {
        "repo": "geoff/widgets",
        "number": 7,
        "title": "Add widget",
        "state": "open",
        "created_at": ts("2026-01-01T00:00:00+00:00"),
        "closed_at": None,
        "labels": (
            "category:enhancement",
            "mode:direct",
            "tests:yes",
            "phase:tdd",
        ),
        "events": (
            LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        ),
        "comment_count": 3,
    }
    return IssueData(**{**defaults, **overrides})


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


def test_build_record_assembles_identity_and_phase_history() -> None:
    issue = make_issue()
    now = ts("2026-01-02T00:00:00+00:00")

    record = build_record(issue, now=now)

    assert record is not None
    assert record["repo"] == "geoff/widgets"
    assert record["number"] == 7
    assert record["title"] == "Add widget"
    assert record["state"] == "open"
    assert record["created_at"] == "2026-01-01T00:00:00+00:00"
    assert record["closed_at"] is None
    assert record["current_phase"] == "tdd"
    assert record["phase_history"] == [
        {
            "phase": "tdd",
            "entered_at": "2026-01-01T00:00:00+00:00",
            "exited_at": None,
            "duration_seconds": 86400.0,
        }
    ]


def test_completed_issue_lifetime_and_final_phase_measure_to_close() -> None:
    issue = make_issue(
        state="closed",
        closed_at=ts("2026-01-05T00:00:00+00:00"),
        events=(
            LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
            LabelEvent(
                "labeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")
            ),
            LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:00+00:00")),
        ),
        labels=(
            "category:enhancement",
            "mode:direct",
            "tests:yes",
            "phase:code-pr-review",
        ),
    )

    record = build_record(issue, now=ts("2026-02-01T00:00:00+00:00"))

    assert record is not None
    assert record["lifetime_seconds"] == 4 * 86400.0
    durations = {
        entry["phase"]: entry["duration_seconds"] for entry in record["phase_history"]
    }
    assert durations == {"tdd": 2 * 86400.0, "code-pr-review": 2 * 86400.0}


def test_open_issue_lifetime_measures_to_now() -> None:
    issue = make_issue()

    record = build_record(issue, now=ts("2026-01-03T00:00:00+00:00"))

    assert record is not None
    assert record["lifetime_seconds"] == 2 * 86400.0


def bounce_events() -> tuple[LabelEvent, ...]:
    """A build → code-pr-review → build rework bounce (modeled on #80)."""
    return (
        LabelEvent("labeled", "phase:build", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:build", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent(
            "unlabeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")
        ),
    )


def test_transitions_carry_backward_flag_and_rework_count() -> None:
    issue = make_issue(
        events=bounce_events(),
        labels=("category:enhancement", "mode:direct", "tests:no", "phase:build"),
    )

    record = build_record(issue, now=ts("2026-01-04T00:00:00+00:00"))

    assert record is not None
    assert record["transitions"] == [
        {
            "from": "build",
            "to": "code-pr-review",
            "at": "2026-01-02T00:00:00+00:00",
            "backward": False,
        },
        {
            "from": "code-pr-review",
            "to": "build",
            "at": "2026-01-03T00:00:00+00:00",
            "backward": True,
        },
    ]
    assert record["rework_count"] == 1


def test_phase_visits_count_repeated_cycles() -> None:
    issue = make_issue(
        events=bounce_events(),
        labels=("category:enhancement", "mode:direct", "tests:no", "phase:build"),
    )

    record = build_record(issue, now=ts("2026-01-04T00:00:00+00:00"))

    assert record is not None
    assert record["phase_visits"] == {"build": 2, "code-pr-review": 1}


def test_record_reports_issue_comment_count() -> None:
    issue = make_issue(comment_count=5)

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is not None
    assert record["comments"] == {"issue": 5, "total": 5}


def test_record_carries_category_mode_tests_metadata() -> None:
    issue = make_issue()

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is not None
    assert record["category"] == "enhancement"
    assert record["mode"] == "direct"
    assert record["tests"] == "yes"


def test_issue_with_non_canonical_current_label_is_skipped() -> None:
    issue = make_issue(
        labels=("category:enhancement", "mode:direct", "tests:yes", "phase:review")
    )

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is None


def test_issue_with_non_canonical_label_in_timeline_is_skipped() -> None:
    issue = make_issue(
        events=(
            LabelEvent("labeled", "phase:old-name", ts("2026-01-01T00:00:00+00:00")),
            LabelEvent("unlabeled", "phase:old-name", ts("2026-01-02T00:00:00+00:00")),
            LabelEvent("labeled", "phase:tdd", ts("2026-01-02T00:00:00+00:00")),
        )
    )

    record = build_record(issue, now=ts("2026-01-03T00:00:00+00:00"))

    assert record is None


def test_issue_with_no_phase_history_is_skipped() -> None:
    issue = make_issue(labels=(), events=(), comment_count=0)

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is None
