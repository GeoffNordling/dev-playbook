"""Tests for workflow_state_data.core — pure timeline-to-record transforms."""

from collections.abc import Callable
from datetime import datetime

import pytest

from workflow_state_data.core import (
    IssueData,
    LabelEvent,
    PersistentDoublePhaseError,
    build_record,
    live_view,
    reconstruct_phase_history,
)


@pytest.fixture
def bounce_events(ts: Callable[[str], datetime]) -> tuple[LabelEvent, ...]:
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


def test_single_phase_label_yields_one_open_visit(
    ts: Callable[[str], datetime],
) -> None:
    events = [LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00"))]

    history = reconstruct_phase_history(events, until=ts("2026-01-02T00:00:00+00:00"))

    assert len(history) == 1
    assert history[0].phase == "tdd"
    assert history[0].entered_at == ts("2026-01-01T00:00:00+00:00")
    assert history[0].exited_at is None
    assert history[0].duration_seconds == 86400.0


def test_same_timestamp_swap_closes_old_visit_and_opens_new(
    ts: Callable[[str], datetime],
) -> None:
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


def test_swap_with_remove_before_add_yields_same_transition(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "code-pr-review"]
    assert history[0].exited_at == ts("2026-01-03T00:00:00+00:00")
    assert history[1].exited_at is None


def test_metadata_labels_do_not_create_phase_visits(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "mode:direct", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "tests:yes", ts("2026-01-02T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-03T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd"]


def test_unlabel_without_replacement_closes_the_visit(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-05T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-06T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "build"]
    assert history[0].exited_at == ts("2026-01-02T00:00:00+00:00")
    assert history[1].entered_at == ts("2026-01-05T00:00:00+00:00")


def test_rework_bounce_produces_three_visits(
    ts: Callable[[str], datetime],
    bounce_events: tuple[LabelEvent, ...],
) -> None:
    history = reconstruct_phase_history(
        list(bounce_events), until=ts("2026-01-04T00:00:00+00:00")
    )

    assert [visit.phase for visit in history] == ["build", "code-pr-review", "build"]
    assert history[2].exited_at is None


def test_swap_straddling_a_second_boundary_is_tolerated(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-03T00:00:01+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:02+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "code-pr-review"]
    assert history[0].exited_at == ts("2026-01-03T00:00:02+00:00")
    assert history[1].entered_at == ts("2026-01-03T00:00:02+00:00")
    assert history[1].exited_at is None


def test_swap_straddling_closed_at_is_tolerated(
    ts: Callable[[str], datetime],
) -> None:
    """A close-and-swap whose unlabeled half lands just past until still settles."""
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-03T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-03T00:00:01+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-03T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd", "code-pr-review"]
    assert history[0].exited_at == ts("2026-01-03T00:00:00+00:00")
    assert history[1].entered_at == ts("2026-01-03T00:00:00+00:00")
    assert history[1].exited_at is None


def test_persistent_double_phase_label_fails_loud(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-02T00:00:00+00:00")),
    ]

    with pytest.raises(PersistentDoublePhaseError):
        reconstruct_phase_history(events, until=ts("2026-01-03T00:00:00+00:00"))


def test_label_added_after_until_is_ignored(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-10T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-10T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-05T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd"]
    assert history[0].exited_at is None
    assert history[0].duration_seconds == 4 * 86400.0


def test_label_removed_after_until_is_ignored(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("unlabeled", "phase:tdd", ts("2026-01-10T00:00:00+00:00")),
    ]

    history = reconstruct_phase_history(events, until=ts("2026-01-05T00:00:00+00:00"))

    assert [visit.phase for visit in history] == ["tdd"]
    assert history[0].exited_at is None
    assert history[0].duration_seconds == 4 * 86400.0


def test_double_phase_persisting_past_the_next_event_fails_loud(
    ts: Callable[[str], datetime],
) -> None:
    events = [
        LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
        LabelEvent("labeled", "phase:code-pr-review", ts("2026-01-02T00:00:00+00:00")),
        LabelEvent("labeled", "phase:build", ts("2026-01-03T00:00:00+00:00")),
    ]

    with pytest.raises(PersistentDoublePhaseError):
        reconstruct_phase_history(events, until=ts("2026-01-04T00:00:00+00:00"))


def test_build_record_assembles_identity_and_phase_history(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
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


def test_completed_issue_lifetime_and_final_phase_measure_to_close(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
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


def test_open_issue_lifetime_measures_to_now(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue()

    record = build_record(issue, now=ts("2026-01-03T00:00:00+00:00"))

    assert record is not None
    assert record["lifetime_seconds"] == 2 * 86400.0


def test_transitions_carry_backward_flag_and_rework_count(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
    bounce_events: tuple[LabelEvent, ...],
) -> None:
    issue = make_issue(
        events=bounce_events,
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


def test_phase_visits_count_repeated_cycles(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
    bounce_events: tuple[LabelEvent, ...],
) -> None:
    issue = make_issue(
        events=bounce_events,
        labels=("category:enhancement", "mode:direct", "tests:no", "phase:build"),
    )

    record = build_record(issue, now=ts("2026-01-04T00:00:00+00:00"))

    assert record is not None
    assert record["phase_visits"] == {"build": 2, "code-pr-review": 1}


def test_record_reports_issue_comment_count(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue(comment_count=5)

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is not None
    assert record["comments"] == {"issue": 5, "total": 5}


def test_record_carries_category_mode_tests_metadata(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue()

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is not None
    assert record["category"] == "enhancement"
    assert record["mode"] == "direct"
    assert record["tests"] == "yes"


def test_issue_with_non_canonical_current_label_is_skipped(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue(
        labels=("category:enhancement", "mode:direct", "tests:yes", "phase:review")
    )

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is None


def test_issue_with_non_canonical_label_in_timeline_is_skipped(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue(
        events=(
            LabelEvent("labeled", "phase:old-name", ts("2026-01-01T00:00:00+00:00")),
            LabelEvent("unlabeled", "phase:old-name", ts("2026-01-02T00:00:00+00:00")),
            LabelEvent("labeled", "phase:tdd", ts("2026-01-02T00:00:00+00:00")),
        )
    )

    record = build_record(issue, now=ts("2026-01-03T00:00:00+00:00"))

    assert record is None


def test_issue_with_no_phase_history_is_skipped(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    issue = make_issue(labels=(), events=(), comment_count=0)

    record = build_record(issue, now=ts("2026-01-02T00:00:00+00:00"))

    assert record is None


def record(repo: str, number: int, state: str, phase: str | None) -> dict:
    """A minimal issue record carrying just the fields live_view reads."""
    return {
        "repo": repo,
        "number": number,
        "title": f"Issue {number}",
        "state": state,
        "current_phase": phase,
    }


def test_groups_open_issues_by_current_phase() -> None:
    records = [
        record("geoff/widgets", 1, "open", "tdd"),
        record("geoff/widgets", 2, "open", "code-pr-review"),
        record("geoff/gadgets", 3, "open", "tdd"),
    ]

    view = live_view(records)

    assert view == {
        "tdd": [
            {"repo": "geoff/widgets", "number": 1, "title": "Issue 1"},
            {"repo": "geoff/gadgets", "number": 3, "title": "Issue 3"},
        ],
        "code-pr-review": [
            {"repo": "geoff/widgets", "number": 2, "title": "Issue 2"},
        ],
    }


def test_open_issue_without_current_phase_appears_under_no_phase() -> None:
    records = [record("geoff/widgets", 1, "open", None)]

    view = live_view(records)

    assert view == {
        "no-phase": [{"repo": "geoff/widgets", "number": 1, "title": "Issue 1"}],
    }


def test_closed_issues_are_excluded_from_live_view() -> None:
    records = [
        record("geoff/widgets", 1, "open", "tdd"),
        record("geoff/widgets", 2, "closed", "code-pr-review"),
    ]

    view = live_view(records)

    assert view == {
        "tdd": [{"repo": "geoff/widgets", "number": 1, "title": "Issue 1"}],
    }
