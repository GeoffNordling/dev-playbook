"""Tests for sub-agent recursion: the render callback and the transcript walk.

Two tiers. The first exercises the `render_subagent` callback threading in
`render` with a trivial stub. The second drives `transcript.render_session`
against a fake AgentsView daemon — a single runner that dispatches `session get`
and `session messages` from a hand-authored `{id: {"meta", "rows"}}` map — and
asserts structural invariants (well-formed XML, nesting, guard placeholders),
never trimmed real sessions.
"""

import json
import subprocess
import xml.etree.ElementTree as ET
from collections.abc import Callable

import pytest

from transcript_export import transcript
from transcript_export.model import tool_call_from_row
from transcript_export.render import render_tool_call
from transcript_export.transcript import render_session


def tc_row(
    *,
    tool_name: str = "Task",
    tool_use_id: str = "toolu_1",
    input_json: str = "{}",
    subagent_session_id: str | None = None,
) -> dict:
    """A raw `tool_calls[]` entry; `subagent_session_id` set marks a spawn."""
    row: dict = {
        "tool_name": tool_name,
        "tool_use_id": tool_use_id,
        "input_json": input_json,
        "result_content": "",
        "result_content_length": 0,
    }
    if subagent_session_id is not None:
        row["subagent_session_id"] = subagent_session_id
    return row


def assistant_row(
    *,
    ordinal: int,
    source_uuid: str,
    source_parent_uuid: str | None = None,
    content: str = "",
    tool_calls: list[dict] | None = None,
) -> dict:
    """A raw assistant message row, optionally carrying tool calls."""
    row: dict = {
        "ordinal": ordinal,
        "role": "assistant",
        "source_type": "assistant",
        "source_uuid": source_uuid,
        "content": content,
        "model": "m",
    }
    if source_parent_uuid is not None:
        row["source_parent_uuid"] = source_parent_uuid
    if tool_calls is not None:
        row["tool_calls"] = tool_calls
    return row


def user_row(
    *,
    ordinal: int,
    source_uuid: str,
    source_parent_uuid: str | None = None,
    content: str = "ask",
) -> dict:
    """A raw user message row."""
    row: dict = {
        "ordinal": ordinal,
        "role": "user",
        "source_type": "user",
        "source_uuid": source_uuid,
        "content": content,
    }
    if source_parent_uuid is not None:
        row["source_parent_uuid"] = source_parent_uuid
    return row


def completed(stdout: str) -> object:
    """A canned successful CompletedProcess carrying one JSON payload."""
    return subprocess.CompletedProcess(args=["agentsview"], returncode=0, stdout=stdout)


def fake_daemon(sessions: dict[str, dict]) -> Callable:
    """A fake `subprocess.run` dispatching `session get`/`messages` from a map.

    `sessions` maps a session id to `{"meta": {...}, "rows": [...]}`. `get`
    returns the meta; `messages` returns rows with ordinal >= `--from` so paging
    exhausts after the live rows (the second page comes back empty).
    """

    def runner(args: list[str], **kwargs: object) -> object:
        cmd, sid = args[2], args[3]
        entry = sessions[sid]
        if cmd == "get":
            return completed(json.dumps(entry["meta"]))
        if cmd == "messages":
            frm = int(args[args.index("--from") + 1])
            rows = [r for r in entry["rows"] if r["ordinal"] >= frm]
            return completed(json.dumps({"messages": rows, "count": len(rows)}))
        raise AssertionError(f"unexpected agentsview command: {cmd}")

    return runner


# --- render.py callback threading -------------------------------------------


def test_render_tool_call_embeds_subagent_when_callback_supplied() -> None:
    out = render_tool_call(
        tool_call_from_row(tc_row(subagent_session_id="agent-abc")),
        render_subagent=lambda sid: f'<subagent id="{sid}"/>',
    )
    el = ET.fromstring(out)
    sub = el.find("subagent")
    assert sub is not None
    assert sub.attrib["id"] == "agent-abc"


def test_render_tool_call_ignores_subagent_without_callback() -> None:
    out = render_tool_call(tool_call_from_row(tc_row(subagent_session_id="agent-abc")))
    assert ET.fromstring(out).find("subagent") is None


def test_render_tool_call_callback_not_called_without_subagent_id() -> None:
    def boom(_sid: str) -> str:
        raise AssertionError("callback must not fire for a non-spawning call")

    out = render_tool_call(tool_call_from_row(tc_row()), render_subagent=boom)
    assert ET.fromstring(out).find("subagent") is None


# --- transcript.render_session: header + nesting ----------------------------


def test_render_session_emits_header_and_closes() -> None:
    sessions = {
        "s1": {
            "meta": {"id": "s1", "project": "demo", "message_count": 1},
            "rows": [user_row(ordinal=1, source_uuid="u0")],
        }
    }
    el = ET.fromstring(render_session("s1", runner=fake_daemon(sessions)))
    assert el.tag == "session"
    assert el.attrib["id"] == "s1"
    assert [k.tag for k in el] == ["user"]


def test_render_session_nests_subagent_inside_tool_call() -> None:
    sessions = {
        "parent": {
            "meta": {"id": "parent", "message_count": 2},
            "rows": [
                user_row(ordinal=1, source_uuid="u0"),
                assistant_row(
                    ordinal=2,
                    source_uuid="u1",
                    source_parent_uuid="u0",
                    content="spawning a helper",
                    tool_calls=[tc_row(subagent_session_id="agent-child")],
                ),
            ],
        },
        "agent-child": {
            "meta": {"id": "agent-child", "message_count": 1},
            "rows": [assistant_row(ordinal=1, source_uuid="c0", content="child reply")],
        },
    }
    el = ET.fromstring(render_session("parent", runner=fake_daemon(sessions)))
    call = el.find("assistant/tool-call")
    assert call is not None
    sub = call.find("subagent")
    assert sub is not None
    assert sub.attrib == {"id": "agent-child", "messages": "1"}
    assert sub.find("assistant").text == "child reply"  # type: ignore[union-attr]


def test_render_session_recurses_into_grandchild() -> None:
    sessions = {
        "parent": {
            "meta": {"id": "parent", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="u1",
                    content="x",
                    tool_calls=[tc_row(subagent_session_id="child")],
                )
            ],
        },
        "child": {
            "meta": {"id": "child", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="c1",
                    content="y",
                    tool_calls=[tc_row(subagent_session_id="grandchild")],
                )
            ],
        },
        "grandchild": {
            "meta": {"id": "grandchild", "message_count": 1},
            "rows": [assistant_row(ordinal=1, source_uuid="g1", content="deep")],
        },
    }
    el = ET.fromstring(render_session("parent", runner=fake_daemon(sessions)))
    deep = el.find("assistant/tool-call/subagent/assistant/tool-call/subagent")
    assert deep is not None
    assert deep.attrib["id"] == "grandchild"
    assert deep.find("assistant").text == "deep"  # type: ignore[union-attr]


# --- guards -----------------------------------------------------------------


def test_subagent_cycle_guard_emits_placeholder() -> None:
    # The child spawns its own parent: the back-link must not recurse forever.
    sessions = {
        "parent": {
            "meta": {"id": "parent", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="u1",
                    content="x",
                    tool_calls=[tc_row(subagent_session_id="child")],
                )
            ],
        },
        "child": {
            "meta": {"id": "child", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="c1",
                    content="y",
                    tool_calls=[tc_row(subagent_session_id="parent")],
                )
            ],
        },
    }
    el = ET.fromstring(render_session("parent", runner=fake_daemon(sessions)))
    back = el.find("assistant/tool-call/subagent/assistant/tool-call/subagent")
    assert back is not None
    assert back.attrib == {"id": "parent", "omitted": "cycle"}
    assert len(back) == 0  # self-closing placeholder, not expanded


def test_subagent_depth_guard_emits_placeholder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(transcript, "MAX_SUBAGENT_DEPTH", 1)
    sessions: dict[str, dict] = {
        "parent": {
            "meta": {"id": "parent", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="u1",
                    content="x",
                    tool_calls=[tc_row(subagent_session_id="child")],
                )
            ],
        },
        "child": {
            "meta": {"id": "child", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="c1",
                    content="y",
                    tool_calls=[tc_row(subagent_session_id="grandchild")],
                )
            ],
        },
        "grandchild": {"meta": {"id": "grandchild"}, "rows": []},
    }
    el = ET.fromstring(render_session("parent", runner=fake_daemon(sessions)))
    # Depth 1 expands the child; the grandchild at depth 2 is past the ceiling.
    gc = el.find("assistant/tool-call/subagent/assistant/tool-call/subagent")
    assert gc is not None
    assert gc.attrib == {"id": "grandchild", "omitted": "depth"}


def test_subagent_messages_attribute_omitted_when_count_absent() -> None:
    sessions = {
        "parent": {
            "meta": {"id": "parent", "message_count": 1},
            "rows": [
                assistant_row(
                    ordinal=1,
                    source_uuid="u1",
                    content="x",
                    tool_calls=[tc_row(subagent_session_id="child")],
                )
            ],
        },
        "child": {
            "meta": {"id": "child"},  # no message_count
            "rows": [assistant_row(ordinal=1, source_uuid="c1", content="y")],
        },
    }
    el = ET.fromstring(render_session("parent", runner=fake_daemon(sessions)))
    sub = el.find("assistant/tool-call/subagent")
    assert sub is not None
    assert sub.attrib == {"id": "child"}


# --- the body walk emits abandoned rewind branches --------------------------


def test_render_session_emits_rewound_branch_at_fork_point() -> None:
    # Two assistants share parent u0; the higher-ordinal one (u2) is live, the
    # other (u1) is the abandoned branch, emitted as <rewound-branch> right before
    # the live sibling it was superseded by — here just after u0, which precedes u2.
    sessions = {
        "s1": {
            "meta": {"id": "s1", "message_count": 3},
            "rows": [
                user_row(ordinal=1, source_uuid="u0"),
                assistant_row(
                    ordinal=2,
                    source_uuid="u1",
                    source_parent_uuid="u0",
                    content="first try",
                ),
                assistant_row(
                    ordinal=3,
                    source_uuid="u2",
                    source_parent_uuid="u0",
                    content="second try",
                ),
            ],
        }
    }
    el = ET.fromstring(render_session("s1", runner=fake_daemon(sessions)))
    assert [k.tag for k in el] == ["user", "rewound-branch", "assistant"]
    assert el.find("rewound-branch/assistant").text == "first try"  # type: ignore[union-attr]
    assert el.findall("assistant")[-1].text == "second try"


# --- F1: well-formedness guard ----------------------------------------------


def test_render_session_well_formed_document_passes_through() -> None:
    sessions = {
        "s1": {
            "meta": {"id": "s1", "project": "demo", "message_count": 1},
            "rows": [user_row(ordinal=1, source_uuid="u0")],
        }
    }
    # A normal render is well-formed and must pass the guard (no raise).
    ET.fromstring(render_session("s1", runner=fake_daemon(sessions)))


def test_render_session_raises_on_malformed_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sessions = {
        "s1": {
            "meta": {"id": "s1", "project": "demo", "message_count": 1},
            "rows": [user_row(ordinal=1, source_uuid="u0")],
        }
    }
    # Force a malformed open tag so the assembled document cannot parse; the
    # guard must crash at the source rather than ship malformed XML.
    monkeypatch.setattr(transcript, "render_session_open", lambda meta: "<session>")
    monkeypatch.setattr(transcript, "_render_body", lambda *a, **k: "<user>hi")
    with pytest.raises(ValueError, match="malformed XML"):
        render_session("s1", runner=fake_daemon(sessions))
