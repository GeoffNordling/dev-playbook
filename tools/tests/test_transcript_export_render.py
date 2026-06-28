"""Tests for transcript_export.render — header, turns, thinking, escaping.

Fixtures are small hand-authored dicts shaped like the documented `session get`
and `session messages` fields, never trimmed real sessions. Every rendered turn
is also parsed with ElementTree to assert it is well-formed XML.
"""

import xml.etree.ElementTree as ET

import pytest

from transcript_export.classify import MessageKind, classify
from transcript_export.forks import MessageNode
from transcript_export.model import Message, ToolCall, message_from_row
from transcript_export.render import (
    escape,
    render_compaction,
    render_interrupted,
    render_message,
    render_rewound_branch,
    render_session_open,
    render_tool_call,
    render_turn,
    strip_tool_markers,
)


def msg(
    *,
    source_type: str,
    content: str = "hello",
    role: str | None = None,
    source_subtype: str | None = None,
    is_compact_boundary: bool = False,
    model: str | None = None,
    thinking_text: str | None = None,
    ordinal: int = 0,
    tool_calls: list[dict] | None = None,
) -> Message:
    """A message with the fields a turn needs; `role` defaults to source_type."""
    raw: dict = {
        "ordinal": ordinal,
        "role": role if role is not None else source_type,
        "source_type": source_type,
        "source_uuid": "u1",
        "content": content,
    }
    if source_subtype is not None:
        raw["source_subtype"] = source_subtype
    if is_compact_boundary:
        raw["is_compact_boundary"] = True
    if model is not None:
        raw["model"] = model
    if thinking_text is not None:
        raw["thinking_text"] = thinking_text
    if tool_calls is not None:
        raw["tool_calls"] = tool_calls
    return message_from_row(raw)


def tc(
    *,
    tool_name: str = "Bash",
    tool_use_id: str = "toolu_1",
    input_json: str = "{}",
    result_content: str = "",
    result_content_length: int | None = None,
) -> ToolCall:
    """A ToolCall fixture; `result_content_length` defaults to the body length."""
    raw: dict = {
        "tool_name": tool_name,
        "tool_use_id": tool_use_id,
        "input_json": input_json,
        "result_content": result_content,
        "result_content_length": (
            result_content_length
            if result_content_length is not None
            else len(result_content)
        ),
    }
    return message_from_row(
        {
            "ordinal": 0,
            "role": "assistant",
            "source_type": "assistant",
            "source_uuid": "u1",
            "content": "",
            "tool_calls": [raw],
        }
    ).tool_calls[0]


# --- escape -----------------------------------------------------------------


def test_escape_covers_all_five_entities() -> None:
    assert escape("""<a> & "b" 'c'""") == "&lt;a&gt; &amp; &quot;b&quot; &apos;c&apos;"


def test_escape_does_not_double_escape_ampersand() -> None:
    # `&` must be replaced first; otherwise the `&` in `&lt;` would re-escape.
    assert escape("a < b") == "a &lt; b"
    assert escape("&amp;") == "&amp;amp;"


def test_escape_strips_xml_illegal_control_characters() -> None:
    # Only the C0 control bytes XML 1.0 forbids are removed (the bare ESC 0x1b
    # that opens an ANSI sequence, plus BEL and NUL); the printable `[31m` tail of
    # the sequence is valid text and survives.
    assert escape("red\x1b[31mtext\x07\x00end") == "red[31mtextend"


def test_escape_keeps_tab_newline_and_carriage_return() -> None:
    # The three whitespace controls XML 1.0 allows must survive.
    assert escape("a\tb\nc\rd") == "a\tb\nc\rd"


def test_render_turn_with_ansi_output_is_well_formed_xml() -> None:
    # A turn whose tool output contains a raw ESC must still parse: the stripping
    # happens before entity-escaping, so the document stays well-formed.
    m = msg(
        source_type="assistant",
        content="ran it",
        model="claude-opus-4-8",
        tool_calls=[
            {
                "tool_name": "Bash",
                "tool_use_id": "toolu_1",
                "input_json": "{}",
                "result_content": "\x1b[1;31mError\x1b[0m: boom",
                "result_content_length": 20,
            }
        ],
    )

    out = render_turn(m)
    el = ET.fromstring(out)

    assert el.find("tool-call/output").text == "[1;31mError[0m: boom"  # type: ignore[union-attr]


# --- header -----------------------------------------------------------------


def full_meta() -> dict:
    return {
        "id": "sess-1",
        "project": "dev_playbook",
        "agent": "claude",
        "git_branch": "main",
        "cwd": "/home/x",
        "started_at": "2026-06-27T19:06:07Z",
        "ended_at": "2026-06-28T00:50:22Z",
        "message_count": 207,
        "compaction_count": 1,
    }


def test_header_maps_every_field_to_its_attribute() -> None:
    open_tag = render_session_open(full_meta())
    el = ET.fromstring(open_tag + "</session>")
    assert el.tag == "session"
    assert el.attrib == {
        "id": "sess-1",
        "project": "dev_playbook",
        "agent": "claude",
        "branch": "main",
        "cwd": "/home/x",
        "started": "2026-06-27T19:06:07Z",
        "ended": "2026-06-28T00:50:22Z",
        "messages": "207",
        "compactions": "1",
    }


def test_header_omits_missing_optional_attributes() -> None:
    el = ET.fromstring(render_session_open({"id": "s", "project": "p"}) + "</session>")
    assert el.attrib == {"id": "s", "project": "p"}
    assert "branch" not in el.attrib
    assert "ended" not in el.attrib


def test_header_keeps_zero_counts() -> None:
    # A zero count is meaningful (kept on `is None`, not falsiness).
    el = ET.fromstring(
        render_session_open({"id": "s", "message_count": 0, "compaction_count": 0})
        + "</session>"
    )
    assert el.attrib["messages"] == "0"
    assert el.attrib["compactions"] == "0"


def test_header_requires_id() -> None:
    with pytest.raises(ValueError, match="missing required 'id'"):
        render_session_open({"project": "p"})


def test_header_escapes_attribute_values() -> None:
    el = ET.fromstring(
        render_session_open({"id": "s", "cwd": '/a&b/"c"'}) + "</session>"
    )
    assert el.attrib["cwd"] == '/a&b/"c"'


# --- user turns -------------------------------------------------------------


def test_user_turn_renders_ord_and_text() -> None:
    el = ET.fromstring(render_turn(msg(source_type="user", content="hi", ordinal=3)))
    assert el.tag == "user"
    assert el.attrib == {"ord": "3"}
    assert el.text == "hi"


def test_user_turn_escapes_xml_looking_content() -> None:
    raw = 'if a < b && c > d then say "go"'
    out = render_turn(msg(source_type="user", content=raw, ordinal=1))
    # Round-trips: the literal text survives escaping + parsing unchanged.
    assert ET.fromstring(out).text == raw
    assert "<b" not in out.replace("</", "")  # the literal `<` was escaped


# --- slash commands ---------------------------------------------------------


def test_slash_command_splits_command_and_args() -> None:
    el = ET.fromstring(
        render_turn(msg(source_type="user", content="/goal ship it now", ordinal=4))
    )
    assert el.tag == "user"
    assert el.attrib == {"ord": "4", "command": "/goal"}
    assert el.text == "ship it now"


def test_slash_command_with_no_args_has_empty_text() -> None:
    el = ET.fromstring(render_turn(msg(source_type="user", content="/clear")))
    assert el.attrib["command"] == "/clear"
    assert (el.text or "") == ""


# --- assistant turns --------------------------------------------------------


def test_assistant_turn_with_model_thinking_and_prose() -> None:
    out = render_turn(
        msg(
            source_type="assistant",
            content="here is the answer",
            model="claude-opus-4-8",
            thinking_text="let me reason",
            ordinal=5,
        )
    )
    el = ET.fromstring(out)
    assert el.tag == "assistant"
    assert el.attrib == {"ord": "5", "model": "claude-opus-4-8"}
    thinking = el.find("thinking")
    assert thinking is not None and thinking.text == "let me reason"
    # Thinking precedes the prose, which is the assistant element's tail text.
    assert thinking.tail == "here is the answer"


def test_assistant_turn_without_thinking_has_no_thinking_child() -> None:
    el = ET.fromstring(
        render_turn(msg(source_type="assistant", content="done", model="m", ordinal=2))
    )
    assert el.find("thinking") is None
    assert el.text == "done"


def test_assistant_turn_without_model_omits_model_attribute() -> None:
    el = ET.fromstring(render_turn(msg(source_type="assistant", content="x")))
    assert "model" not in el.attrib


def test_assistant_turn_escapes_thinking_and_prose() -> None:
    out = render_turn(
        msg(
            source_type="assistant",
            content="a > b",
            thinking_text="x < y & z",
            model="m",
        )
    )
    el = ET.fromstring(out)
    assert el.find("thinking").text == "x < y & z"  # type: ignore[union-attr]
    assert el.find("thinking").tail == "a > b"  # type: ignore[union-attr]


# --- non-turn messages fail loud --------------------------------------------


def test_render_turn_rejects_compaction() -> None:
    m = msg(source_type="system", source_subtype="compact_boundary", content="summary")
    assert classify(m) is MessageKind.COMPACTION
    with pytest.raises(ValueError, match="non-turn message"):
        render_turn(m)


def test_render_turn_rejects_interrupt() -> None:
    m = msg(
        source_type="system",
        source_subtype="interrupted",
        content="[Request interrupted by user]",
    )
    with pytest.raises(ValueError, match="non-turn message"):
        render_turn(m)


# --- marker stripping -------------------------------------------------------


def test_strip_markers_removes_bash_marker_and_command_line() -> None:
    content = (
        "I'll list the worktrees.\n[Bash: List git worktrees]\n$ git worktree list"
    )
    assert strip_tool_markers(content, 1) == "I'll list the worktrees."


def test_strip_markers_keeps_multiline_command_in_block() -> None:
    # A bash command can span several lines; the whole trailing block goes.
    content = 'Merging now.\n[Bash: Merge main]\n$ DP=/home/x\ngit -C "$DP" merge main'
    assert strip_tool_markers(content, 1) == "Merging now."


def test_strip_markers_with_no_prose_yields_empty() -> None:
    content = "[Read: /a/b.py]"
    assert strip_tool_markers(content, 1) == ""


def test_strip_markers_handles_parallel_tool_calls() -> None:
    content = "Reading both.\n[Read: /a]\n[Read: /b]"
    assert strip_tool_markers(content, 2) == "Reading both."


def test_strip_markers_noop_without_tool_calls() -> None:
    content = "Just prose, no [brackets: here] stripped."
    assert strip_tool_markers(content, 0) == content


def test_strip_markers_leaves_prose_when_fewer_markers_than_calls() -> None:
    # Defensive: never eat prose if the marker count is unexpectedly low.
    content = "Some prose with no markers."
    assert strip_tool_markers(content, 1) == content


def test_render_turn_strips_markers_from_assistant_prose() -> None:
    m = msg(
        source_type="assistant",
        content="Running the build.\n[Bash: run build]\n$ make build",
        model="m",
        tool_calls=[{"tool_name": "Bash", "tool_use_id": "t1", "input_json": "{}"}],
    )
    el = ET.fromstring(render_turn(m))
    assert el.text == "Running the build."


# --- tool-call rendering ----------------------------------------------------


def test_tool_call_renders_name_id_args_and_output() -> None:
    el = ET.fromstring(
        render_tool_call(
            tc(
                tool_name="Bash",
                tool_use_id="toolu_abc",
                input_json='{"command": "ls"}',
                result_content="file1\nfile2",
            )
        )
    )
    assert el.tag == "tool-call"
    assert el.attrib["name"] == "Bash"
    assert el.attrib["id"] == "toolu_abc"
    assert "outcome" not in el.attrib
    assert el.find("args").text == '{"command": "ls"}'  # type: ignore[union-attr]
    out = el.find("output")
    assert out is not None
    assert out.text == "file1\nfile2"
    assert out.attrib == {"chars": "11", "truncated": "false"}


def test_tool_call_escapes_args_and_output() -> None:
    el = ET.fromstring(
        render_tool_call(
            tc(input_json='{"q": "a < b & c"}', result_content="x > y & <z>")
        )
    )
    assert el.find("args").text == '{"q": "a < b & c"}'  # type: ignore[union-attr]
    assert el.find("output").text == "x > y & <z>"  # type: ignore[union-attr]


def test_tool_call_truncates_long_output_at_2000() -> None:
    body = "z" * 2500
    el = ET.fromstring(render_tool_call(tc(result_content=body)))
    out = el.find("output")
    assert out is not None
    assert out.attrib["truncated"] == "true"
    assert out.attrib["chars"] == "2500"
    assert len(out.text or "") == 2000


def test_tool_call_empty_read_output_reports_full_length() -> None:
    # Read/ToolSearch bodies come back empty; chars still reports the real size.
    el = ET.fromstring(
        render_tool_call(
            tc(tool_name="Read", result_content="", result_content_length=8421)
        )
    )
    out = el.find("output")
    assert out is not None
    assert (out.text or "") == ""
    assert out.attrib == {"chars": "8421", "truncated": "false"}


def test_tool_call_marks_rejected_outcome() -> None:
    el = ET.fromstring(
        render_tool_call(
            tc(result_content="The user doesn't want to proceed with this tool use.")
        )
    )
    assert el.attrib["outcome"] == "rejected"


def test_tool_call_marks_error_outcome() -> None:
    el = ET.fromstring(
        render_tool_call(
            tc(
                result_content="<tool_use_error>File has not been read yet.</tool_use_error>"
            )
        )
    )
    assert el.attrib["outcome"] == "error"


def test_assistant_turn_embeds_tool_calls_after_prose() -> None:
    m = msg(
        source_type="assistant",
        content="Listing files.\n[Bash: list]\n$ ls",
        model="m",
        ordinal=7,
        tool_calls=[
            {
                "tool_name": "Bash",
                "tool_use_id": "toolu_x",
                "input_json": '{"command": "ls"}',
                "result_content": "a\nb",
            }
        ],
    )
    el = ET.fromstring(render_turn(m))
    assert el.text == "Listing files."
    call = el.find("tool-call")
    assert call is not None
    assert call.attrib["name"] == "Bash"
    assert call.find("output").text == "a\nb"  # type: ignore[union-attr]


# --- timeline markers -------------------------------------------------------


def test_render_compaction_emits_escaped_summary() -> None:
    m = msg(
        source_type="system",
        source_subtype="compact_boundary",
        content="Summary: a < b & more",
    )
    assert classify(m) is MessageKind.COMPACTION
    el = ET.fromstring(render_compaction(m))
    assert el.tag == "compaction"
    assert not el.attrib
    assert el.text == "Summary: a < b & more"


def test_render_compaction_rejects_non_compaction() -> None:
    with pytest.raises(ValueError, match="non-compaction"):
        render_compaction(msg(source_type="user", content="hi"))


def test_render_interrupted_emits_self_closing_with_ord() -> None:
    m = msg(
        source_type="system",
        source_subtype="interrupted",
        content="[Request interrupted by user]",
        ordinal=12,
    )
    assert classify(m) is MessageKind.INTERRUPT
    el = ET.fromstring(render_interrupted(m))
    assert el.tag == "interrupted"
    assert el.attrib == {"ord": "12"}
    assert (el.text or "") == ""


def test_render_interrupted_rejects_non_interrupt() -> None:
    with pytest.raises(ValueError, match="non-interrupt"):
        render_interrupted(msg(source_type="user", content="not an interrupt"))


# --- message dispatch -------------------------------------------------------


def test_render_message_dispatches_turn() -> None:
    el = ET.fromstring(render_message(msg(source_type="user", content="hi", ordinal=1)))
    assert el.tag == "user"


def test_render_message_dispatches_compaction() -> None:
    m = msg(source_type="system", source_subtype="compact_boundary", content="s")
    assert ET.fromstring(render_message(m)).tag == "compaction"


def test_render_message_dispatches_interrupt() -> None:
    m = msg(
        source_type="system",
        source_subtype="interrupted",
        content="[Request interrupted by user]",
        ordinal=3,
    )
    assert ET.fromstring(render_message(m)).tag == "interrupted"


def test_render_message_drops_plumbing_to_empty() -> None:
    m = msg(source_type="system", source_subtype="task_notification", content="notice")
    assert classify(m) is MessageKind.DROP
    assert render_message(m) == ""


# --- rewound branches -------------------------------------------------------


def node(message: Message, *children: MessageNode) -> MessageNode:
    """A MessageNode with its (already ordinal-sorted) children."""
    return MessageNode(message, tuple(children))


def test_rewound_branch_renders_linear_chain_in_order() -> None:
    chain = node(
        msg(source_type="user", content="ask", ordinal=1),
        node(msg(source_type="assistant", content="answer", model="m", ordinal=2)),
    )
    el = ET.fromstring(render_rewound_branch(chain))
    assert el.tag == "rewound-branch"
    kids = list(el)
    assert [k.tag for k in kids] == ["user", "assistant"]
    assert kids[0].text == "ask"
    assert kids[1].text == "answer"


def test_rewound_branch_nests_inner_fork_as_rewound_branch() -> None:
    # The abandoned branch root itself forks: the lower-ordinal child (branch-x)
    # nests as its own <rewound-branch>; the highest-ordinal child continues inline.
    inner = node(
        msg(source_type="user", content="root", ordinal=1),
        node(msg(source_type="assistant", content="branch-x", model="m", ordinal=5)),
        node(msg(source_type="assistant", content="branch-y", model="m", ordinal=9)),
    )
    el = ET.fromstring(render_rewound_branch(inner))
    kids = list(el)
    assert [k.tag for k in kids] == ["user", "rewound-branch", "assistant"]
    assert kids[0].text == "root"
    assert list(kids[1])[0].text == "branch-x"
    assert kids[2].text == "branch-y"


def test_rewound_branch_skips_dropped_plumbing() -> None:
    # A task_notification wedged into the abandoned chain renders to nothing.
    chain = node(
        msg(source_type="user", content="ask", ordinal=1),
        node(
            msg(
                source_type="system",
                source_subtype="task_notification",
                content="notice",
                ordinal=2,
            ),
            node(msg(source_type="assistant", content="answer", model="m", ordinal=3)),
        ),
    )
    el = ET.fromstring(render_rewound_branch(chain))
    assert [k.tag for k in el] == ["user", "assistant"]


def test_rewound_branch_renders_marker_in_full_fidelity() -> None:
    # Full fidelity: a compaction inside an abandoned branch still renders.
    chain = node(
        msg(source_type="user", content="ask", ordinal=1),
        node(
            msg(
                source_type="system",
                source_subtype="compact_boundary",
                content="summary",
                ordinal=2,
            )
        ),
    )
    el = ET.fromstring(render_rewound_branch(chain))
    assert [k.tag for k in el] == ["user", "compaction"]
    assert list(el)[1].text == "summary"
