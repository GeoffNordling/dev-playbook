"""Shared fakes for transcript_export tests: row builders + a fake AgentsView daemon.

Hand-authored dicts shaped like the documented `session get` / `session messages`
fields (never trimmed real sessions), plus a `subprocess.run` stand-in that serves
`session get` / `session messages` from an in-memory `{id: {"meta", "rows"}}` map.
The shapes mirror what `agentsview v0.34.5` emits: an assistant turn ends its
`content` with one inline `[ToolName: …]` marker per tool call, the sub-agent spawn
tool is `Agent`, and system-typed rows (interrupt, compaction) carry role=assistant.
"""

import json
import subprocess
from collections.abc import Callable

INTERRUPT_CONTENT = "[Request interrupted by user]"


def tc_row(
    *,
    tool_name: str = "Agent",
    tool_use_id: str = "toolu_1",
    input_json: str = "{}",
    subagent_session_id: str | None = None,
    result_content: str = "",
    result_content_length: int | None = None,
) -> dict:
    """A raw `tool_calls[]` entry; `subagent_session_id` set marks a sub-agent spawn.

    `result_content_length` defaults to the body length — the API reports the true
    length, and only Read/ToolSearch send an empty body with a nonzero length, which
    a caller pins by passing `result_content=""` with an explicit length.
    """
    row: dict = {
        "tool_name": tool_name,
        "tool_use_id": tool_use_id,
        "input_json": input_json,
        "result_content": result_content,
        "result_content_length": (
            len(result_content)
            if result_content_length is None
            else result_content_length
        ),
    }
    if subagent_session_id is not None:
        row["subagent_session_id"] = subagent_session_id
    return row


def user_row(
    *,
    ordinal: int,
    source_uuid: str,
    source_parent_uuid: str | None = None,
    content: str = "ask",
) -> dict:
    """A raw user message row."""
    row: dict = {
        "ordinal": ordinal,
        "role": "user",
        "source_type": "user",
        "source_uuid": source_uuid,
        "content": content,
    }
    if source_parent_uuid is not None:
        row["source_parent_uuid"] = source_parent_uuid
    return row


def assistant_row(
    *,
    ordinal: int,
    source_uuid: str,
    source_parent_uuid: str | None = None,
    content: str = "",
    thinking_text: str | None = None,
    tool_calls: list[dict] | None = None,
) -> dict:
    """A raw assistant message row, optionally carrying tool calls.

    Real assistant turns end their `content` with one inline `[ToolName: …]` marker
    per tool call (the renderer strips them and fails loud if none is present), so a
    fixture with tool calls appends a matching marker line for each.
    """
    row: dict = {
        "ordinal": ordinal,
        "role": "assistant",
        "source_type": "assistant",
        "source_uuid": source_uuid,
        "content": content,
        "model": "m",
    }
    if source_parent_uuid is not None:
        row["source_parent_uuid"] = source_parent_uuid
    if thinking_text is not None:
        row["thinking_text"] = thinking_text
    if tool_calls is not None:
        row["tool_calls"] = tool_calls
        markers = "\n".join(
            f"[{tc.get('tool_name', 'Agent')}: spawn]" for tc in tool_calls
        )
        row["content"] = f"{content}\n{markers}" if content else markers
    return row


def system_row(
    *,
    ordinal: int,
    source_uuid: str,
    source_subtype: str,
    content: str,
    source_parent_uuid: str | None = None,
) -> dict:
    """A raw system-typed row: an interrupt (`interrupted`) or a compaction boundary
    (`compact_boundary`). Both arrive as source_type=system with role=assistant."""
    row: dict = {
        "ordinal": ordinal,
        "role": "assistant",
        "source_type": "system",
        "source_subtype": source_subtype,
        "source_uuid": source_uuid,
        "content": content,
    }
    if source_parent_uuid is not None:
        row["source_parent_uuid"] = source_parent_uuid
    return row


def fake_daemon(
    sessions: dict[str, dict], evicted: frozenset[str] = frozenset()
) -> Callable:
    """A fake `subprocess.run` dispatching `session get`/`messages` from a map.

    `sessions` maps a session id to `{"meta": {...}, "rows": [...]}`. `get` returns
    the meta; `messages` returns rows with ordinal >= `--from`, so paging exhausts
    after the live rows (the next page comes back empty). A lookup for an id absent
    from the map exits nonzero with `... not found`, mirroring the daemon's response
    for a linked-but-uningested subagent (which the client maps to SessionNotFound).
    An id in `evicted` answers `get` from the map but fails `messages` not-found,
    modelling a session pruned between the two calls.
    """

    def completed(stdout: str) -> object:
        return subprocess.CompletedProcess(
            args=["agentsview"], returncode=0, stdout=stdout
        )

    def not_found(sid: str) -> object:
        return subprocess.CompletedProcess(
            args=["agentsview"],
            returncode=1,
            stdout="",
            stderr=f"fatal: session {sid} not found",
        )

    def runner(args: list[str], **kwargs: object) -> object:
        # Locate the subcommand relative to "session" so the fake is agnostic to
        # leading global flags (e.g. the injected `--server <url>`).
        base = args.index("session")
        cmd, sid = args[base + 1], args[base + 2]
        if sid not in sessions:
            return not_found(sid)
        entry = sessions[sid]
        if cmd == "get":
            return completed(json.dumps(entry["meta"]))
        if cmd == "messages":
            if sid in evicted:
                return not_found(sid)
            frm = int(args[args.index("--from") + 1])
            rows = [r for r in entry["rows"] if r["ordinal"] >= frm]
            return completed(json.dumps({"messages": rows, "count": len(rows)}))
        raise AssertionError(f"unexpected agentsview command: {cmd}")

    return runner
