"""XML rendering: the session header, conversation turns, thinking, tool calls.

Pure functions from the normalized model to XML strings — no I/O, no daemon. The
header maps a `session get` payload to the `<session>` element's attributes; the
turn renderer emits one `<user>` / `<assistant>` element (a slash command is a
`<user command="/cmd">args</user>` variant) with assistant thinking as a
`<thinking>` child, and an assistant turn's `tool_calls[]` as nested
`<tool-call>` elements. Timeline markers, rewound branches, and sub-agents land
in later tasks; this module is the escaping + turn + tool-call core they build
on. All text is entity-escaped, never CDATA. See PLAN.md for the authoritative
schema.
"""

import re

from transcript_export.classify import MessageKind, classify
from transcript_export.model import Message, ToolCall

TOOL_OUTPUT_TRUNCATION = 2000
"""Max characters of a tool output we inline; longer bodies are cut and marked
`truncated="true"`. See the Design's accepted-losses section in PLAN.md."""

_REJECTION_PREFIX = "The user doesn't want to proceed"
"""A user-denied tool call's `result_content` opens with this sentence."""

_ERROR_MARKER = "<tool_use_error>"
"""A failed tool call wraps its message in this block inside `result_content`."""

_TOOL_MARKER = re.compile(r"^\[[A-Za-z][A-Za-z0-9_]*: .*\]$")
"""One inline tool marker line in a turn's pre-rendered `content`, e.g.
`[Bash: List worktrees]` or `[Tool: EnterWorktree]`. Verified (agentsview
v0.34.5, 554 tool-bearing messages) to match exactly one line per tool call."""

_HEADER_FIELDS: tuple[tuple[str, str], ...] = (
    ("id", "id"),
    ("project", "project"),
    ("agent", "agent"),
    ("branch", "git_branch"),
    ("cwd", "cwd"),
    ("started", "started_at"),
    ("ended", "ended_at"),
    ("messages", "message_count"),
    ("compactions", "compaction_count"),
)
"""(attribute name, `session get` source key) for the `<session>` header, in
document order. The renamed keys (git_branch→branch, *_at→started/ended,
message_count→messages, compaction_count→compactions) match the Design; id /
project / agent / cwd map 1:1."""


def escape(text: str) -> str:
    """Entity-escape text for either XML element content or an attribute value.

    Replaces all five predefined entities, `&` first so the ampersands the later
    replacements introduce are not double-escaped. Covering the full set keeps one
    helper safe in both positions — element text *and* double-quoted attributes —
    so we never need CDATA.
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def render_session_open(meta: dict) -> str:
    """Render the opening `<session>` tag with the header attributes.

    Maps the `session get` payload to the schema's attribute names. `id` is
    required and fails loud if absent; the rest are emitted only when present, so
    a non-repo session simply has no `branch` and an in-progress one no `ended`.
    A zero count is kept (`is None`, not falsiness). There is no session-level
    model — model is per message and can change mid-session. The caller closes the
    element with `</session>` after the body.
    """
    if not meta.get("id"):
        raise ValueError("session metadata is missing required 'id'")
    attrs = []
    for attr, key in _HEADER_FIELDS:
        value = meta.get(key)
        if value is None:
            continue
        attrs.append(f'{attr}="{escape(str(value))}"')
    return f"<session {' '.join(attrs)}>"


def strip_tool_markers(content: str, tool_call_count: int) -> str:
    """Drop the trailing inline tool markers from a turn's pre-rendered text.

    A turn's `content` is prose followed by one `[ToolName: detail]` marker per
    tool call (and, for Bash, a trailing `$ command` line that may itself span
    several lines). Those markers duplicate what we render structurally from
    `tool_calls[]`, so we keep only the prose. The markers always trail the prose
    and there is exactly one marker line per tool call (verified live), so the
    block starts at the `tool_call_count`-th marker line from the end; everything
    from there on is the marker block. With no tool calls — or, defensively, fewer
    marker lines than tool calls — the content is returned unchanged so prose is
    never eaten.
    """
    if tool_call_count <= 0:
        return content
    lines = content.split("\n")
    marker_indices = [i for i, line in enumerate(lines) if _TOOL_MARKER.match(line)]
    if len(marker_indices) < tool_call_count:
        return content
    block_start = marker_indices[-tool_call_count]
    return "\n".join(lines[:block_start]).rstrip()


def _tool_outcome(result_content: str) -> str | None:
    """Derive a tool call's `outcome` attribute from its output text, or None.

    A user denial opens with a fixed sentence; a tool failure wraps its message in
    a `<tool_use_error>` block. A normal call has neither and gets no attribute.
    The denial check comes first since a rejection is not an error.
    """
    if result_content.startswith(_REJECTION_PREFIX):
        return "rejected"
    if _ERROR_MARKER in result_content:
        return "error"
    return None


def render_tool_call(tool_call: ToolCall) -> str:
    """Render one tool use as a `<tool-call>` with its `<args>` and `<output>`.

    `<args>` carries the full `input_json` (entity-escaped, never CDATA);
    `<output>` carries `result_content` truncated inline at
    `TOOL_OUTPUT_TRUNCATION`, with `chars` reporting the authoritative full length
    (`result_content_length` — the only length we have for Read/ToolSearch, whose
    bodies come back empty) and `truncated` flagging whether we cut the inline
    body. An `outcome` attribute marks a rejected or errored call; a normal call
    omits it.
    """
    attrs = f'name="{escape(tool_call.tool_name)}" id="{escape(tool_call.tool_use_id)}"'
    outcome = _tool_outcome(tool_call.result_content)
    if outcome is not None:
        attrs += f' outcome="{outcome}"'
    body = tool_call.result_content
    truncated = len(body) > TOOL_OUTPUT_TRUNCATION
    shown = body[:TOOL_OUTPUT_TRUNCATION]
    return (
        f"<tool-call {attrs}>"
        f"<args>{escape(tool_call.input_json)}</args>"
        f'<output chars="{tool_call.result_content_length}" '
        f'truncated="{"true" if truncated else "false"}">'
        f"{escape(shown)}</output>"
        f"</tool-call>"
    )


def render_turn(message: Message) -> str:
    """Render one conversation turn as a `<user>` or `<assistant>` element.

    Dispatches on `classify`: a normal user turn, a slash command (rendered as a
    `<user command="/cmd">args</user>` variant — command is the first token, args
    the rest), or an assistant turn carrying its per-message `model`, an optional
    `<thinking>` child before the prose, and one nested `<tool-call>` per
    `tool_calls[]` entry after it. The prose has its trailing inline tool markers
    stripped (they duplicate the structural `<tool-call>` rendering). Timeline
    markers (interrupt, compaction) and dropped plumbing are *not* turns — passing
    one in fails loud, since they render through separate paths in later tasks.
    """
    kind = classify(message)
    text = strip_tool_markers(message.content, len(message.tool_calls))
    if kind is MessageKind.USER:
        return f'<user ord="{message.ordinal}">{escape(text)}</user>'
    if kind is MessageKind.SLASH_COMMAND:
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        return (
            f'<user ord="{message.ordinal}" command="{escape(command)}">'
            f"{escape(args)}</user>"
        )
    if kind is MessageKind.ASSISTANT:
        attrs = f'ord="{message.ordinal}"'
        if message.model is not None:
            attrs += f' model="{escape(message.model)}"'
        body = ""
        if message.thinking_text:
            body += f"<thinking>{escape(message.thinking_text)}</thinking>"
        body += escape(text)
        for tool_call in message.tool_calls:
            body += render_tool_call(tool_call)
        return f"<assistant {attrs}>{body}</assistant>"
    raise ValueError(
        f"render_turn called on a non-turn message at ordinal {message.ordinal}: "
        f"{kind} renders through a separate path"
    )
