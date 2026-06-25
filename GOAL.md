# GOAL: Claude Transcript Export

## What to build

A tool that turns any Claude Code session into a faithful, complete,
human-readable transcript on disk — and can loop over many sessions
automatically.

"Faithful and complete" means nothing important is lost: every user and
assistant message in order; every tool call with its name, arguments, and
output; sub-agents nested inline where they were invoked; and the messy
realities — rewinds, interrupts, rejected tool calls, compaction — preserved
rather than smoothed over.

## Depend on AgentsView

A design decision: depend on AgentsView (Wes McKinney's tool), an always-on
local daemon that parses Claude Code sessions and dozens of other agent formats.
Get session data from its `agentsview` CLI rather than parsing raw `.jsonl`.

## Facts and decisions

- Session data comes from three `agentsview` CLI commands: `session messages`
  (messages in order, each tool call inlined with its arguments), `session
  tool-calls` (tool metadata, including the session id of each sub-agent a call
  spawned), and `session export` (raw session JSONL).
- The parsed CLI gives tool-call arguments but not tool output bodies. Output
  bodies come only from `session export`, matched to each call by `tool_use_id`.
- Sub-agents are themselves sessions. Query a sub-agent by its id with the same
  commands and recurse to nest them.

## Reference prototype

A working end-to-end prototype lives at
`tools/transcript-export-prototype/render_transcript.py`. One self-contained
script that calls `agentsview`, pulls tool outputs from `session export`,
recurses into sub-agents, and writes finished transcripts. It already handles
ordering, paging, and recursion. It is a prototype: reference it while building
the real tool at `tools/bin/transcript-export`, then delete the
`tools/transcript-export-prototype/` directory once the real tool exists.

## Done when

- The tool lives in this repo, not as a loose script outside it.
- It produces a faithful, complete transcript (per above) for a given session,
  and can loop over many sessions in one run.
- It depends only on the `agentsview` CLI — no raw-`.jsonl` parsing beyond
  pulling output bodies from `session export`.
- It has tests that run against the live AgentsView daemon and exercise the CLI
  surfaces it depends on.

## Decisions left to the builder (make early, record in PROGRESS.md)

- Output format: plain text (like the prototype) or markdown.
- Where the tool lives in the repo, and how it is invoked.
- How sessions are selected: explicit ids, most-recent-N, or all.
