"""XML rendering: the session header, conversation turns, thinking, tool calls.

Pure functions from the normalized model to XML strings — no I/O, no daemon. The
header maps a `session get` payload to the `<session>` element's attributes; the
turn renderer emits one `<user>` / `<assistant>` element (a slash command is a
`<user command="/cmd">args</user>` variant) with assistant thinking as a
`<thinking>` child, and an assistant turn's `tool_calls[]` as nested
`<tool-call>` elements. Timeline markers (`<compaction>`, `<interrupted/>`) and
abandoned rewind branches (`<rewound-branch>`) render here too. A tool call that
spawned a sub-agent nests the child as a `<subagent>` — but the fetch + recursion
is impure, so these functions take an injected `render_subagent` callback (the
`transcript` module supplies it); a pure render with no callback leaves the link
unexpanded. All text is entity-escaped, never CDATA.
"""

import re
from collections.abc import Callable, Sequence

from dev_playbook.transcript_export.classify import MessageKind, classify
from dev_playbook.transcript_export.forks import MessageNode
from dev_playbook.transcript_export.model import Message, ToolCall

TOOL_OUTPUT_TRUNCATION = 2000
"""Max characters of a tool output we inline; longer bodies are cut and marked
`truncated="true"`."""

_REJECTION_PREFIX = "The user doesn't want to proceed"
"""A user-denied tool call's `result_content` opens with this sentence."""

_ERROR_MARKER = "<tool_use_error>"
"""A failed tool call wraps its message in this block inside `result_content`."""

_TOOL_MARKER = re.compile(r"^\[[A-Z][A-Za-z0-9_]*( [A-Za-z0-9_]+)*(: .*)?\]$")
"""One inline tool marker line in a turn's pre-rendered `content`, e.g.
`[Bash: List worktrees]`, `[Tool: EnterWorktree]`, or — from `claude-haiku-4-5`
and plan-mode turns — the bare `[Bash]` / `[TaskList]` / `[Exiting Plan Mode]`
form with no colon-detail. The leading word is a TitleCase tool/action name
(first letter uppercase), which excludes the lowercase bracketed lines that occur
inside Bash command bodies (`[project]`, `[build]` in an emitted heredoc) — those
must NOT be mistaken for markers. Verified across 5064 real tool-bearing messages
to match exactly one line per tool call (agentsview v0.34.5)."""

_XML_INVALID = re.compile("[^\t\n\r\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")
"""Characters XML 1.0 forbids outright (C0 controls other than tab/newline/CR,
and the surrogate / non-character code points). Real tool output is full of them
— ANSI colour codes carry a bare ESC (0x1b) — and they are illegal even as
numeric entities, so they must be removed, not escaped. Stripping is a deliberate
sanitization, not a silent fallback: these bytes are terminal-control noise an LLM
reader has no use for, and `result_content_length` still records the true length."""

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
document order. Some keys are renamed (git_branch→branch, *_at→started/ended,
message_count→messages, compaction_count→compactions); id / project / agent /
cwd map 1:1."""


def escape(text: str) -> str:
    """Entity-escape text for either XML element content or an attribute value.

    Replaces all five predefined entities, `&` first so the ampersands the later
    replacements introduce are not double-escaped. Covering the full set keeps one
    helper safe in both positions — element text *and* double-quoted attributes —
    so we never need CDATA. First strips characters XML 1.0 forbids (ANSI/control
    bytes in tool output), which are illegal even as entities and would otherwise
    make the whole document fail to parse.
    """
    text = _XML_INVALID.sub("", text)
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


def _marker_label(line: str) -> str:
    """The leading label of a marker line.

    The text before the first `:`, or the whole bracket contents for a bare
    marker. `[Bash: detail]` -> `Bash`, `[TaskList]` -> `TaskList`,
    `[Exiting Plan Mode]` -> `Exiting Plan Mode`.
    """
    inner = line.strip()[1:-1]
    return inner.split(":", 1)[0].strip()


def strip_tool_markers(content: str, tool_names: Sequence[str]) -> str:
    """Drop the trailing inline tool markers and their bodies, keeping only prose.

    A turn's `content` is prose followed by, for each tool call, a
    `[ToolName: detail]` (or bare `[ToolName]`) marker line that heads that call's
    inlined command/output body. We render tool calls structurally from
    `tool_calls[]`, so the whole trailing region — every marker and body — is
    dropped. Markers and bodies interleave (`prose / M1 / body1 / M2 / body2 …`)
    and a body (or prose) line can itself be marker-shaped, so we do *not* count
    marker lines (that count is wrong whenever a body contains a bracketed line —
    the bug this replaced). Instead we find where the trailing region begins: the
    first *genuine* marker, i.e. the first marker line whose label matches the
    first tool call. A marker-shaped line inside a body sits after that point (so
    it is dropped, not miscounted); a marker-shaped line in the prose has a label
    that won't match the tool (so it is left as prose). For a marker whose label
    we cannot map to the tool name (e.g. `[Tool: X]`, `[Exiting Plan Mode]`) we
    fall back to the first marker line.

    With no tool calls the content is returned unchanged. We fail loud only on a
    genuine misfit: tool calls exist but the content has no marker line at all.
    """
    if not tool_names:
        return content
    lines = content.split("\n")
    marker_indices = [i for i, line in enumerate(lines) if _TOOL_MARKER.match(line)]
    if not marker_indices:
        raise ValueError(
            f"expected a tool marker for each of {len(tool_names)} tool call(s) "
            "but found none; marker model does not fit this turn's content"
        )
    first_tool = tool_names[0]
    region_start = next(
        (i for i in marker_indices if _marker_label(lines[i]) == first_tool),
        marker_indices[0],
    )
    return "\n".join(lines[:region_start]).rstrip()


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


def render_tool_call(
    tool_call: ToolCall,
    render_subagent: Callable[[str], str] | None = None,
) -> str:
    """Render one tool use as a `<tool-call>` with its `<args>` and `<output>`.

    `<args>` carries the full `input_json` (entity-escaped, never CDATA);
    `<output>` carries `result_content` truncated inline at
    `TOOL_OUTPUT_TRUNCATION`, with `chars` reporting the authoritative full length
    (`result_content_length` — the only length we have for Read/ToolSearch, whose
    bodies come back empty) and `truncated` flagging whether we cut the inline
    body. An `outcome` attribute marks a rejected or errored call; a normal call
    omits it. When the call spawned a sub-agent (`subagent_session_id` set) and a
    `render_subagent` callback is supplied, the child session is rendered inline
    as a nested `<subagent>` after the `<output>`; with no callback the link is
    left unexpanded (a pure render with no daemon access).
    """
    attrs = f'name="{escape(tool_call.tool_name)}" id="{escape(tool_call.tool_use_id)}"'
    outcome = _tool_outcome(tool_call.result_content)
    if outcome is not None:
        attrs += f' outcome="{outcome}"'
    body = tool_call.result_content
    truncated = len(body) > TOOL_OUTPUT_TRUNCATION
    shown = body[:TOOL_OUTPUT_TRUNCATION]
    subagent = ""
    if render_subagent is not None and tool_call.subagent_session_id:
        subagent = render_subagent(tool_call.subagent_session_id)
    return (
        f"<tool-call {attrs}>"
        f"<args>{escape(tool_call.input_json)}</args>"
        f'<output chars="{tool_call.result_content_length}" '
        f'truncated="{"true" if truncated else "false"}">'
        f"{escape(shown)}</output>"
        f"{subagent}"
        f"</tool-call>"
    )


def render_turn(
    message: Message,
    render_subagent: Callable[[str], str] | None = None,
) -> str:
    """Render one conversation turn as a `<user>` or `<assistant>` element.

    Dispatches on `classify`: a normal user turn, a slash command (rendered as a
    `<user command="/cmd">args</user>` variant — command is the first token, args
    the rest), or an assistant turn carrying its per-message `model`, an optional
    `<thinking>` child before the prose, and one nested `<tool-call>` per
    `tool_calls[]` entry after it. The prose has its trailing inline tool markers
    stripped (they duplicate the structural `<tool-call>` rendering). A
    `render_subagent` callback, when supplied, is threaded to each tool call so a
    sub-agent spawn nests inline. Timeline markers (interrupt, compaction) and
    dropped plumbing are *not* turns — passing one in fails loud, since they
    render through separate paths.
    """
    kind = classify(message)
    text = strip_tool_markers(
        message.content, [tc.tool_name for tc in message.tool_calls]
    )
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
            body += render_tool_call(tool_call, render_subagent)
        return f"<assistant {attrs}>{body}</assistant>"
    raise ValueError(
        f"render_turn called on a non-turn message at ordinal {message.ordinal}: "
        f"{kind} renders through a separate path"
    )


def render_compaction(message: Message) -> str:
    """Render a compaction boundary as `<compaction>summary</compaction>`.

    The boundary's pre-rendered `content` is the compaction summary (per-compaction
    token counts are an accepted loss). Fails loud on a non-compaction message,
    which renders through a different path.
    """
    if classify(message) is not MessageKind.COMPACTION:
        raise ValueError(
            f"render_compaction called on a non-compaction message at ordinal "
            f"{message.ordinal}"
        )
    return f"<compaction>{escape(message.content)}</compaction>"


def render_interrupted(message: Message) -> str:
    """Render a user interrupt as a self-closing `<interrupted ord="…"/>` marker.

    An interrupt carries no content beyond the fixed marker text; only its position
    (`ordinal`) is worth keeping. Fails loud on a non-interrupt message.
    """
    if classify(message) is not MessageKind.INTERRUPT:
        raise ValueError(
            f"render_interrupted called on a non-interrupt message at ordinal "
            f"{message.ordinal}"
        )
    return f'<interrupted ord="{message.ordinal}"/>'


def render_message(
    message: Message,
    render_subagent: Callable[[str], str] | None = None,
) -> str:
    """Dispatch one message to its renderer by kind; a `DROP` renders to nothing.

    The single entry point a transcript walk uses for a message that may be a turn,
    a compaction boundary, an interrupt, or dropped plumbing. Turns route to
    `render_turn` (which threads the `render_subagent` callback to their tool
    calls); the two timeline markers to their renderers; a `DROP` message yields
    the empty string so callers can append it unconditionally.
    """
    kind = classify(message)
    if kind is MessageKind.COMPACTION:
        return render_compaction(message)
    if kind is MessageKind.INTERRUPT:
        return render_interrupted(message)
    if kind is MessageKind.DROP:
        return ""
    return render_turn(message, render_subagent)


def render_rewound_branch(
    node: MessageNode,
    render_subagent: Callable[[str], str] | None = None,
) -> str:
    """Render one abandoned fork branch as a `<rewound-branch>`, in full fidelity.

    The branch is a `MessageNode` subtree from `reconstruct_forks`; its messages
    render in document order exactly as the live path would (`render_message` per
    node, so markers, dropped plumbing, and sub-agent spawns behave identically —
    the `render_subagent` callback is threaded through). A *nested* fork inside
    the abandoned branch — a node with more than one child — keeps its
    highest-ordinal child as this branch's inline continuation and wraps each
    lower-ordinal sibling in its own nested `<rewound-branch>`, mirroring the
    top-level live/abandoned split recursively.
    """
    return f"<rewound-branch>{_render_node(node, render_subagent)}</rewound-branch>"


def _render_node(
    node: MessageNode,
    render_subagent: Callable[[str], str] | None = None,
) -> str:
    """Render a `MessageNode` and its descendants for a `<rewound-branch>`.

    The node's children are ordinal-sorted ascending (see `forks.build_node`); the
    last (highest-ordinal) child continues this branch inline, and every earlier
    sibling is a divergence that nests as its own `<rewound-branch>` right at this
    fork point, before the inline continuation (chronological order).
    """
    body = render_message(node.message, render_subagent)
    if node.children:
        *forked, primary = node.children
        for head in forked:
            body += render_rewound_branch(head, render_subagent)
        body += _render_node(primary, render_subagent)
    return body
