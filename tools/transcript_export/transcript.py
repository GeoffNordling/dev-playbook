"""Session orchestration: fetch, reconstruct, render — recursing into sub-agents.

The impure top of the render stack and the one place that turns a session *id*
into its complete XML. Given an id and the AgentsView client it fetches the
session header and messages, applies the normalize/keep/drop pipeline,
reconstructs rewind forks, then walks the live path emitting each message with
any abandoned branches at their fork points. When a tool call spawned a
sub-agent it fetches that child session and renders it inline as a nested
`<subagent>`, recursively — the child renders in the very same schema. A visited
set guards against a cycle in the agent graph and a depth ceiling against
pathological nesting; tripping either emits a self-closing placeholder rather
than silently dropping the sub-agent.

`render_session` is the single per-session entry point; T10 wires it into the
CLI (selection + file output) and reuses it unchanged. See PLAN.md for the
authoritative schema.
"""

import subprocess
import xml.etree.ElementTree as ElementTree
from collections.abc import Callable

from transcript_export.classify import keep_messages
from transcript_export.client import session_get, session_messages
from transcript_export.forks import reconstruct_forks
from transcript_export.model import normalize_messages
from transcript_export.render import (
    escape,
    render_message,
    render_rewound_branch,
    render_session_open,
)

MAX_SUBAGENT_DEPTH = 8
"""How deep the sub-agent recursion may go before it stops expanding and emits a
placeholder. A real agent graph is only a few levels deep; this ceiling guards
against a pathological or malformed chain, not a normal limit."""


def render_session(session_id: str, runner: Callable = subprocess.run) -> str:
    """Render one whole session to a complete `<session>…</session>` string.

    Fetches the session header and messages through the AgentsView client and
    renders the full transcript, recursing into any sub-agents inline. The single
    entry point a caller uses per selected session; the session id seeds the
    cycle-guard's visited set so a sub-agent that links back to it is caught.
    """
    meta = session_get(session_id, runner=runner)
    body = _render_body(session_id, runner, visited=frozenset({session_id}), depth=0)
    document = f"{render_session_open(meta)}{body}</session>"
    _assert_well_formed(document, session_id)
    return document


def _assert_well_formed(document: str, session_id: str) -> None:
    """Fail loud if the complete `<session>` document is not well-formed XML.

    A rendered transcript is one XML document; a malformed one (unclosed tag,
    stray close, illegal char) must crash at the source rather than ship. Parses
    the whole top-level document with a strict parser and re-raises any failure
    as a clear error. Validates only the complete document, not nested fragments.
    """
    try:
        ElementTree.fromstring(document)
    except ElementTree.ParseError as exc:
        raise ValueError(
            f"render_session produced malformed XML for session {session_id}: {exc}"
        ) from exc


def _render_body(
    session_id: str,
    runner: Callable,
    visited: frozenset[str],
    depth: int,
) -> str:
    """Render a session's transcript body: live path plus abandoned branches.

    Shared by the top-level `<session>` and every nested `<subagent>` — they
    differ only in the wrapper tag the caller adds. Fetches and normalizes the
    rows (rule 1), applies the keep/drop policy (rule 2 + plumbing), reconstructs
    forks, then walks the live path in ordinal order: before each live message it
    emits any rewind branches it superseded (keyed by that message's
    `source_uuid`), then the message itself through `render_message`. Branches are
    keyed by their live sibling, which is always on the live path; a key that
    isn't (a malformed payload) is emitted up front so nothing is lost. A
    `render_subagent` callback closed over this session's `visited`/`depth` is
    threaded into every render so sub-agent spawns expand inline.
    """
    rows = session_messages(session_id, runner=runner)
    messages = keep_messages(normalize_messages(rows))
    fork = reconstruct_forks(messages)
    render_subagent = _subagent_renderer(runner, visited, depth)

    live_uuids = {message.source_uuid for message in fork.live_path}
    parts: list[str] = []
    for fork_point, heads in fork.abandoned_branches.items():
        if fork_point not in live_uuids:
            for head in heads:
                parts.append(render_rewound_branch(head, render_subagent))
    for message in fork.live_path:
        # A live-path message always has a uuid (reconstruct_forks fails loud
        # otherwise); the guard only narrows the type for the branch lookup.
        if message.source_uuid is not None:
            for head in fork.abandoned_branches.get(message.source_uuid, ()):
                parts.append(render_rewound_branch(head, render_subagent))
        parts.append(render_message(message, render_subagent))
    return "".join(parts)


def _subagent_renderer(
    runner: Callable,
    visited: frozenset[str],
    depth: int,
) -> Callable[[str], str]:
    """Build the callback `render_message` threads to expand a sub-agent inline.

    The returned function maps a `subagent_session_id` to its full
    `<subagent id messages>…</subagent>` XML, closed over the current `visited`
    set and `depth`. It enforces the two guards: a session already on the path
    back to the root (a cycle) or one past `MAX_SUBAGENT_DEPTH` is *not* expanded
    — instead a self-closing `<subagent id omitted="cycle|depth"/>` placeholder
    records that the sub-agent existed without recursing. The `messages` attribute
    carries the child's `message_count` (omitted if the header lacks it), matching
    the top-level header's mapping.
    """

    def render_subagent(subagent_session_id: str) -> str:
        ident = escape(subagent_session_id)
        if subagent_session_id in visited:
            return f'<subagent id="{ident}" omitted="cycle"/>'
        if depth + 1 > MAX_SUBAGENT_DEPTH:
            return f'<subagent id="{ident}" omitted="depth"/>'
        meta = session_get(subagent_session_id, runner=runner)
        body = _render_body(
            subagent_session_id,
            runner,
            visited=visited | {subagent_session_id},
            depth=depth + 1,
        )
        count = meta.get("message_count")
        messages_attr = "" if count is None else f' messages="{escape(str(count))}"'
        return f'<subagent id="{ident}"{messages_attr}>{body}</subagent>'

    return render_subagent
