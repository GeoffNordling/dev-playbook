"""Tests for workflow_state_data.cli — selector parsing and JSON emission."""

import json
from datetime import datetime

import pytest

from workflow_state_data.cli import main
from workflow_state_data.core import IssueData, LabelEvent


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def issue(repo: str, number: int, phase: str) -> IssueData:
    return IssueData(
        repo=repo,
        number=number,
        title=f"Issue {number}",
        state="open",
        created_at=ts("2026-01-01T00:00:00+00:00"),
        closed_at=None,
        labels=("category:enhancement", "mode:direct", "tests:yes", f"phase:{phase}"),
        events=(
            LabelEvent("labeled", f"phase:{phase}", ts("2026-01-01T00:00:00+00:00")),
        ),
        comment_count=0,
    )


def untriaged(repo: str, number: int) -> IssueData:
    return IssueData(
        repo=repo,
        number=number,
        title=f"Issue {number}",
        state="open",
        created_at=ts("2026-01-01T00:00:00+00:00"),
        closed_at=None,
        labels=("wontfix",),
        events=(),
        comment_count=0,
    )


def test_main_emits_issue_records_json(capsys: pytest.CaptureFixture) -> None:
    fetched = [issue("geoff/widgets", 1, "tdd"), untriaged("geoff/widgets", 2)]

    exit_code = main(
        [],
        fetch=lambda repos: fetched,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert exit_code == 0
    records = json.loads(capsys.readouterr().out)
    assert [record["number"] for record in records] == [1]
    assert records[0]["current_phase"] == "tdd"


def test_live_flag_emits_open_issues_grouped_by_phase(
    capsys: pytest.CaptureFixture,
) -> None:
    fetched = [
        issue("geoff/widgets", 1, "tdd"),
        issue("geoff/gadgets", 3, "code-pr-review"),
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


def test_repo_selector_narrows_fetch() -> None:
    fetched_with: list[list[str] | None] = []

    def fetch(repos: list[str] | None) -> list[IssueData]:
        fetched_with.append(repos)
        return []

    main(
        ["--repo", "geoff/widgets,geoff/gadgets"],
        fetch=fetch,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert fetched_with == [["geoff/widgets", "geoff/gadgets"]]


def test_issue_selector_filters_records(capsys: pytest.CaptureFixture) -> None:
    fetched = [issue("geoff/widgets", 1, "tdd"), issue("geoff/widgets", 2, "tdd")]

    exit_code = main(
        ["--repo", "geoff/widgets", "--issue", "2"],
        fetch=lambda repos: fetched,
        now=ts("2026-01-02T00:00:00+00:00"),
    )

    assert exit_code == 0
    records = json.loads(capsys.readouterr().out)
    assert [record["number"] for record in records] == [2]


def test_issue_selector_requires_exactly_one_repo() -> None:
    with pytest.raises(SystemExit):
        main(
            ["--issue", "2"],
            fetch=lambda repos: [],
            now=ts("2026-01-02T00:00:00+00:00"),
        )
