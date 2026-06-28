"""XML rendering: the session header, conversation turns, and assistant thinking.

Pure functions from the normalized model to XML strings — no I/O, no daemon. The
header maps a `session get` payload to the `<session>` element's attributes; the
turn renderer emits one `<user>` / `<assistant>` element (a slash command is a
`<user command="/cmd">args</user>` variant) with assistant thinking as a
`<thinking>` child. Tool calls, timeline markers, rewound branches, and
sub-agents land in later tasks; this module is the escaping + turn core they
build on. All text is entity-escaped, never CDATA. See PLAN.md for the
authoritative schema.
"""

from transcript_export.classify import MessageKind, classify
from transcript_export.model import Message

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


def render_turn(message: Message) -> str:
    """Render one conversation turn as a `<user>` or `<assistant>` element.

    Dispatches on `classify`: a normal user turn, a slash command (rendered as a
    `<user command="/cmd">args</user>` variant — command is the first token, args
    the rest), or an assistant turn carrying its per-message `model` and an
    optional `<thinking>` child before the prose. Timeline markers (interrupt,
    compaction) and dropped plumbing are *not* turns — passing one in fails loud,
    since they render through separate paths in later tasks.
    """
    kind = classify(message)
    if kind is MessageKind.USER:
        return f'<user ord="{message.ordinal}">{escape(message.content)}</user>'
    if kind is MessageKind.SLASH_COMMAND:
        parts = message.content.split(maxsplit=1)
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
        body += escape(message.content)
        return f"<assistant {attrs}>{body}</assistant>"
    raise ValueError(
        f"render_turn called on a non-turn message at ordinal {message.ordinal}: "
        f"{kind} renders through a separate path"
    )
