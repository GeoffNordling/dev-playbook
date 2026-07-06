"""Tests for transcript_export.model — normalization and resume dedup.

Fixtures are small hand-authored dicts shaped like the documented `messages` /
`tool_calls` fields, never trimmed real sessions.
"""

from dev_playbook.transcript_export.model import (
    Message,
    ToolCall,
    collapse_resume_duplicates,
    message_from_row,
    normalize_messages,
)


def row(
    *,
    ordinal: int,
    source_uuid: str,
    role: str = "user",
    content: str = "hi",
    **extra: object,
) -> dict:
    """A minimal `session messages` row with the always-present fields set."""
    return {
        "ordinal": ordinal,
        "role": role,
        "source_type": role,
        "source_uuid": source_uuid,
        "content": content,
        **extra,
    }


def test_message_from_row_maps_documented_fields() -> None:
    raw = row(
        ordinal=7,
        source_uuid="u1",
        role="assistant",
        content="done",
        source_subtype="compact_boundary",
        is_system=True,
        is_compact_boundary=True,
        source_parent_uuid="p1",
        model="claude-opus-4-8",
        thinking_text="let me think",
    )

    msg = message_from_row(raw)

    assert msg == Message(
        ordinal=7,
        role="assistant",
        source_type="assistant",
        source_subtype="compact_boundary",
        is_system=True,
        is_compact_boundary=True,
        source_uuid="u1",
        source_parent_uuid="p1",
        model="claude-opus-4-8",
        thinking_text="let me think",
        content="done",
        tool_calls=(),
    )


def test_optional_fields_default_when_absent() -> None:
    msg = message_from_row(row(ordinal=0, source_uuid="u1"))

    assert msg.source_subtype is None
    assert msg.source_parent_uuid is None
    assert msg.model is None
    assert msg.thinking_text is None
    assert msg.is_system is False
    assert msg.is_compact_boundary is False
    assert msg.tool_calls == ()


def test_tool_calls_are_normalized() -> None:
    raw = row(
        ordinal=3,
        source_uuid="u1",
        role="assistant",
        content="running",
        tool_calls=[
            {
                "tool_name": "Bash",
                "category": "execution",
                "tool_use_id": "toolu_a",
                "input_json": '{"command": "ls"}',
                "skill_name": None,
                "subagent_session_id": None,
                "result_content": "file.txt",
                "result_content_length": 8,
            }
        ],
    )

    (call,) = message_from_row(raw).tool_calls

    assert call == ToolCall(
        tool_name="Bash",
        category="execution",
        tool_use_id="toolu_a",
        input_json='{"command": "ls"}',
        skill_name=None,
        subagent_session_id=None,
        result_content="file.txt",
        result_content_length=8,
    )


def test_tool_call_optional_fields_default() -> None:
    raw = row(
        ordinal=3,
        source_uuid="u1",
        role="assistant",
        tool_calls=[
            {
                "tool_name": "Read",
                "tool_use_id": "toolu_b",
                "input_json": "{}",
                "result_content_length": 4000,
            }
        ],
    )

    (call,) = message_from_row(raw).tool_calls

    # Read returns length-only: the body is empty, category/skill/subagent absent.
    assert call.category is None
    assert call.skill_name is None
    assert call.subagent_session_id is None
    assert call.result_content == ""
    assert call.result_content_length == 4000


def test_collapse_resume_duplicates_keeps_first_per_source_uuid() -> None:
    first = message_from_row(row(ordinal=0, source_uuid="u1", content="original"))
    other = message_from_row(row(ordinal=1, source_uuid="u2", content="second"))
    # A resume re-emits u1 verbatim with the same source_uuid at a later ordinal.
    replay = message_from_row(row(ordinal=9, source_uuid="u1", content="original"))

    kept = collapse_resume_duplicates([first, other, replay])

    assert [m.source_uuid for m in kept] == ["u1", "u2"]
    assert kept[0].ordinal == 0


def test_fork_siblings_survive_resume_dedup() -> None:
    # A fork shares a parent but carries a different source_uuid and content, so
    # rule 1 must keep both branch heads (collapsing forks is not its job).
    a = message_from_row(
        row(ordinal=5, source_uuid="a", source_parent_uuid="p", content="branch A")
    )
    b = message_from_row(
        row(ordinal=6, source_uuid="b", source_parent_uuid="p", content="branch B")
    )

    kept = collapse_resume_duplicates([a, b])

    assert [m.source_uuid for m in kept] == ["a", "b"]


def test_queued_command_row_has_no_source_uuid() -> None:
    # A live `queued_command` preview row omits source_uuid entirely; the model
    # must tolerate that (None) rather than KeyError on a hard index.
    raw = {
        "ordinal": 46,
        "role": "user",
        "source_type": "user",
        "source_subtype": "queued_command",
        "content": "do the thing",
    }

    msg = message_from_row(raw)

    assert msg.source_uuid is None
    assert msg.source_subtype == "queued_command"


def test_collapse_resume_duplicates_keeps_every_uuidless_row() -> None:
    # A uuid-less row can never be a resume re-emission (those are matched by
    # source_uuid), so two distinct uuid-less previews must both survive rule 1 —
    # collapsing them on a shared None key would wrongly merge separate prompts.
    a = message_from_row(
        {"ordinal": 1, "role": "user", "source_type": "user", "content": "first"}
    )
    b = message_from_row(
        {"ordinal": 2, "role": "user", "source_type": "user", "content": "second"}
    )

    kept = collapse_resume_duplicates([a, b])

    assert [m.content for m in kept] == ["first", "second"]


def test_normalize_messages_preserves_order_and_dedups() -> None:
    rows = [
        row(ordinal=0, source_uuid="u1", content="a"),
        row(ordinal=1, source_uuid="u2", content="b"),
        row(ordinal=2, source_uuid="u1", content="a"),
        row(ordinal=3, source_uuid="u3", content="c"),
    ]

    result = normalize_messages(rows)

    assert [m.source_uuid for m in result] == ["u1", "u2", "u3"]
    assert [m.ordinal for m in result] == [0, 1, 3]
    assert all(isinstance(m, Message) for m in result)
