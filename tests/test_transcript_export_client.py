"""Tests for transcript_export.client — the AgentsView CLI boundary.

The subprocess call itself is the humble boundary; everything here exercises
argument building, JSON parsing, message paging, and loud failure with an
injected fake runner.
"""

import json
import subprocess
from collections.abc import Callable

import pytest

from dev_playbook.transcript_export.client import (
    DAEMON_URL,
    LIST_PAGE,
    SEARCH_MATCH_CAP,
    AgentsViewError,
    SessionNotFound,
    session_get,
    session_list,
    session_messages,
    session_search,
)


def completed(returncode: int, stdout: str = "", stderr: str = "") -> object:
    """A canned CompletedProcess standing in for one agentsview invocation."""
    return subprocess.CompletedProcess(
        args=["agentsview"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def recording_runner(results: list[object], calls: list[list[str]]) -> Callable:
    """A fake subprocess.run that records argv and replays canned results."""

    def runner(args: list[str], **kwargs: object) -> object:
        calls.append(args)
        return results.pop(0)

    return runner


def messages_page(rows: list[dict]) -> str:
    """JSON for one `session messages` page in the documented shape."""
    return json.dumps({"messages": rows, "count": len(rows)})


def list_page(ids: list[str], next_cursor: str | None = None) -> str:
    """JSON for one `session list` page; the final page omits `next_cursor`."""
    payload: dict = {"sessions": [{"id": sid} for sid in ids], "total": len(ids)}
    if next_cursor is not None:
        payload["next_cursor"] = next_cursor
    return json.dumps(payload)


def test_session_list_builds_argv_and_returns_the_session_rows() -> None:
    calls: list[list[str]] = []
    runner = recording_runner([completed(0, stdout=list_page(["s1"]))], calls)

    assert session_list(runner=runner) == [{"id": "s1"}]
    # Every command targets the standing daemon via `--server`, never auto-start,
    # and asks for the maximum page so the common archive is one round trip.
    assert calls == [
        [
            "agentsview",
            "--server",
            DAEMON_URL,
            "session",
            "list",
            "--format",
            "json",
            "--limit",
            str(LIST_PAGE),
        ]
    ]


def test_session_list_pages_on_next_cursor_until_the_key_is_absent() -> None:
    calls: list[list[str]] = []
    # The regression this guards: `--all` used to read page one and stop, so an
    # archive larger than a page exported a silent prefix. The daemon signals the
    # end by OMITTING next_cursor, not by nulling it or answering an empty batch.
    runner = recording_runner(
        [
            completed(0, stdout=list_page(["s0", "s1"], next_cursor="cur-1")),
            completed(0, stdout=list_page(["s2"])),
        ],
        calls,
    )

    assert [row["id"] for row in session_list(page=2, runner=runner)] == [
        "s0",
        "s1",
        "s2",
    ]
    assert "--cursor" not in calls[0]
    assert calls[1][calls[1].index("--cursor") + 1] == "cur-1"


def test_session_list_limit_stops_early_without_a_second_round_trip() -> None:
    calls: list[list[str]] = []
    # `--recent 2` must ask the daemon for two rows, not the whole archive: the
    # cursor is set, but the limit is already satisfied, so we never follow it.
    runner = recording_runner(
        [completed(0, stdout=list_page(["s0", "s1"], next_cursor="cur-1"))], calls
    )

    assert [row["id"] for row in session_list(limit=2, runner=runner)] == ["s0", "s1"]
    assert len(calls) == 1
    assert calls[0][calls[0].index("--limit") + 1] == "2"


def test_session_list_limit_truncates_an_overlong_page() -> None:
    calls: list[list[str]] = []
    runner = recording_runner(
        [completed(0, stdout=list_page(["s0", "s1", "s2"]))], calls
    )

    assert [row["id"] for row in session_list(limit=2, runner=runner)] == ["s0", "s1"]


def test_session_list_limit_larger_than_the_archive_returns_what_exists() -> None:
    calls: list[list[str]] = []
    runner = recording_runner([completed(0, stdout=list_page(["s0"]))], calls)

    assert [row["id"] for row in session_list(limit=9, runner=runner)] == ["s0"]


def test_session_list_fails_loud_on_a_repeating_cursor() -> None:
    calls: list[list[str]] = []
    # A daemon replaying one cursor would page forever; that is a fault to
    # surface, not a condition to silently swallow with a break.
    runner = recording_runner(
        [
            completed(0, stdout=list_page(["s0"], next_cursor="cur-1")),
            completed(0, stdout=list_page(["s1"], next_cursor="cur-1")),
        ],
        calls,
    )

    with pytest.raises(AgentsViewError, match="repeated a cursor"):
        session_list(page=1, runner=runner)


def test_session_search_builds_argv_and_parses_payload() -> None:
    calls: list[list[str]] = []
    payload = {"matches": [{"session_id": "s1"}], "next_cursor": None}
    runner = recording_runner([completed(0, stdout=json.dumps(payload))], calls)

    assert session_search("auth bug", runner=runner) == payload
    assert calls == [
        [
            "agentsview",
            "--server",
            DAEMON_URL,
            "session",
            "search",
            "auth bug",
            "--json",
            "--limit",
            str(SEARCH_MATCH_CAP),
        ]
    ]


def test_session_get_builds_argv_and_parses_payload() -> None:
    calls: list[list[str]] = []
    payload = {"id": "s1", "project": "demo", "message_count": 9}
    runner = recording_runner([completed(0, stdout=json.dumps(payload))], calls)

    result = session_get("s1", runner=runner)

    assert result == payload
    assert calls == [
        ["agentsview", "--server", DAEMON_URL, "session", "get", "s1", "--json"]
    ]


def test_session_messages_pages_until_empty_batch() -> None:
    calls: list[list[str]] = []
    page_one = [{"ordinal": 0}, {"ordinal": 5}, {"ordinal": 11}]
    page_two = [{"ordinal": 12}, {"ordinal": 20}]
    runner = recording_runner(
        [
            completed(0, stdout=messages_page(page_one)),
            completed(0, stdout=messages_page(page_two)),
            completed(0, stdout=messages_page([])),
        ],
        calls,
    )

    rows = session_messages("s1", page=3, runner=runner)

    assert [row["ordinal"] for row in rows] == [0, 5, 11, 12, 20]
    # Each page advances --from to the previous batch's last ordinal + 1.
    assert [call[call.index("--from") + 1] for call in calls] == ["0", "12", "21"]
    assert all(call[call.index("--limit") + 1] == "3" for call in calls)


def test_session_messages_defaults_to_page_100() -> None:
    calls: list[list[str]] = []
    runner = recording_runner([completed(0, stdout=messages_page([]))], calls)

    session_messages("s1", runner=runner)

    assert calls[0][calls[0].index("--limit") + 1] == "100"


def test_session_messages_guards_against_a_non_advancing_cursor() -> None:
    calls: list[list[str]] = []
    # A daemon that keeps replaying the same ordinal would loop forever; the
    # cursor advances to 1 on the first page, then the second page's ordinal
    # fails the last+1 <= frm guard and the loop stops. Exactly two pages are
    # queued, so a third call would raise IndexError instead of hanging.
    runner = recording_runner(
        [completed(0, stdout=messages_page([{"ordinal": 0}]))] * 2,
        calls,
    )

    rows = session_messages("s1", page=5, runner=runner)

    assert [row["ordinal"] for row in rows] == [0, 0]
    assert len(calls) == 2


def test_infrastructure_failure_stays_a_bare_agentsview_error() -> None:
    calls: list[list[str]] = []
    # A daemon-down / connection failure is not a missing session; it must
    # surface loudly as a bare AgentsViewError, never be mistaken for an
    # unresolvable subagent link.
    runner = recording_runner(
        [completed(1, stderr="error: connection refused (is the daemon running?)")],
        calls,
    )

    with pytest.raises(AgentsViewError, match="connection refused") as excinfo:
        session_get("s1", runner=runner)

    assert not isinstance(excinfo.value, SessionNotFound)


def test_infrastructure_not_found_is_not_escalated_to_session_not_found() -> None:
    calls: list[list[str]] = []
    # An infrastructure "not found" (host, config file, missing binary) carries
    # the words "not found" but names no session; escalating it to
    # SessionNotFound would silently swallow a real fault as an unresolvable
    # link, so it must stay a bare AgentsViewError.
    runner = recording_runner(
        [completed(1, stderr="error: host not found: 127.0.0.1:8080")], calls
    )

    with pytest.raises(AgentsViewError) as excinfo:
        session_get("s1", runner=runner)

    assert not isinstance(excinfo.value, SessionNotFound)


def test_session_not_found_is_an_agentsview_error() -> None:
    assert issubclass(SessionNotFound, AgentsViewError)


def test_session_get_raises_session_not_found_when_stderr_reports_not_found() -> None:
    calls: list[list[str]] = []
    runner = recording_runner(
        [completed(1, stderr="fatal: session agent-x not found")], calls
    )

    with pytest.raises(SessionNotFound, match="not found"):
        session_get("agent-x", runner=runner)
