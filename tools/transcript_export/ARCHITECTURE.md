# transcript_export — architecture

*A map of the system at altitude: the pipeline, where code lives, the load-bearing
bets, and the known limits. Per-module mechanics stay in each file's docstring —
this is the view above them.*

## What this is

`transcript_export` turns a Claude Code session into a single XML transcript. You
point it at a session id; you get an `<id>.xml` file back.

It exists for **fast, approximate analysis of conversations at scale** — reading a
session's shape and substance well enough to reason over many of them in bulk. It
is **not** a historical record: getting the important parts right matters, getting
every byte right does not. When in doubt it drops noise (terminal-control bytes,
duplicated harness plumbing, oversized tool dumps) rather than preserve it.

Where the data comes from: the Claude Code harness writes each session as messy
JSONL. The **AgentsView daemon** (which we assume is always active) parses that JSONL into a clean, typed messages API
(`agentsview session list | get | messages`). `transcript_export` reads *only that
parsed API* — never the raw `.jsonl`, never `agentsview session export`. The daemon
already did the hard parse; redoing it here would just duplicate and drift from it.

What it refuses to do:
- Never reads raw `.jsonl`, never calls `session export`.
- Never summarizes — it reproduces turns, lightly pruned.
- Never silently patches a surprise — unexpected input fails loud (see below).

## What the output looks like

A compact, illustrative sample (the full element set lives in `render.py`):

```xml
<session id="01J…" project="dev-playbook" agent="claude" branch="main"
         started="…" ended="…" messages="128" compactions="1">
  <user ord="3">fix the flaky test in forks</user>
  <assistant ord="4" model="claude-opus-4-8">
    <thinking>which test is flaky…</thinking>
    Let me reproduce it.
    <tool-call name="Bash" id="toolu_…">
      <args>{"command": "pytest -q tools/tests"}</args>
      <output chars="5123" truncated="true">…first 2000 chars of output…</output>
    </tool-call>
  </assistant>
  <interrupted ord="9"/>
  <compaction>…summary written when the context was compacted…</compaction>
  <rewound-branch>…an edited-away attempt, rendered in full fidelity…</rewound-branch>
  <user ord="14" command="/commit">amend</user>
</session>
```

There is no session-level `model` — model is per assistant message and can change
mid-session. A `<tool-call>` that spawned a sub-agent nests the child inline as
`<subagent id="…" messages="…">…</subagent>`, in the very same schema, recursively.

## The pipeline

Five stages turn raw rows into the transcript body; `render_session` wraps the
header around it.

| stage | function | what it does |
|---|---|---|
| fetch | `client.session_messages` | page every raw row for the session (impure — shells out to `agentsview`) |
| normalize | `model.normalize_messages` | raw dicts → typed `Message` / `ToolCall`; drop verbatim **resume** re-emissions (dedup rule 1, keyed on `source_uuid`) |
| keep | `classify.keep_messages` | drop harness plumbing (`system` rows other than the compaction summary; `queued_command` previews), then collapse **adjacent** repeats (dedup rule 2) |
| reconstruct-forks | `forks.reconstruct_forks` | sort by ordinal into the live path; carve edited-away rewinds out as abandoned branches |
| render | `render.render_message` | walk the live path in ordinal order, emitting each `<rewound-branch>` just before the live message that superseded it; recurse into sub-agents inline |

`transcript.render_session` is the one entry point per session: it fetches the
header (`session get`), runs the body through the pipeline, wraps it in
`<session>…</session>`, and asserts the whole document is well-formed XML before
returning it.

## File structure & public surface

The modules map onto the pipeline. Only `client` and the fetch at the top of
`transcript` are impure; everything else is pure functions over plain data.

| module | exports (the seams) | role |
|---|---|---|
| `cli.py` | `main`, `select_session_ids` | argv → select sessions (`ids` / `--recent N` / `--all`) → write one `<id>.xml` each |
| `transcript.py` | `render_session` | impure orchestrator: fetch + pipeline + sub-agent recursion + well-formedness guard |
| `client.py` | `session_list` / `session_get` / `session_messages`, `AgentsViewError` | the only daemon boundary; shells to `agentsview`, fails loud on nonzero exit |
| `model.py` | `Message`, `ToolCall`, `normalize_messages` | typed records + resume dedup (rule 1) |
| `classify.py` | `MessageKind`, `classify`, `keep_messages` | what each message *is* (off `source_type`, not `role`) + keep/drop + dedup rule 2 |
| `forks.py` | `reconstruct_forks`, `ForkReconstruction`, `MessageNode` | rewind reconstruction over the ordinal spine |
| `render.py` | `render_message`, `render_session_open`, `escape`, … | model → XML strings; pure, no I/O |

## Key decisions

Each is stated as the bet, then the fact that forced it.

**Read the parsed messages API, not the raw `.jsonl`.** The daemon already turns the
harness's messy JSONL into typed rows — tool calls extracted into `tool_calls[]`, a
stable `ordinal`, `source_type` / `source_subtype`. Re-parsing the `.jsonl` here
would reimplement the daemon and drift from it. We also skip `session export`, so
the output schema is *ours*, shaped for LLM reading.

**Reconstruct rewinds off the ordinal spine, not a parent→child tree.** A rewind
surfaces as two messages naming the same `source_parent_uuid`; the live one is
whichever has the higher `ordinal`. The obvious approach — follow parent→child
links — was tried first and connected to a visible message ~0% of the time (the
parent is usually an unsurfaced raw sub-record). Ordinals only ever increase on the
live branch, so sorting by ordinal *is* the live transcript; the lower-ordinal
siblings are the abandoned branches.

**Classify off `source_type` / `source_subtype`, never `role`.** The compaction
summary arrives as `role=assistant` but `source_type=system`. A role-based split
would render that summary as an ordinary assistant turn and would never drop system
plumbing — so every classification keys off source_type/subtype.

**Fail loud; never paper over.** This runs over *every* live session for analysis,
so a silent skip would quietly corrupt the dataset. Anything unexpected raises — and
those guards double as the canary that tells us the daemon's output shape drifted
(see next section).

**Pure core, thin impure shell.** Only `client` and `transcript`'s fetch touch the
daemon. `model` / `classify` / `forks` / `render` are pure functions over dicts and
dataclasses, so the whole pipeline tests on hand-built rows with no I/O. Even
sub-agent nesting is injected as a `render_subagent` callback, keeping rendering
pure.

## What fails loud

The guards that stop bad output from shipping — and signal that the daemon's output
shape changed:

- **CLI nonzero exit** → `AgentsViewError` (never partial output).
- **Unknown `source_type`** → `classify` raises rather than guess a kind.
- **Tool calls present but no inline marker to strip** → `strip_tool_markers` raises (the "marker model" no longer fits the content).
- **A rewind partition that drops or duplicates a message** → `reconstruct_forks`'s conservation check raises; a uuid-less message reaching it raises too.
- **A final document that isn't well-formed XML** → `render_session` raises before returning it.

## Known limits & future fixes

**Accepted losses** — deliberate, not worth fixing for approximate analysis:

- Tool output is inlined up to 2000 characters, then cut with `truncated="true"`; the `chars` attribute always reports the true length.
- `Read` / `ToolSearch` outputs come back length-only from the API, so their `<output>` body is empty (but `chars` is real).
- Terminal-control / ANSI bytes are stripped from text (XML forbids them even as entities); the length still counts them.
- Per-compaction token counts are dropped.
- Sub-agents deeper than 8 levels, or that cycle back to an ancestor, render as `<subagent omitted="depth|cycle"/>` instead of expanding.
- Parentless rows are treated as sequential session-roots, not rewinds of each other — a deliberate tradeoff with no clean disambiguator: a genuine root-level rewind is only caught when its siblings share a *concrete* parent uuid. (Telling two null-parent rows apart from a real root-level rewind isn't possible from the data we get.)

**Known issues — future fixes** (real defects we'd fix, not just watch):

- **Marker over-strip via fallback.** An alias-label tool call — one whose marker label isn't the tool name (`[Exiting Plan Mode]`, `[Tool: X]`) — makes `strip_tool_markers` fall back to the *first* marker-shaped line. If some prose above that call is itself marker-shaped, the strip starts too early and eats a little prose. Narrow: it loses prose, never crashes. *Fix direction:* map alias labels to their tools, or have the daemon emit explicit tool spans.

**Drift risks** — assumptions that hold today and are watched by the fail-loud canaries above:

- **The marker model is pinned to one daemon version** (`agentsview v0.34.5`, verified on 5064 tool-bearing messages). A new marker format would make `strip_tool_markers` fail loud on the gross case (tool calls but zero markers).
- **The fork model assumes the ordinal spine** — that writes only ever continue with increasing global ordinals. The conservation guard catches lost or duplicated messages, but not a wrong-yet-conserved partition if that assumption ever breaks.
