"""Per-message classification plus the keep/drop and adjacent-repeat dedup pass.

Classification keys off `source_type`/`source_subtype`, never `role`: a
compaction boundary is `role=assistant` but `source_type=system`, so a role-based
split would mistake the summary for an ordinary assistant turn (and a
system->drop check keyed off role would never fire). Each message resolves to one
`MessageKind`; the harness plumbing we don't want (`source_type=system` other
than the compaction summary, e.g. sub-agent `task_notification` notices) becomes
`DROP`.

`keep_messages` applies the Design's keep/drop policy: drop every `DROP` message,
then collapse adjacent repeats (dedup rule 2). Rule 1 (verbatim resume
re-emissions, keyed on `source_uuid`) runs upstream in `normalize_messages`; rule
2 catches queued-prompt / injection doubles, which re-emit a real message with a
*different* `source_uuid` and so slip past rule 1. See PLAN.md for the
authoritative design.
"""

from enum import Enum

from transcript_export.model import Message

INTERRUPT_MARKER = "[Request interrupted by user]"


class MessageKind(Enum):
    """What a message is, for rendering and the keep/drop policy.

    `DROP` marks harness plumbing to omit; every other kind is kept and rendered.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SLASH_COMMAND = "slash_command"
    INTERRUPT = "interrupt"
    COMPACTION = "compaction"
    DROP = "drop"


def classify(message: Message) -> MessageKind:
    """Resolve one message to its `MessageKind`, keyed off source_type/subtype.

    Order matters: both the compaction boundary and an interrupt arrive as
    `source_type=system` but are kept, so they are recognized before the
    system->drop rule swallows them. A real interrupt is `source_type=system`,
    `source_subtype="interrupted"`, `content="[Request interrupted by user]"`.
    Slash command is a content refinement on a user turn. An unexpected `source_type`
    (not user/assistant/system) fails loud rather than being silently dropped.

    A `queued_command` preview (a user-typed prompt the harness records while the
    assistant is still working, before re-emitting it as a real user message with
    a `source_uuid` and parent linkage) is dropped: it carries no `source_uuid`,
    so keeping it would orphan it from the fork tree, and the real re-emission
    survives to connect the live path.
    """
    if message.is_compact_boundary or message.source_subtype == "compact_boundary":
        return MessageKind.COMPACTION
    if message.source_subtype == "interrupted" or message.content == INTERRUPT_MARKER:
        return MessageKind.INTERRUPT
    if message.source_subtype == "queued_command":
        return MessageKind.DROP
    if message.source_type == "system":
        return MessageKind.DROP
    if message.source_type == "user":
        if message.content.startswith("/"):
            return MessageKind.SLASH_COMMAND
        return MessageKind.USER
    if message.source_type == "assistant":
        return MessageKind.ASSISTANT
    raise ValueError(
        f"unclassifiable message at ordinal {message.ordinal}: "
        f"source_type={message.source_type!r} source_subtype={message.source_subtype!r}"
    )


def collapse_adjacent_repeats(messages: list[Message]) -> list[Message]:
    """Dedup rule 2: drop a message that exactly repeats the previous kept one.

    Queued-prompt / injection doubles re-emit a real message with a *different*
    `source_uuid`, so the resume dedup (rule 1) misses them; here we collapse a
    message that matches the immediately preceding kept message on both `role` and
    `content`. Fork siblings differ in content, so they are never collapsed; a
    non-adjacent repeat (A, B, A) is kept because only the immediate predecessor
    is compared.
    """
    kept: list[Message] = []
    for message in messages:
        previous = kept[-1] if kept else None
        if (
            previous is not None
            and previous.role == message.role
            and previous.content == message.content
        ):
            continue
        kept.append(message)
    return kept


def keep_messages(messages: list[Message]) -> list[Message]:
    """Apply the keep/drop policy: drop plumbing, then collapse adjacent repeats.

    Expects the resume-deduped list from `normalize_messages` (rule 1 already
    applied). Drops every `DROP`-classified message, then runs dedup rule 2 over
    the survivors, in that order — a plumbing message wedged between two copies of
    a real message must be removed first so the copies become adjacent. Input
    order is preserved; classify each survivor with `classify` at render time.
    """
    survivors = [m for m in messages if classify(m) is not MessageKind.DROP]
    return collapse_adjacent_repeats(survivors)
