"""Tests for workflow_state_data.core.live_view — open issues by current phase."""

from workflow_state_data.core import live_view


def record(repo: str, number: int, state: str, phase: str) -> dict:
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


def test_closed_issues_are_excluded_from_live_view() -> None:
    records = [
        record("geoff/widgets", 1, "open", "tdd"),
        record("geoff/widgets", 2, "closed", "code-pr-review"),
    ]

    view = live_view(records)

    assert view == {
        "tdd": [{"repo": "geoff/widgets", "number": 1, "title": "Issue 1"}],
    }
