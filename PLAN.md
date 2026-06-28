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
- The tool reads **only** the parsed `agentsview` CLI (`get` / `messages` /
  `tool-calls` / `list`); it never calls `session export` and never parses raw
  `.jsonl`.
- Selection works: explicit ids, `--recent N`, and `--all`; one run renders many
  sessions.
- `make -C tools check` is green, and the suite includes tests that run against
  the live AgentsView daemon and exercise each CLI surface used.
- The `tools/transcript-export-prototype/` directory is deleted.

## Design

The authoritative design. Read it before implementing; the tasks implement it.

### Goal

A CLI tool that exports any Claude Code session into a faithful, **high-signal**,
machine-readable **XML** transcript on disk — every meaningful message in order,
tool calls with arguments, sub-agents nested inline, and the messy realities
(rewinds, compaction, interrupts, rejected calls) preserved and marked.
**Primary consumer is an LLM**; human-readability is secondary. Sourced
**entirely from AgentsView's parsed CLI** — no raw-JSONL parsing. Batches over
many sessions in one run.

### Data source — parsed AgentsView only (no `export`)

- Use only the **parsed** `agentsview` commands. **Never** call `session export`;
  **never** parse raw `.jsonl`. The whole dependency is AgentsView's parsed
  surface.
- Commands used:
  - `session list --format json` — enumerate sessions (selection). Children are
    excluded by default, which is what we want for top-level selection.
  - `session get <id> --json` — session metadata (the `<session>` header).
  - `session messages <id> --json --from <ord> --limit <n>` — the ordered
    conversation. **Default page is 100** — always pass an explicit `--limit`
    and page on `last_ordinal + 1`.
  - `session tool-calls <id> --json` — tool-call metadata incl.
    `subagent_session_id` (sub-agent links) and `tool_use_id`.
- A sub-agent is a normal session with an `agent-<hex>` id — query it with the
  same commands and recurse.

### What the parsed API gives, and the accepted losses

GET (all confirmed present): every message in order; assistant `thinking_text`;
tool calls with **full arguments** (`input_json`); fork structure (`source_uuid`
/ `source_parent_uuid`); interrupts and the compaction **summary** (as
`source_type=system` messages); sub-agent links; rejected-vs-error outcome
(derivable from the result text).

ACCEPTED LOSSES (consequences of dropping `export`, all consciously accepted):
- Full tool-output bodies. Outputs are low-value; the parsed `result_content` is
  **partial** anyway (≈complete for `Bash`, **empty** for `Read`). Truncate what
  we get at 2000 chars and move on.
- Contents of `@`-referenced files — the **filename** is kept, not the body.
- `pr-link` (a minor provenance marker).
- Compaction trigger / token counts (the **count** + the **summary** are kept).

### XML schema (kebab-case, entity-escaped)

- Root `<session>`; intrinsic metadata as **attributes**: id, project, agent,
  model, branch, cwd, started, ended, messages, compactions.
- Turns: `<user>` / `<assistant>`, each with `ord` (source ordinal). A slash
  command → `command="/goal"` attribute + args as the element text.
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
  forks.
- **Resume dedup:** collapse verbatim resume-duplicates by `source_uuid` (keep
  the first occurrence). Distinct from forks, which have *different*
  `source_uuid`s.

### Keep / drop policy (high-signal faithful)

Principle: KEEP user intent, assistant output, tool calls + (partial) outputs,
and structural markers for the messy realities. DROP harness plumbing,
telemetry, and duplicate injections of a real message. (Most plumbing record
types never reach us anyway — we read the parsed message stream, not raw
records.)

- KEEP: user / assistant messages; assistant thinking; tool calls + args +
  (partial) outputs; slash-command invocations (parse `<command-name>` →
  one clean `command="…"` line); the compaction summary message; interrupts.
- DROP: `is_system`/`isMeta` plumbing (context-usage, `<local-command-caveat>`);
  the `isMeta` expanded-prompt twin of a slash command; `local_command` stdout;
  harness telemetry. Dedup the queued-prompt triple down to the real user
  message.

### Proven facts (live exploration, agentsview v0.34.5)

- Sub-agents are standalone sessions (`agent-<hex>`), linked via the tool-call's
  `subagent_session_id`; observed nesting depth 1 (recursion handles deeper).
- Messages have **no** `source_subtype`; specials are `source_type=system`
  (+ `is_system`), distinguished only by content text.
- Resume re-emits messages verbatim (same `source_uuid`); edits **fork** (same
  `source_parent_uuid`, different `source_uuid`).
- `session messages` default `--limit` is **100**; ordinals are a sparse global
  index (gaps are normal); tool calls key to messages by ordinal; parallel tool
  calls share one ordinal.
- `result_content` (tool output in the parsed messages) is partial — ≈complete
  for `Bash`, empty for `Read`.
- Rejected vs error both look like failures; a denial begins "The user doesn't
  want to proceed…", an error is a `<tool_use_error>` block or raw output.
- Interrupt = a message with content exactly `[Request interrupted by user]`.

## Working notes

- **Layout:** logic in a `tools/transcript_export/` package; CLI entry at
  `tools/bin/transcript-export`; tests in `tools/tests/`.
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

- [ ] **T1 — Scaffold + green build.** Create the `tools/transcript_export/`
  package (`__init__.py`) and a `tools/bin/transcript-export` entry that imports
  it and prints usage. Wire it into the `tools/` project so ruff/mypy/pytest see
  it. Add one trivial unit test. `make -C tools check` green.
- [ ] **T2 — AgentsView client.** `client.py`: thin wrappers `session_get`,
  `session_messages` (paged via `--from`/`--limit`, default-page-100 aware),
  `session_tool_calls`, `session_list`. Shell out to `agentsview`, parse JSON,
  **fail loud** on nonzero exit. Unit tests mock `subprocess`. Green.
- [ ] **T3 — Message model + resume dedup.** A normalized message dataclass; an
  ordered list built from `session_messages`; collapse verbatim
  resume-duplicates by `source_uuid` (keep first). Unit tests with fixtures.
  Green.
- [ ] **T4 — Fork reconstruction.** Build the tree from
  `source_parent_uuid`→`source_uuid`; compute the live path (ancestors of the
  highest-ordinal message); collect abandoned branches per fork point. Unit test
  with a multi-branch fixture (incl. a nested fork). Green.
- [ ] **T5 — Record classification.** Classify each kept message: normal
  user/assistant; slash command (parse `<command-name>`/`<command-args>`);
  interrupt (`[Request interrupted by user]`); compaction summary; and which
  messages to DROP (isMeta plumbing, expanded-prompt twin). Per the Keep/drop
  policy in Design. Unit tests. Green.
- [ ] **T6 — Render: header + turns + thinking.** Entity-escaping helper;
  `<session>` header from `session_get`; `<user>`/`<assistant>` turns with `ord`;
  `<thinking>`. Pure function (model → XML string). Unit tests incl. escaping of
  `< > & "` and content that contains XML-looking text. Green.
- [ ] **T7 — Render: tool calls.** `<tool-call name id>` + `<args>` (raw JSON,
  escaped) + `<output chars truncated>` (truncate 2000); derive
  `outcome="rejected"|"error"` from result text. Unit tests. Green.
- [ ] **T8 — Render: markers + rewound branches.** `<compaction>`,
  `<interrupted/>`, and `<rewound-branch>` (abandoned branch in full fidelity at
  its fork point). Unit tests. Green.
- [ ] **T9 — Sub-agent recursion.** When a tool call has `subagent_session_id`,
  fetch the child and render it nested inside the `<tool-call>` as `<subagent>`,
  recursively, with cycle + depth guards. Unit tests with a mocked
  parent→child. Green.
- [ ] **T10 — CLI: selection + output.** Accept explicit ids, `--recent N`,
  `--all`; for each session render and write `<out_dir>/<id>.xml`. End-to-end
  wiring. Unit tests for selection logic (mocked `session_list`). Green.
- [ ] **T11 — Live-daemon integration tests.** Render a real recent session end
  to end against the live daemon; assert well-formed XML + structural invariants;
  exercise `get`/`messages`/`tool-calls`/`list`. Green.
- [ ] **T12 — Retire the prototype.** Delete `tools/transcript-export-prototype/`;
  update any README/pointers. `make -C tools check` green.
