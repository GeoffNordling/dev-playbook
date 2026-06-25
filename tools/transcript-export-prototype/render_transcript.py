#!/usr/bin/env python3
"""Render Claude Code sessions as full text transcripts via the AgentsView daemon.

Single self-contained pass. Runs fully inside the Claude Code sandbox: it shells
out to the `agentsview` CLI (which reads the always-on daemon's SQLite DB), made
possible by granting the sandbox write access to ~/.agentsview (its WAL dir).
No top-level-command workaround, no intermediate files.

Public AgentsView surface depended on (the dependency contract our tests pin):
  agentsview session list                 -> recent sessions (for --recent)
  agentsview session get <id> --json       -> metadata
  agentsview session messages <id> --json  -> ordered messages; AgentsView already
                                              inlines each tool call with its args
  agentsview session tool-calls <id> --json-> tool metadata + subagent_session_id
  agentsview session export <id>           -> raw JSONL; sole source of tool OUTPUT
                                              bodies (the parsed CLI gives only
                                              result_length), indexed by tool_use_id

Sub-agents: any tool call carrying subagent_session_id is fetched and rendered
inline, recursively. Rewinds/interrupts/rejected tool calls fall out naturally
because we render AgentsView's own ordered message + tool-call view.

Usage:
  render_transcript.py <out_dir> <session_id> [<session_id> ...]
  render_transcript.py <out_dir> --recent N
"""

import json
import subprocess
import sys

OUTPUT_TRUNC = 2000  # max chars of any single tool output to inline
MAX_DEPTH = 4  # sub-agent recursion guard
PAGE = 500  # messages page size


def av(*args):
    """Call the agentsview CLI; return stdout. Fail loud on nonzero exit."""
    r = subprocess.run(["agentsview", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(
            f"agentsview {' '.join(args)} failed (rc={r.returncode}): "
            f"{r.stderr.strip()[:300]}"
        )
    return r.stdout


def av_json(*args):
    return json.loads(av(*args))


def get_messages(sid):
    out, frm = [], 0
    while True:
        d = av_json(
            "session",
            "messages",
            sid,
            "--json",
            "--from",
            str(frm),
            "--limit",
            str(PAGE),
        )
        batch = d.get("messages", [])
        if not batch:
            break
        out.extend(batch)
        last = batch[-1]["ordinal"]
        if last + 1 <= frm:
            break
        frm = last + 1
    seen, uniq = set(), []
    for m in out:
        if m["id"] in seen:
            continue
        seen.add(m["id"])
        uniq.append(m)
    return uniq


def get_result_bodies(sid):
    """Index tool_result output bodies by tool_use_id from raw export JSONL."""
    bodies = {}
    for line in av("session", "export", sid).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = rec.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                bodies[b.get("tool_use_id")] = {
                    "text": _result_text(b.get("content")),
                    "is_error": bool(b.get("is_error")),
                }
    return bodies


def _result_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                parts.append(
                    b.get("text", "")
                    if b.get("type") == "text"
                    else f"[{b.get('type', 'block')}]"
                )
            else:
                parts.append(str(b))
        return "\n".join(parts)
    return str(content)


def _indent(text, prefix):
    return "\n".join(prefix + ln for ln in text.splitlines())


def render(sid, depth=0, seen=None):
    seen = seen or set()
    if sid in seen or depth > MAX_DEPTH:
        return f"[recursion guard: {sid}]\n"
    seen = seen | {sid}

    meta = av_json("session", "get", sid, "--json")
    messages = get_messages(sid)
    tool_calls = av_json("session", "tool-calls", sid, "--json").get("tool_calls", [])
    bodies = get_result_bodies(sid)

    tc_by_ord = {}
    for c in tool_calls:
        tc_by_ord.setdefault(c["ordinal"], []).append(c)

    out = []
    if depth == 0:
        bar = "=" * 80
        out += [
            bar,
            f"SESSION {sid}",
            f"  project={meta.get('project', '?')}  agent={meta.get('agent', '?')}"
            f"  messages={meta.get('message_count', '?')}  tool_calls={len(tool_calls)}",
            f"  started={meta.get('started_at', '?')}  cwd={meta.get('cwd', '?')}",
            bar,
            "",
        ]

    for m in messages:
        ordn, role = m["ordinal"], m["role"].upper()
        ts = (m.get("timestamp") or "")[:19]
        sub = m.get("source_subtype", "")
        out.append(f"#{ordn}  {role}{f' ({sub})' if sub else ''}  {ts}")
        out.append("-" * 80)
        content = (m.get("content") or "").rstrip()
        if content:
            out.append(content)
        thinking = (m.get("thinking_text") or "").strip()
        if thinking:
            out.append("  [thinking]")
            out.append(_indent(thinking, "  | "))

        for c in tc_by_ord.get(ordn, []):
            name = c.get("tool_name")
            body = bodies.get(c.get("tool_use_id"))
            if body and body["text"].strip():
                txt = body["text"]
                err = "  !! is_error" if body["is_error"] else ""
                out.append(f"  >> output [{name}] ({len(txt)} chars){err}")
                out.append(_indent(txt[:OUTPUT_TRUNC], "  | "))
                if len(txt) > OUTPUT_TRUNC:
                    out.append(f"  | ...(+{len(txt) - OUTPUT_TRUNC} more chars)")
            child = c.get("subagent_session_id")
            if child:
                out.append(f"  vv SUB-AGENT  {child}  [{name}]")
                out.append(_indent(render(child, depth + 1, seen), "  | "))
        out.append("")
    return "\n".join(out)


def recent_session_ids(n):
    d = av_json("session", "list", "--format", "json")
    sessions = d.get("sessions", d if isinstance(d, list) else [])
    return [s["id"] for s in sessions[:n]]


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip().splitlines()[-3])  # usage hint
        print(
            "usage: render_transcript.py <out_dir> <session_id ...> | <out_dir> --recent N"
        )
        sys.exit(2)
    out_dir = sys.argv[1]
    rest = sys.argv[2:]
    sids = recent_session_ids(int(rest[1])) if rest[0] == "--recent" else rest
    for sid in sids:
        text = render(sid)
        path = f"{out_dir}/{sid}.txt"
        with open(path, "w") as f:
            f.write(text)
        print(f"wrote {path}  ({len(text)} chars, {text.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
