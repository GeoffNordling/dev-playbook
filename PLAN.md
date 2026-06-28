# Plan: Claude Transcript Export (XML, AgentsView-parsed)

A Ralph loop works this file top to bottom. Each iteration, a fresh agent
reads this plan and the progress log, completes one unfinished task,
checks it off, and commits. Everything it needs to act is here — including the
Design and Working notes below, where earlier iterations may leave important facts.

## Done when

- `tools/bin/transcript-export <out_dir> <session_id>` writes
  `<out_dir>/<session_id>.xml`, a well-formed XML transcript following the schema
  in the Design below.
- The transcript renders every kept message in order, assistant thinking, and
  tool calls with arguments and truncated (≤2000-char) outputs.
- Sub-agents are fetched and nested inline as `<subagent>`, recursively.
- Rewind forks render with the live path as the main transcript and abandoned
  branches inside `<rewound-branch>`; verbatim resume-duplicates are collapsed.
- All text content is entity-escaped and the whole file parses as valid XML.
- The tool reads **only** the parsed `agentsview` messages API (`list` / `get` /
  `messages`); it never calls `session export` and never parses raw `.jsonl`.
- Selection works: explicit ids, `--recent N`, and `--all`; one run renders many
  sessions.
- `make -C tools check` is green, and the suite includes tests that run against
  the live AgentsView daemon and exercise each CLI surface used.
- The `tools/transcript-export-prototype/` directory is deleted.

## Design

The authoritative design. Read it before implementing; the tasks implement it.

### What AgentsView is

AgentsView parses Claude Code's session logs into a queryable database, exposed
through the `agentsview` CLI. Its daemon runs continuously in the background on
this machine, so the data is **always available** — there is no setup or start
step; just shell out to `agentsview`. Every subcommand accepts `--json` and
prints one JSON object to stdout (and exits nonzero on error). This tool uses
three read commands — `session list`, `session get`, `session messages` —
detailed under Data source below.

### Goal

A CLI tool that exports any Claude Code session into a faithful, **high-signal**,
machine-readable **XML** transcript on disk — every meaningful message in order,
tool calls with arguments, sub-agents nested inline, and the messy realities
(rewinds, compaction, interrupts, rejected calls) preserved and marked.
**Primary consumer is an LLM**; human-readability is secondary. Sourced
**entirely from AgentsView's parsed CLI** — no raw-JSONL parsing. Batches over
many sessions in one run.

### Data source — the messages API only

**This tool reads only AgentsView's parsed messages API; it never calls
`session export` and never parses raw `.jsonl`.** That one locked decision
defines everything we can and cannot capture (next section).

Commands used:
- `session list --format json` → `{sessions, next_cursor, total}` — selection.
  Sub-agent sessions are excluded by default (what we want for the top-level pick).
- `session get <id> --json` — session metadata for the `<session>` header.
- `session messages <id> --json --from <ord> --limit <n>` → `{messages, count}`,
  the ordered conversation. **Default page is 100** — always pass `--limit` and
  page on `last_ordinal + 1`.

A sub-agent is a normal session with an `agent-<hex>` id (linked from the tool
call that spawned it); query it with the same commands and recurse.

### What the messages API gives us (verified, agentsview v0.34.5)

Each `session messages` row carries: `ordinal` (sparse global index; gaps are
normal), `role`, `source_type` (`user`/`assistant`/`system`), `source_subtype`
(`null` | `task_notification` | `compact_boundary`), `is_system`,
`is_compact_boundary`, `source_uuid`, `source_parent_uuid` (absent on a message
with no parent), `model` (per message — can vary across the session),
`thinking_text`, a pre-rendered `content` string, and a structured `tool_calls`
array.

Each `tool_calls[]` entry holds everything we need about one tool use:
`tool_name`, `category`, `tool_use_id`, `input_json` (full arguments),
`skill_name`, `subagent_session_id` (set when the call spawned a sub-agent),
`result_content` (the output body) and `result_content_length`. So a single
`messages` call yields the conversation, thinking, tool args + outputs, sub-agent
links, fork links, and compaction boundaries — no second endpoint needed.

ACCEPTED LOSSES (consequences of messages-only, consciously accepted):
- `Read` and `ToolSearch` outputs come back empty (length only) — the call and
  its arguments are kept, the body is not. Every other tool's output is present;
  truncate at 2000 chars.
- Contents of `@`-referenced files — the **filename** is kept, not the body.
- `pr-link` and per-compaction token counts (the compaction **summary** is kept).

### XML schema (kebab-case, entity-escaped)

- Root `<session>`; intrinsic metadata as **attributes**: id, project, agent,
  branch, cwd, started, ended, messages, compactions. (No session-level model —
  model is per message and can change mid-session.)
- Turns: `<user>` / `<assistant>`, each with `ord` (source ordinal);
  `<assistant>` also carries `model`. A slash command → `command="/goal"`
  attribute + args as the element text.
- `<thinking>` child element inside assistant turns.
- Tool calls: `<tool-call name="…" id="toolu_…">` containing `<args>` (raw JSON,
  entity-escaped) and `<output chars="…" truncated="true|false">…</output>`
  (truncate inline at 2000). Outcome attribute on the call:
  `outcome="rejected"` (user denied) / `outcome="error"` (tool failed), derived
  from the result text; omitted when normal.
- Sub-agent: `<subagent id="agent-…" messages="…">` nested **inside** its
  spawning `<tool-call>`, holding the child session in the same schema,
  recursively (cycle + depth guard).
- Timeline markers in document order: `<compaction>summary…</compaction>`,
  `<interrupted ord="…"/>`.
- Rewind forks: the **live path** is the main transcript; each abandoned branch
  nests in **full fidelity** inside `<rewound-branch>` at its fork point.
- All text content entity-escaped (`&lt; &gt; &amp; &quot; &apos;`). Entity
  escaping is total and edge-case-free — do NOT use CDATA.

### Reconstruction rules

- **Live path / forks:** build the message tree from `source_parent_uuid` →
  `source_uuid`. The **live path is the ancestor chain of the
  most-recently-written message** (highest ordinal; writing only ever continues
  on the live branch, so abandoned branches freeze with older ordinals). Every
  other subtree hanging off a fork point is an abandoned branch →
  `<rewound-branch>`. A plain tree walk, so it generalizes to nested/stacked
  forks. A fork's common parent may itself be absent from the payload; root each
  present child as its own branch head.
- **Dedup (two rules):** (1) collapse verbatim resume re-emissions by
  `source_uuid` — a resumed session re-emits earlier messages with the *same*
  `source_uuid`; keep the first. (2) Collapse a message that exactly repeats the
  immediately preceding kept message (same `role` + `content`) — queued-prompt /
  injection doubles occur with a *different* `source_uuid`, so rule 1 misses
  them. Forks are neither: same `source_parent_uuid`, *different* `source_uuid`,
  *different* content.
- **Turn text vs tool markers:** a message's `content` is pre-rendered prose
  followed by inline tool markers — `[ToolName: detail]`, plus a trailing
  `$ command` line for Bash. Those markers duplicate what we render structurally
  from `tool_calls[]`, so strip the trailing marker / `$` lines and emit only the
  prose as the turn text. Markers always trail the prose. `thinking_text` is a
  separate field (already clean).

### Keep / drop policy (high-signal faithful)

Principle: KEEP user intent, assistant output, tool calls + (partial) outputs,
and structural markers for the messy realities. DROP harness plumbing,
telemetry, and duplicate injections of a real message. (Most plumbing record
types never reach us anyway — we read the parsed message stream, not raw
records.)

- KEEP: user / assistant messages; assistant thinking (`thinking_text`); tool
  calls + args + (partial) outputs; slash-command invocations (a user message
  whose `content` starts with `/` — command is the first token, args the rest);
  the compaction summary; interrupts.
- DROP: `source_type="system"` plumbing **other than** the compaction summary —
  in practice `source_subtype="task_notification"` (sub-agent completion notices).
  The wrappers the raw export carries (`<command-name>` twins, `<local-command-*>`
  blocks, context-usage notices) are **already stripped by the parsed API** and
  never reach us, so there is nothing extra to filter. Then apply the two dedup
  rules above.

### Verified behaviours (live exploration, agentsview v0.34.5)

- Resume re-emits messages verbatim with the **same** `source_uuid`; an
  edit/rewind **forks** (same `source_parent_uuid`, different `source_uuid`).
- Compaction boundary = `source_subtype="compact_boundary"`
  (`is_compact_boundary=true`); its `content` is the summary.
- Sub-agent completion plumbing = `source_subtype="task_notification"` system
  messages (dropped).
- Rejected vs error tool calls both surface as failures in `result_content`: a
  denial begins "The user doesn't want to proceed…"; an error is a
  `<tool_use_error>` block.
- Interrupt = a message whose content is exactly `[Request interrupted by user]`.
- Ordinals are a sparse global index (gaps normal); parallel tool calls share one
  ordinal, so a message's `tool_calls` array can hold several.
- Sub-agents are standalone `agent-<hex>` sessions, queried the same way and
  excluded from the default `session list`; recursion handles any nesting depth.

### Finding example sessions for development

To develop and sanity-check each messy case, pull a live example from the daemon.
`agentsview session search <text> --json` searches message/tool content (each
match carries a `session_id`); `agentsview session list --json` filters and sorts
session metadata.

- **One rich example with everything:** session
  `d45168f9-7715-4631-afe2-074f8fa2df85` holds a 3-way rewind fork, a compaction,
  two sub-agents, an interrupt, and a rejected tool call — a good single fixture
  to eyeball end to end.
- **Rewind/fork:** no content marker exists — find it structurally. In a
  session's `messages`, locate a `source_parent_uuid` shared by ≥2 messages with
  different `source_uuid`; that is a fork point (ordinals 128 / 135 / 145 in the
  example above).
- **Compaction:** `session list --json --sort compactions:desc` — the top
  sessions carry the most compaction boundaries.
- **Sub-agents:** `session list --json --include-children` surfaces `agent-*`
  child sessions; each child's `source_session_id` is a parent that spawned one.
- **Interrupt:** `session search "[Request interrupted by user]" --json`.
- **Rejected tool call:**
  `session search "The user doesn't want to proceed" --json --in tool_result`.

## Working notes

- **Layout:** logic in a `tools/transcript_export/` package; CLI entry at
  `tools/bin/transcript-export`; tests in `tools/tests/`.
- **`tools/` is an existing `uv` project** (its own `pyproject.toml`, `Makefile`,
  and sibling packages like `skipcache/`, `judgments/`). T1 *adds* a package
  following those conventions — it does not create the project. The `Makefile`'s
  `mypy` target lists packages **explicitly**; add `transcript_export/` to that
  list or the new code is silently never typechecked.
- **Header field mapping** (`session get` → `<session>` attributes): `git_branch`
  → branch, `started_at` → started, `ended_at` → ended, `message_count` →
  messages, `compaction_count` → compactions; id / project / agent / cwd map 1:1.
- **Unit-test fixtures are small hand-authored JSON** dicts shaped like the
  documented `messages` / `tool_calls` fields — do **not** capture and trim real
  sessions for them. The live daemon is only for the T11 integration test and for
  eyeballing the rich example session.
- **Output / idempotency:** write one file per session, `<out_dir>/<id>.xml`;
  re-running overwrites it (idempotent regenerate). Sub-agents are always nested
  inline, never emitted as separate files.
- **Check gate:** `make -C tools check` (ruff format-check, ruff lint, mypy
  typecheck, pytest). If it can't find ruff/pytest, run `uv sync` in `tools/`
  first. Every task must leave this green.
- **Two test tiers:** unit tests **mock the `agentsview` subprocess** (no daemon
  needed) — use these for everything except the one live-daemon task. The
  live-daemon tests need the always-on local daemon and must assert *structural
  invariants* (well-formed XML, header present, ordering), never exact content —
  real sessions change.
- `session messages` default page is **100** — always pass `--limit` and page on
  `last_ordinal + 1`.
- The reference prototype (`tools/transcript-export-prototype/render_transcript.py`)
  is **plain-text and uses `export`** — directional reference only. Do **not**
  copy its `export` usage or its dedup-by-`id` bug (dedup on `source_uuid`).
  Delete the whole prototype dir in the final task.

## Tasks

- [x] **T1 — Scaffold + green build.** Create the `tools/transcript_export/`
  package (`__init__.py`) and a `tools/bin/transcript-export` entry that imports
  it and prints usage. Wire it into the `tools/` project so ruff/mypy/pytest see
  it. Add one trivial unit test. `make -C tools check` green.
- [ ] **T2 — AgentsView client.** `client.py`: thin wrappers `session_list`,
  `session_get`, `session_messages` (paged via `--from`/`--limit`,
  default-page-100 aware). Shell out to `agentsview`, parse JSON, **fail loud**
  on nonzero exit. Unit tests mock `subprocess`. Green.
- [ ] **T3 — Message model + resume dedup.** A normalized message dataclass; an
  ordered list built from `session_messages`; collapse verbatim
  resume-duplicates by `source_uuid` (keep first). Unit tests with fixtures.
  Green.
- [ ] **T4 — Fork reconstruction.** Build the tree from
  `source_parent_uuid`→`source_uuid`; compute the live path (ancestors of the
  highest-ordinal message); collect abandoned branches per fork point. Unit test
  with a multi-branch fixture (incl. a nested fork). Green.
- [ ] **T5 — Record classification.** Key off `source_type`/`source_subtype`,
  **not** `role` (the compaction boundary is `role=assistant` but
  `source_type=system`). Classify each message: normal user/assistant; slash
  command (user `content` starts with `/`); interrupt
  (`[Request interrupted by user]`); compaction summary
  (`source_subtype="compact_boundary"`); DROP = `source_type="system"` except the
  compaction summary (e.g. `task_notification`). Apply the two dedup rules from
  Reconstruction. Per the Keep/drop policy in Design. Unit tests. Green.
- [ ] **T6 — Render: header + turns + thinking.** Entity-escaping helper;
  `<session>` header from `session_get`; `<user>`/`<assistant>` turns with `ord`;
  `<thinking>`. Pure function (model → XML string). Unit tests incl. escaping of
  `< > & "` and content that contains XML-looking text. Green.
- [ ] **T7 — Render: tool calls.** From each message's `tool_calls[]`:
  `<tool-call name id>` + `<args>` (`input_json`, escaped) + `<output chars
  truncated>` (`result_content`, truncate 2000; empty for Read/ToolSearch).
  Derive `outcome="rejected"|"error"` from the output text. Unit tests. Green.
- [ ] **T8 — Render: markers + rewound branches.** `<compaction>`,
  `<interrupted/>`, and `<rewound-branch>` (abandoned branch in full fidelity at
  its fork point). Unit tests. Green.
- [ ] **T9 — Sub-agent recursion.** When a `tool_calls[]` entry has
  `subagent_session_id`, fetch that child session and render it nested inside the
  `<tool-call>` as `<subagent>`, recursively, with cycle + depth guards. Unit
  tests with a mocked parent→child. Green.
- [ ] **T10 — CLI: selection + output.** Accept explicit ids, `--recent N`,
  `--all`; for each session render and write `<out_dir>/<id>.xml`. End-to-end
  wiring. Unit tests for selection logic (mocked `session_list`). Green.
- [ ] **T11 — Live-daemon integration tests.** Render a real recent session end
  to end against the live daemon; assert well-formed XML + structural invariants;
  exercise `list`/`get`/`messages`. Green.
- [ ] **T12 — Retire the prototype.** Delete `tools/transcript-export-prototype/`;
  update any README/pointers. `make -C tools check` green.
