"""Tests for workflow_state_data.cli — selector parsing and JSON emission."""

import json
from collections.abc import Callable
from datetime import datetime

import pytest

from workflow_state_data.cli import main
from workflow_state_data.core import IssueData, LabelEvent


def test_main_emits_issue_records_json(
    capsys: pytest.CaptureFixture,
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    tracked = make_issue(number=1)
    untriaged = make_issue(number=2, labels=("wontfix",), events=())

    exit_code = main(
        [],
        fetch=lambda repos: [tracked, untriaged],
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert exit_code == 0
    records = json.loads(capsys.readouterr().out)
    assert [record["number"] for record in records] == [1]
    assert records[0]["current_phase"] == "tdd"


def test_live_flag_emits_open_issues_grouped_by_phase(
    capsys: pytest.CaptureFixture,
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    fetched = [
        make_issue(repo="geoff/widgets", number=1, title="Issue 1"),
        make_issue(
            phase="code-pr-review", repo="geoff/gadgets", number=3, title="Issue 3"
        ),
    ]

    exit_code = main(
        ["--live"],
        fetch=lambda repos: fetched,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert exit_code == 0
    view = json.loads(capsys.readouterr().out)
    assert view == {
        "tdd": [{"repo": "geoff/widgets", "number": 1, "title": "Issue 1"}],
        "code-pr-review": [{"repo": "geoff/gadgets", "number": 3, "title": "Issue 3"}],
    }


def test_repo_selector_narrows_fetch(ts: Callable[[str], datetime]) -> None:
    fetched_with: list[list[str] | None] = []

    def fetch(repos: list[str] | None) -> list[IssueData]:
        """Record the repos selector each fetch call receives."""
        fetched_with.append(repos)
        return []

    main(
        ["--repo", "geoff/widgets,geoff/gadgets"],
        fetch=fetch,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert fetched_with == [["geoff/widgets", "geoff/gadgets"]]


def test_issue_selector_filters_records(
    capsys: pytest.CaptureFixture,
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    fetched = [make_issue(number=1), make_issue(number=2)]

    exit_code = main(
        ["--repo", "geoff/widgets", "--issue", "2"],
        fetch=lambda repos: fetched,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert exit_code == 0
    records = json.loads(capsys.readouterr().out)
    assert [record["number"] for record in records] == [2]


def test_issue_selector_rejects_empty_elements(
    ts: Callable[[str], datetime],
) -> None:
    with pytest.raises(SystemExit):
        main(
            ["--repo", "geoff/widgets", "--issue", "2,"],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_repo_selector_rejects_empty_elements(
    ts: Callable[[str], datetime],
) -> None:
    with pytest.raises(SystemExit):
        main(
            ["--repo", "geoff/widgets,"],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_repo_elements_are_stripped_of_surrounding_whitespace(
    ts: Callable[[str], datetime],
) -> None:
    fetched_with: list[list[str] | None] = []

    def fetch(repos: list[str] | None) -> list[IssueData]:
        """Record the repos selector each fetch call receives."""
        fetched_with.append(repos)
        return []

    main(
        ["--repo", "geoff/widgets, geoff/gadgets"],
        fetch=fetch,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert fetched_with == [["geoff/widgets", "geoff/gadgets"]]


def test_empty_repo_value_is_rejected_not_widened_to_account_scope(
    ts: Callable[[str], datetime],
) -> None:
    with pytest.raises(SystemExit):
        main(
            ["--repo", ""],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_issue_selector_rejects_non_numeric_elements(
    ts: Callable[[str], datetime],
) -> None:
    with pytest.raises(SystemExit):
        main(
            ["--repo", "geoff/widgets", "--issue", "7,abc"],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_requested_issue_absent_from_fetch_fails_loud(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    fetched = [make_issue(number=1)]

    with pytest.raises(SystemExit, match="9"):
        main(
            ["--repo", "geoff/widgets", "--issue", "9"],
            fetch=lambda repos: fetched,
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_requested_issue_dropped_by_scope_rule_fails_loud(
    ts: Callable[[str], datetime],
    make_issue: Callable[..., IssueData],
) -> None:
    """A fetched issue scope-dropped for a historical non-canonical label errors."""
    dropped = make_issue(
        number=7,
        events=(
            LabelEvent("labeled", "phase:tdd", ts("2026-01-01T00:00:00+00:00")),
            LabelEvent("labeled", "wontfix", ts("2026-01-01T01:00:00+00:00")),
            LabelEvent("unlabeled", "wontfix", ts("2026-01-01T02:00:00+00:00")),
        ),
    )

    with pytest.raises(SystemExit, match="7"):
        main(
            ["--repo", "geoff/widgets", "--issue", "7"],
            fetch=lambda repos: [dropped],
            now=ts("2026-01-02T00:00:00+00:00"),
        )


def test_issue_selector_requires_exactly_one_repo(
    ts: Callable[[str], datetime],
) -> None:
    with pytest.raises(SystemExit):
        main(
            ["--issue", "2"],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )
