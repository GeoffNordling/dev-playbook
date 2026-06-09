"""Tests for workflow_state_data.github — deterministic fetch machinery.

The gh subprocess itself is the humble boundary; everything here exercises
query building, response parsing, pagination, and error handling with
injected fakes.
"""

import json
import subprocess
from collections.abc import Callable
from datetime import datetime

import pytest

from workflow_state_data.core import LabelEvent
from workflow_state_data.github import (
    GitHubError,
    build_search_query,
    fetch_issues,
    gh_graphql,
    parse_issue_node,
)


def completed(returncode: int, stdout: str = "", stderr: str = "") -> object:
    return subprocess.CompletedProcess(
        args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def queued_runner(results: list[object]) -> Callable:
    """A fake subprocess.run that replays canned results in order."""

    def runner(*args: object, **kwargs: object) -> object:
        return results.pop(0)

    return runner


def issue_node(**overrides: object) -> dict:
    defaults: dict = {
        "id": "ID7",
        "number": 7,
        "title": "Add widget",
        "state": "OPEN",
        "createdAt": "2026-01-01T00:00:00Z",
        "closedAt": None,
        "repository": {"nameWithOwner": "geoff/widgets"},
        "labels": {"nodes": [{"name": "mode:direct"}, {"name": "phase:tdd"}]},
        "comments": {"totalCount": 3},
        "timelineItems": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [
                {
                    "__typename": "LabeledEvent",
                    "label": {"name": "phase:tdd"},
                    "createdAt": "2026-01-01T00:00:00Z",
                },
                {
                    "__typename": "UnlabeledEvent",
                    "label": {"name": "phase:tdd"},
                    "createdAt": "2026-01-02T00:00:00Z",
                },
            ],
        },
    }
    return {**defaults, **overrides}


def test_search_query_is_account_wide_and_phase_filtered() -> None:
    query = build_search_query(repos=None)

    assert "is:issue" in query
    assert "user:@me" in query
    # All canonical phase labels OR-ed in a single comma-joined qualifier.
    assert query.count("label:") == 1
    assert '"phase:tdd"' in query
    assert '"phase:sdd-code-pr-review"' in query


def test_search_query_narrows_to_given_repos() -> None:
    query = build_search_query(repos=["geoff/widgets", "geoff/gadgets"])

    assert "repo:geoff/widgets" in query
    assert "repo:geoff/gadgets" in query
    assert "user:@me" not in query


def test_parse_issue_node_maps_graphql_shape_to_issue_data() -> None:
    issue = parse_issue_node(issue_node())

    assert issue.repo == "geoff/widgets"
    assert issue.number == 7
    assert issue.title == "Add widget"
    assert issue.state == "open"
    assert issue.created_at == datetime.fromisoformat("2026-01-01T00:00:00+00:00")
    assert issue.closed_at is None
    assert issue.labels == ("mode:direct", "phase:tdd")
    assert issue.comment_count == 3
    assert issue.events == (
        LabelEvent(
            "labeled",
            "phase:tdd",
            datetime.fromisoformat("2026-01-01T00:00:00+00:00"),
        ),
        LabelEvent(
            "unlabeled",
            "phase:tdd",
            datetime.fromisoformat("2026-01-02T00:00:00+00:00"),
        ),
    )


def test_parse_issue_node_parses_closed_issue() -> None:
    issue = parse_issue_node(
        issue_node(state="CLOSED", closedAt="2026-01-05T00:00:00Z")
    )

    assert issue.state == "closed"
    assert issue.closed_at == datetime.fromisoformat("2026-01-05T00:00:00+00:00")


def search_page(nodes: list[dict], end_cursor: str | None) -> dict:
    return {
        "search": {
            "pageInfo": {
                "hasNextPage": end_cursor is not None,
                "endCursor": end_cursor,
            },
            "nodes": nodes,
        }
    }


def test_fetch_issues_paginates_search_results() -> None:
    cursors: list[str | None] = []

    def run_query(query: str, variables: dict) -> dict:
        cursors.append(variables.get("cursor"))
        if variables.get("cursor") is None:
            return search_page([issue_node()], "CUR1")
        return search_page([issue_node(number=8)], None)

    issues = fetch_issues(repos=None, run_query=run_query)

    assert [issue.number for issue in issues] == [7, 8]
    assert cursors == [None, "CUR1"]


def timeline_event(typename: str, label: str, at: str) -> dict:
    return {"__typename": typename, "label": {"name": label}, "createdAt": at}


def routed_run_query(
    search_response: dict, timeline_response: dict, timeline_calls: list[dict]
) -> Callable[[str, dict], dict]:
    """A fake gh: routes search queries and per-issue timeline queries."""

    def run_query(query: str, variables: dict) -> dict:
        if "search(" in query:
            return search_response
        timeline_calls.append(variables)
        return timeline_response

    return run_query


def test_fetch_issues_paginates_long_timelines() -> None:
    truncated = issue_node(
        timelineItems={
            "pageInfo": {"hasNextPage": True, "endCursor": "T1"},
            "nodes": [
                timeline_event("LabeledEvent", "phase:tdd", "2026-01-01T00:00:00Z")
            ],
        }
    )
    rest = {
        "node": {
            "timelineItems": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    timeline_event(
                        "UnlabeledEvent", "phase:tdd", "2026-01-02T00:00:00Z"
                    ),
                    timeline_event(
                        "LabeledEvent", "phase:build", "2026-01-02T00:00:00Z"
                    ),
                ],
            }
        }
    }
    timeline_calls: list[dict] = []
    run_query = routed_run_query(search_page([truncated], None), rest, timeline_calls)

    issues = fetch_issues(repos=None, run_query=run_query)

    assert timeline_calls == [{"id": "ID7", "cursor": "T1"}]
    assert [event.label for event in issues[0].events] == [
        "phase:tdd",
        "phase:tdd",
        "phase:build",
    ]
    assert [event.action for event in issues[0].events] == [
        "labeled",
        "unlabeled",
        "labeled",
    ]


def test_gh_graphql_fails_loud_on_subprocess_error() -> None:
    runner = queued_runner([completed(1, stderr="gh: HTTP 401 Bad credentials")])

    with pytest.raises(GitHubError, match="Bad credentials"):
        gh_graphql("query {}", {}, runner=runner, sleep=lambda _: None)


def test_gh_graphql_fails_loud_on_graphql_errors_payload() -> None:
    body = json.dumps({"data": None, "errors": [{"message": "Could not resolve"}]})
    runner = queued_runner([completed(0, stdout=body)])

    with pytest.raises(GitHubError, match="Could not resolve"):
        gh_graphql("query {}", {}, runner=runner, sleep=lambda _: None)


def test_gh_graphql_retries_once_after_rate_limit() -> None:
    body = json.dumps({"data": {"ok": True}})
    runner = queued_runner(
        [
            completed(
                1, stderr="gh: You have exceeded a secondary rate limit (HTTP 429)"
            ),
            completed(0, stdout=body),
        ]
    )
    sleeps: list[float] = []

    data = gh_graphql("query {}", {}, runner=runner, sleep=sleeps.append)

    assert data == {"ok": True}
    assert len(sleeps) == 1
