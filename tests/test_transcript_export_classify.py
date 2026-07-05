"""Tests for transcript_export.classify — record classification + dedup rule 2.

Fixtures are small hand-authored dicts shaped like the documented `messages`
fields, never trimmed real sessions. Classification keys off
`source_type`/`source_subtype`, so the helper lets `role` and `source_type`
diverge (as they do for the compaction boundary: role=assistant, type=system).
"""

import pytest

from dev_playbook.transcript_export.classify import (
    MessageKind,
    classify,
    collapse_adjacent_repeats,
    keep_messages,
)
from dev_playbook.transcript_export.model import Message, message_from_row


def msg(
    *,
    source_type: str,
    content: str = "hello",
    role: str | None = None,
    source_subtype: str | None = None,
    is_compact_boundary: bool = False,
    source_uuid: str = "u1",
    source_parent_uuid: str | None = None,
    ordinal: int = 0,
    thinking_text: str | None = None,
    tool_calls: list[dict] | None = None,
) -> Message:
    """A message with `source_type`/`content` set; `role` defaults to source_type."""
    raw: dict = {
        "ordinal": ordinal,
        "role": role if role is not None else source_type,
        "source_type": source_type,
        "source_uuid": source_uuid,
        "content": content,
    }
    if source_subtype is not None:
        raw["source_subtype"] = source_subtype
    if is_compact_boundary:
        raw["is_compact_boundary"] = True
    if source_parent_uuid is not None:
        raw["source_parent_uuid"] = source_parent_uuid
    if thinking_text is not None:
        raw["thinking_text"] = thinking_text
    if tool_calls is not None:
        raw["tool_calls"] = tool_calls
    return message_from_row(raw)


def test_normal_user_message_is_user() -> None:
    assert classify(msg(source_type="user", content="hi")) is MessageKind.USER


def test_normal_assistant_message_is_assistant() -> None:
    assert (
        classify(msg(source_type="assistant", content="done")) is MessageKind.ASSISTANT
    )


def test_user_message_starting_with_slash_is_slash_command() -> None:
    m = msg(source_type="user", content="/goal ship it")
    assert classify(m) is MessageKind.SLASH_COMMAND


def test_assistant_message_starting_with_slash_is_still_assistant() -> None:
    # The slash-command refinement applies only to user turns.
    m = msg(source_type="assistant", content="/usr/bin is a path")
    assert classify(m) is MessageKind.ASSISTANT


def test_interrupt_marker_is_interrupt() -> None:
    # Real interrupt rows are source_type="system", source_subtype="interrupted",
    # content="[Request interrupted by user]" (verified live, session 4a157204…).
    # The interrupt must be recognized before the system->DROP rule swallows it.
    m = msg(
        source_type="system",
        source_subtype="interrupted",
        content="[Request interrupted by user]",
    )
    assert classify(m) is MessageKind.INTERRUPT


def test_interrupt_survives_keep_messages() -> None:
    # The real-shaped interrupt (system-typed) must not be dropped by keep_messages,
    # else no <interrupted/> ever renders.
    m = msg(
        source_type="system",
        source_subtype="interrupted",
        content="[Request interrupted by user]",
    )
    assert keep_messages([m]) == [m]


def test_compaction_boundary_is_compaction_despite_system_type_and_assistant_role() -> (
    None
):
    # The headline reason classification keys off source_type, not role: this row
    # is role=assistant, source_type=system, and must be COMPACTION (kept), not an
    # assistant turn and not dropped as system plumbing.
    m = msg(
        source_type="system",
        role="assistant",
        source_subtype="compact_boundary",
        content="summary of the conversation so far",
    )
    assert classify(m) is MessageKind.COMPACTION


def test_compaction_via_is_compact_boundary_flag() -> None:
    m = msg(
        source_type="system",
        role="assistant",
        is_compact_boundary=True,
        content="summary",
    )
    assert classify(m) is MessageKind.COMPACTION


def test_task_notification_system_message_is_dropped() -> None:
    m = msg(
        source_type="system",
        role="assistant",
        source_subtype="task_notification",
        content="sub-agent finished",
    )
    assert classify(m) is MessageKind.DROP


def test_queued_command_preview_is_dropped() -> None:
    # The queued_command preview (a user-typed prompt recorded while the assistant
    # is still working) carries no source_uuid and is re-emitted later as a real
    # user message, so we drop the orphan preview.
    m = msg(source_type="user", source_subtype="queued_command", content="do it")
    assert classify(m) is MessageKind.DROP


def test_keep_messages_drops_queued_command_preview() -> None:
    msgs = [
        msg(source_type="user", content="real", source_uuid="u1", ordinal=0),
        msg(
            source_type="user",
            source_subtype="queued_command",
            content="queued preview",
            source_uuid="u2",
            ordinal=1,
        ),
        msg(source_type="assistant", content="reply", source_uuid="u3", ordinal=2),
    ]

    kept = keep_messages(msgs)

    assert [m.source_uuid for m in kept] == ["u1", "u3"]


def test_unexpected_source_type_fails_loud() -> None:
    with pytest.raises(ValueError, match="unclassifiable"):
        classify(msg(source_type="tool", content="x"))


def test_adjacent_repeat_with_different_uuid_is_collapsed() -> None:
    # An injection double re-emits a real message with a *different* source_uuid,
    # so rule 1 misses it; rule 2 collapses the adjacent same-role same-content pair.
    a = msg(source_type="user", content="run it", source_uuid="u1", ordinal=0)
    dup = msg(source_type="user", content="run it", source_uuid="u2", ordinal=1)

    kept = collapse_adjacent_repeats([a, dup])

    assert [m.source_uuid for m in kept] == ["u1"]


def test_fork_siblings_differ_in_content_and_survive() -> None:
    a = msg(source_type="assistant", content="branch A", source_uuid="a", ordinal=5)
    b = msg(source_type="assistant", content="branch B", source_uuid="b", ordinal=6)

    kept = collapse_adjacent_repeats([a, b])

    assert [m.source_uuid for m in kept] == ["a", "b"]


def test_non_adjacent_repeat_is_kept() -> None:
    # Only the immediate predecessor is compared, so A, B, A keeps both A's.
    a = msg(source_type="user", content="x", source_uuid="u1", ordinal=0)
    b = msg(source_type="assistant", content="y", source_uuid="u2", ordinal=1)
    a2 = msg(source_type="user", content="x", source_uuid="u3", ordinal=2)

    kept = collapse_adjacent_repeats([a, b, a2])

    assert [m.source_uuid for m in kept] == ["u1", "u2", "u3"]


def _tc(*, tool_use_id: str, result_content: str) -> dict:
    return {
        "tool_name": "Bash",
        "tool_use_id": tool_use_id,
        "input_json": "{}",
        "result_content": result_content,
        "result_content_length": len(result_content),
    }


def test_real_triple_emission_collapses_to_one() -> None:
    # The re-emitted queued/injection double shares every distinguishing field
    # (content, tool_calls + their results, thinking, source_parent_uuid) and only
    # differs in source_uuid, so the whole adjacent run collapses to one.
    rows = [
        msg(
            source_type="user",
            content="retry",
            source_uuid=f"u{i}",
            source_parent_uuid="p1",
            ordinal=i,
        )
        for i in range(3)
    ]

    kept = collapse_adjacent_repeats(rows)

    assert [m.source_uuid for m in kept] == ["u0"]


def test_same_prose_different_tool_result_is_preserved() -> None:
    # A fail-then-pass retry: identical prose, but the tool result differs, so the
    # turns are genuinely distinct and must both survive.
    fail = msg(
        source_type="assistant",
        content="running tests",
        source_uuid="a1",
        ordinal=0,
        tool_calls=[_tc(tool_use_id="t1", result_content="FAILED")],
    )
    ok = msg(
        source_type="assistant",
        content="running tests",
        source_uuid="a2",
        ordinal=1,
        tool_calls=[_tc(tool_use_id="t2", result_content="PASSED")],
    )

    kept = collapse_adjacent_repeats([fail, ok])

    assert [m.source_uuid for m in kept] == ["a1", "a2"]


def test_same_content_different_role_is_not_collapsed() -> None:
    u = msg(source_type="user", content="hello", source_uuid="u1", ordinal=0)
    a = msg(source_type="assistant", content="hello", source_uuid="u2", ordinal=1)

    kept = collapse_adjacent_repeats([u, a])

    assert [m.source_uuid for m in kept] == ["u1", "u2"]


def test_keep_messages_drops_plumbing_then_dedups() -> None:
    # Removing the wedged task_notification makes the two "hi" turns adjacent, so
    # dedup rule 2 then collapses them — drop must run before dedup.
    msgs = [
        msg(source_type="user", content="hi", source_uuid="u1", ordinal=0),
        msg(
            source_type="system",
            role="assistant",
            source_subtype="task_notification",
            content="noise",
            source_uuid="u2",
            ordinal=1,
        ),
        msg(source_type="user", content="hi", source_uuid="u3", ordinal=2),
    ]

    kept = keep_messages(msgs)

    assert [m.source_uuid for m in kept] == ["u1"]


def test_keep_messages_preserves_compaction_and_order() -> None:
    msgs = [
        msg(source_type="user", content="start", source_uuid="u1", ordinal=0),
        msg(
            source_type="system",
            role="assistant",
            source_subtype="compact_boundary",
            content="summary",
            source_uuid="u2",
            ordinal=1,
        ),
        msg(source_type="assistant", content="continue", source_uuid="u3", ordinal=2),
    ]

    kept = keep_messages(msgs)

    # The compaction summary is system-typed but kept, and order is preserved.
    assert [m.source_uuid for m in kept] == ["u1", "u2", "u3"]
