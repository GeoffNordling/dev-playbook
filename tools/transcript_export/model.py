"""The normalized message model and resume dedup.

Turns the raw dicts that `client.session_messages` returns into typed `Message`
records (each carrying its `ToolCall` children), then collapses the verbatim
re-emissions a resumed session produces. A resume replays earlier messages with
the *same* `source_uuid`, so keeping the first occurrence per `source_uuid` drops
the duplicates while leaving genuine forks (same parent, *different*
`source_uuid`) untouched. The adjacent-repeat dedup (rule 2) and fork
reconstruction land in later tasks; see PLAN.md for the authoritative design.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolCall:
    """One tool use parsed from a message's `tool_calls[]` entry.

    `result_content` is the output body (empty for Read/ToolSearch, which the
    messages API returns length-only); `subagent_session_id` is set when the call
    spawned a sub-agent.
    """

    tool_name: str
    category: str | None
    tool_use_id: str
    input_json: str
    skill_name: str | None
    subagent_session_id: str | None
    result_content: str
    result_content_length: int


@dataclass(frozen=True)
class Message:
    """One normalized message row from the AgentsView messages API.

    Classification keys off `source_type`/`source_subtype` (not `role`): the
    compaction boundary is `role=assistant` but `source_type=system`. `ordinal`
    is a sparse global index; `source_parent_uuid` is None for a message with no
    parent (the field is absent in the raw row).
    """

    ordinal: int
    role: str
    source_type: str
    source_subtype: str | None
    is_system: bool
    is_compact_boundary: bool
    source_uuid: str
    source_parent_uuid: str | None
    model: str | None
    thinking_text: str | None
    content: str
    tool_calls: tuple[ToolCall, ...]


def tool_call_from_row(raw: dict) -> ToolCall:
    """Normalize one raw `tool_calls[]` entry into a ToolCall."""
    return ToolCall(
        tool_name=raw["tool_name"],
        category=raw.get("category"),
        tool_use_id=raw["tool_use_id"],
        input_json=raw["input_json"],
        skill_name=raw.get("skill_name"),
        subagent_session_id=raw.get("subagent_session_id"),
        result_content=raw.get("result_content") or "",
        result_content_length=raw.get("result_content_length", 0),
    )


def message_from_row(row: dict) -> Message:
    """Normalize one raw `session messages` row into a Message.

    Required fields (`ordinal`, `role`, `source_type`, `source_uuid`, `content`)
    are read directly so a malformed row fails loud; the genuinely-optional ones
    (`source_subtype`, `source_parent_uuid`, `model`, `thinking_text`,
    `tool_calls`) default to None / empty.
    """
    return Message(
        ordinal=row["ordinal"],
        role=row["role"],
        source_type=row["source_type"],
        source_subtype=row.get("source_subtype"),
        is_system=row.get("is_system", False),
        is_compact_boundary=row.get("is_compact_boundary", False),
        source_uuid=row["source_uuid"],
        source_parent_uuid=row.get("source_parent_uuid"),
        model=row.get("model"),
        thinking_text=row.get("thinking_text"),
        content=row["content"],
        tool_calls=tuple(tool_call_from_row(tc) for tc in row.get("tool_calls") or []),
    )


def collapse_resume_duplicates(messages: list[Message]) -> list[Message]:
    """Drop verbatim resume re-emissions: keep the first message per source_uuid.

    A resumed session replays earlier messages with the same `source_uuid`, so the
    first occurrence is the original and any later one is a duplicate. Forks share
    a parent but carry *different* `source_uuid`s, so they survive this pass.
    """
    seen: set[str] = set()
    kept: list[Message] = []
    for message in messages:
        if message.source_uuid in seen:
            continue
        seen.add(message.source_uuid)
        kept.append(message)
    return kept


def normalize_messages(rows: list[dict]) -> list[Message]:
    """Build the ordered Message list from raw rows, resume-duplicates collapsed.

    Preserves the order `session_messages` returns (ascending ordinal, paged to
    exhaustion); rule 2 (adjacent-repeat) dedup and fork reconstruction run later.
    """
    return collapse_resume_duplicates([message_from_row(row) for row in rows])
