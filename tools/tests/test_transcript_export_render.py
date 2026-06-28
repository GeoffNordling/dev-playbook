"""Tests for transcript_export.render — header, turns, thinking, escaping.

Fixtures are small hand-authored dicts shaped like the documented `session get`
and `session messages` fields, never trimmed real sessions. Every rendered turn
is also parsed with ElementTree to assert it is well-formed XML.
"""

import xml.etree.ElementTree as ET

import pytest

from transcript_export.classify import MessageKind, classify
from transcript_export.model import Message, message_from_row
from transcript_export.render import escape, render_session_open, render_turn


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
    return message_from_row(raw)


# --- escape -----------------------------------------------------------------


def test_escape_covers_all_five_entities() -> None:
    assert escape("""<a> & "b" 'c'""") == "&lt;a&gt; &amp; &quot;b&quot; &apos;c&apos;"


def test_escape_does_not_double_escape_ampersand() -> None:
    # `&` must be replaced first; otherwise the `&` in `&lt;` would re-escape.
    assert escape("a < b") == "a &lt; b"
    assert escape("&amp;") == "&amp;amp;"


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
    m = msg(source_type="user", content="[Request interrupted by user]")
    with pytest.raises(ValueError, match="non-turn message"):
        render_turn(m)
