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
- **Client API (T2, in `transcript_export/client.py`):** `session_list()`,
  `session_get(id)`, `session_messages(id, page=100)` each take an injectable
  `runner: Callable = subprocess.run` (the github.py humble-boundary pattern);
  `session_messages` returns the flat list of message rows (already paged to
  exhaustion), the others return the raw dict payload. Failures raise
  `AgentsViewError`. Reuse these in later tasks — do not re-shell `agentsview`.
- **Message model (T3, in `transcript_export/model.py`):** frozen `Message` and
  `ToolCall` dataclasses + `message_from_row` / `tool_call_from_row` builders,
  `collapse_resume_duplicates` (rule 1, keep-first by `source_uuid`), and
  `normalize_messages(rows)` (map every row then apply rule 1, input order
  preserved). Downstream tasks build on `Message` — do not re-parse raw row
  dicts. `Message` carries `source_parent_uuid` (None when absent) and `ordinal`
  for T4's tree/live-path walk; rule 2 (adjacent-repeat) is **not** applied yet —
  add it in T5.
- **Fork reconstruction (T4, in `transcript_export/forks.py`):**
  `reconstruct_forks(messages) -> ForkReconstruction` with `live_path:
  tuple[Message, ...]` (root→tip ancestor chain of the highest-ordinal message)
  and `abandoned_branches: dict[str | None, tuple[MessageNode, ...]]` keyed by
  fork point — the live-path parent's `source_uuid`, or the absent/None parent
  uuid for a root-level fork. `MessageNode` (message + ordinal-sorted children
  tuple) carries each abandoned subtree in full fidelity, so nested forks inside
  an abandoned branch are preserved as that head's `children`. T8 renders these
  as `<rewound-branch>` at their fork point; it consumes this structure rather
  than re-walking the tree.
- **Classification (T5, in `transcript_export/classify.py`):** `MessageKind` enum
  (`USER`/`ASSISTANT`/`SLASH_COMMAND`/`INTERRUPT`/`COMPACTION`/`DROP`),
  `classify(message) -> MessageKind` (compaction-boundary check *before*
  system->drop, since the boundary is `source_type=system` but kept; unexpected
  `source_type` raises), `collapse_adjacent_repeats` (dedup rule 2), and
  `keep_messages(messages)` = drop plumbing **then** rule 2 (order matters: a
  plumbing message wedged between two copies of a real message must be removed
  first so the copies become adjacent). `keep_messages` returns `list[Message]`,
  not kinds — render tasks call `classify` per message; rule 1 stays upstream in
  `normalize_messages`. Slash-command / interrupt are content refinements on a
  user turn (`content.startswith("/")` / `content == "[Request interrupted by
  user]"`).
- **Rendering (T6, in `transcript_export/render.py`):** `escape(text)` covers all
  five entities (`&` first to avoid double-escaping), reused for **both** element
  text and attribute values; `render_session_open(meta)` emits the `<session …>`
  open tag from a `session get` payload (`id` required/fail-loud, other attrs
  omitted when None, zero counts kept; caller appends `</session>`);
  `render_turn(message)` dispatches on `classify` to a `<user>` / slash-command
  `<user command="/cmd">args</user>` / `<assistant ord model><thinking>…</thinking>prose</assistant>`
  element, and **fails loud** on a non-turn (interrupt/compaction/drop) — those
  route through separate marker paths. Live-verified the `session get` header keys
  match the mapping (id/project/agent/cwd 1:1, git_branch/started_at/ended_at/
  message_count/compaction_count renamed).
- **Tool-call rendering + marker stripping (T7, in `transcript_export/render.py`):**
  `render_tool_call(tool_call)` emits `<tool-call name id [outcome]>` with `<args>`
  (escaped `input_json`) and `<output chars truncated>` (escaped `result_content`,
  cut at `TOOL_OUTPUT_TRUNCATION=2000`). `chars` = `result_content_length` (the
  API's authoritative full length — verified to differ by a few chars from
  `len(result_content)` due to whitespace trimming, and the *only* length for
  empty Read/ToolSearch bodies); `truncated` = `len(result_content) > 2000`.
  `outcome`: `"rejected"` when output starts with `"The user doesn't want to
  proceed"`, else `"error"` when it contains `"<tool_use_error>"`, else omitted
  (rejection checked first). `strip_tool_markers(content, tool_call_count)` removes
  the trailing `[ToolName: detail]` / `$ command` block: there is **exactly one
  `[Word: detail]` marker line per tool call** (live-verified across 554
  tool-bearing messages — `_TOOL_MARKER` regex, zero mismatches), so it cuts at the
  `tool_call_count`-th marker line from the end (handles multi-line `$` commands and
  parallel calls); fewer markers than calls → content returned untouched (never eat
  prose). `render_turn` now strips markers from prose and, for an assistant turn,
  appends one `render_tool_call` per `tool_calls[]` entry after thinking + prose.
  **Sub-agent nesting (`subagent_session_id` → `<subagent>` inside `<tool-call>`)
  is T9** — `render_tool_call` does not yet take child data.
- **Markers + rewound branches (T8, in `transcript_export/render.py`):**
  `render_compaction(message)` → `<compaction>summary</compaction>` (escaped
  `content`, no attributes — matches the schema literally; fails loud on a
  non-compaction); `render_interrupted(message)` → self-closing
  `<interrupted ord="…"/>` (fails loud on a non-interrupt). `render_message(message)`
  is the **single per-message dispatcher** a transcript walk uses: COMPACTION /
  INTERRUPT → their renderers, DROP → `""` (so callers append unconditionally),
  else `render_turn`. T10's live-path walk should reuse `render_message`, not
  re-dispatch. `render_rewound_branch(node: MessageNode)` renders ONE abandoned
  branch head as `<rewound-branch>` in full fidelity via `render_message` per node;
  a **nested** fork (node with >1 child) keeps the highest-ordinal child inline and
  wraps each lower-ordinal sibling in its own nested `<rewound-branch>` (recursive,
  chronological order). T10 emits one `<rewound-branch>` per head in the
  `abandoned_branches[fork_point]` tuple, at its fork point. 12 new unit tests.
- The reference prototype (`tools/transcript-export-prototype/render_transcript.py`)
  is **plain-text and uses `export`** — directional reference only. Do **not**
  copy its `export` usage or its dedup-by-`id` bug (dedup on `source_uuid`).
  Delete the whole prototype dir in the final task.
- **Sub-agent recursion + the session walk (T9, in `transcript_export/transcript.py`):**
  `render_session(session_id, runner=subprocess.run)` is the **single
  per-session entry point** — it `session_get`s the header, renders the body, and
  wraps it in `<session …>…</session>`. **T10 must reuse `render_session`
  unchanged** (just add CLI selection + write `<out_dir>/<id>.xml`); the full
  live-path walk now lives here, not in the CLI. `_render_body` is the shared
  walk for both `<session>` and nested `<subagent>`: it runs the pipeline
  `keep_messages(normalize_messages(rows))` → `reconstruct_forks`, emits any
  abandoned branch whose fork point is off the live path **up front**, then walks
  the live path emitting `render_message` per node followed by
  `render_rewound_branch` for each `abandoned_branches[source_uuid]` head.
  Sub-agent expansion is threaded as an **injected callback**: `render_tool_call`
  / `render_turn` / `render_message` / `render_rewound_branch` now take an
  optional `render_subagent: Callable[[str], str] | None` (default None = pure
  render, no expansion — keeps every earlier test green). `_subagent_renderer`
  closes over `visited`/`depth` and returns that callback: it `session_get`s the
  child for its `message_count` (→ `messages` attr, omitted if absent), renders
  the body via `_render_body`, and emits `<subagent id messages>…</subagent>`.
  **Guards:** `visited` (seeded with the root id) catches a cycle →
  `<subagent id omitted="cycle"/>`; `depth+1 > MAX_SUBAGENT_DEPTH` (8) →
  `omitted="depth"` — both self-closing placeholders, never silent drops. 10 new
  unit tests drive `render_session` against a fake daemon (one runner dispatching
  `get`/`messages` from a `{id: {"meta","rows"}}` map).
- **CLI (T10, in `transcript_export/cli.py`):** `main(argv, runner=subprocess.run,
  render=render_session)` parses args, selects ids, then writes one
  `<out_dir>/<id>.xml` per session (`mkdir(parents, exist_ok)` first — idempotent
  overwrite). `_parse_args` enforces **exactly one** selection mode
  (`sum([bool(ids), recent is not None, all]) != 1` → `parser.error`) and
  `--recent N > 0`. `select_session_ids(explicit_ids, recent, select_all, runner)`
  is the pure selection unit: explicit ids pass through with **no** daemon call;
  `--recent`/`--all` read `session_list(runner)["sessions"]` (already newest-first,
  default sort `recent`) and slice. `main` injects `render` so the file-output
  path is unit-tested with a stub (no daemon); `runner` is threaded into both
  selection and rendering. The `bin/transcript-export` shim is unchanged.
- **RESOLVED in T11 — `source_uuid` KeyError + control chars.** Two real-data
  crashes are fixed: (1) a `source_subtype="queued_command"` preview row has **no
  `source_uuid`** — `message_from_row` now reads `row.get("source_uuid")`
  (`Message.source_uuid` is `str | None`), `collapse_resume_duplicates` skips
  uuid-less rows (they can't be resume re-emissions), and `classify` **drops**
  `queued_command` as plumbing (it is a preview re-emitted later as a real user
  message; keeping it would orphan it from the fork tree). NOTE: the PLAN had
  expected rule 2 to dedup these, but the preview has no uuid and is re-emitted —
  dropping by subtype is correct, and rule 2 still guards other injection doubles.
  (2) Real tool output carries ANSI/control bytes (bare ESC `0x1b`) that XML 1.0
  forbids even as entities; `escape` now strips characters outside the XML 1.0
  legal set (`_XML_INVALID`) before entity-escaping. `forks.reconstruct_forks`
  now fails loud (`_uuid` helper) if a uuid-less message reaches it, since
  `keep_messages` must drop them first.
- **CRITICAL FINDING in T11 — fork reconstruction is broken on real data (→ T12).**
  The whole `source_parent_uuid`→`source_uuid` tree premise is **false** for the
  parsed messages API: a "message" aggregates several raw records, and the next
  message's `source_parent_uuid` points at an *internal* raw record (a tool
  result) of the previous message, not at its `source_uuid`. Measured: parent
  resolves to a message in the set **0/62** times (774efbe3) and **2/196**
  (d45168f9). Consequence: `_live_path` collapses to the single highest-ordinal
  message and **every other message renders as a `<rewound-branch>`** (a fork-free
  session: 25 wrappers + 1 real turn). The *fork signal that DOES survive* is a
  **shared `source_parent_uuid`** — d45168f9's 3-way fork shows up as one parent
  with children at ordinals 128/135/145, exactly the documented fork. Redesign
  (T12): treat **ordinal order as the live spine**; detect forks as parents shared
  by ≥2 messages; an abandoned sibling's branch is the contiguous ordinal range
  `[sibling_ord, next_sibling_ord)`, with the highest-ordinal sibling staying on
  the live path. This supersedes the old "pipeline-ordering" worry (keep_messages
  before reconstruct_forks) — that was a symptom; the tree never connecting is the
  cause. The xfail test `test_forkfree_stream_with_nonresolving_parents_is_all_live`
  encodes the target contract.
- **DONE in T12 — ordinal-spine fork reconstruction.** `forks.reconstruct_forks`
  no longer walks a `source_parent_uuid`→`source_uuid` tree. It now sorts by
  **ordinal** (the live spine), detects forks as a **shared `source_parent_uuid`**
  (≥2 messages), and for each fork the **highest-ordinal sibling stays live** while
  each lower sibling heads an abandoned branch owning the contiguous ordinal range
  `[sibling_ord, next_sibling_ord)`. Internals: `_abandoned_ranges` (one range per
  lower sibling), `_outermost` (drop ranges nested in another so they recurse
  instead — outermost ranges are pairwise disjoint), `_segment` (spine = msgs not in
  any outermost range; branches recurse via `_build_branch`→`_chain`), and `_chain`
  threads a sub-spine into one `MessageNode` chain (next message = highest-ordinal
  child; nested-fork branches = earlier children). **Contract change consumers must
  know:** `abandoned_branches` is now keyed by the **live sibling's `source_uuid`**
  (the message a branch was abandoned *for*) and typed `dict[str, …]` (no more
  `None`/parent keys); the head-of-session never carries branches before it. The
  `_render_body` walk now emits each fork point's `<rewound-branch>`es **before**
  its live message (was: after the parent). MessageNode + `render_rewound_branch`
  are unchanged. Verified on real session d45168f9: full live path (37 user + 231
  assistant turns) with exactly the 2 documented abandoned branches, vs the old
  near-all-rewound collapse.

## Tasks

- [x] **T1 — Scaffold + green build.** Create the `tools/transcript_export/`
  package (`__init__.py`) and a `tools/bin/transcript-export` entry that imports
  it and prints usage. Wire it into the `tools/` project so ruff/mypy/pytest see
  it. Add one trivial unit test. `make -C tools check` green.
- [x] **T2 — AgentsView client.** `client.py`: thin wrappers `session_list`,
  `session_get`, `session_messages` (paged via `--from`/`--limit`,
  default-page-100 aware). Shell out to `agentsview`, parse JSON, **fail loud**
  on nonzero exit. Unit tests mock `subprocess`. Green.
- [x] **T3 — Message model + resume dedup.** A normalized message dataclass; an
  ordered list built from `session_messages`; collapse verbatim
  resume-duplicates by `source_uuid` (keep first). Unit tests with fixtures.
  Green.
- [x] **T4 — Fork reconstruction.** Build the tree from
  `source_parent_uuid`→`source_uuid`; compute the live path (ancestors of the
  highest-ordinal message); collect abandoned branches per fork point. Unit test
  with a multi-branch fixture (incl. a nested fork). Green.
- [x] **T5 — Record classification.** Key off `source_type`/`source_subtype`,
  **not** `role` (the compaction boundary is `role=assistant` but
  `source_type=system`). Classify each message: normal user/assistant; slash
  command (user `content` starts with `/`); interrupt
  (`[Request interrupted by user]`); compaction summary
  (`source_subtype="compact_boundary"`); DROP = `source_type="system"` except the
  compaction summary (e.g. `task_notification`). Apply the two dedup rules from
  Reconstruction. Per the Keep/drop policy in Design. Unit tests. Green.
- [x] **T6 — Render: header + turns + thinking.** Entity-escaping helper;
  `<session>` header from `session_get`; `<user>`/`<assistant>` turns with `ord`;
  `<thinking>`. Pure function (model → XML string). Unit tests incl. escaping of
  `< > & "` and content that contains XML-looking text. Green.
- [x] **T7 — Render: tool calls.** From each message's `tool_calls[]`:
  `<tool-call name id>` + `<args>` (`input_json`, escaped) + `<output chars
  truncated>` (`result_content`, truncate 2000; empty for Read/ToolSearch).
  Derive `outcome="rejected"|"error"` from the output text. Unit tests. Green.
- [x] **T8 — Render: markers + rewound branches.** `<compaction>`,
  `<interrupted/>`, and `<rewound-branch>` (abandoned branch in full fidelity at
  its fork point). Unit tests. Green.
- [x] **T9 — Sub-agent recursion.** When a `tool_calls[]` entry has
  `subagent_session_id`, fetch that child session and render it nested inside the
  `<tool-call>` as `<subagent>`, recursively, with cycle + depth guards. Unit
  tests with a mocked parent→child. Green.
- [x] **T10 — CLI: selection + output.** Accept explicit ids, `--recent N`,
  `--all`; for each session render and write `<out_dir>/<id>.xml`. End-to-end
  wiring. Unit tests for selection logic (mocked `session_list`). Green.
- [x] **T11 — Live-daemon integration tests.** Render a real recent session end
  to end against the live daemon; assert well-formed XML + structural invariants;
  exercise `list`/`get`/`messages`. Green.
- [x] **T12 — Fix fork reconstruction (ordinal-spine redesign).** T11 proved the
  current `reconstruct_forks` is broken on real data: `source_parent_uuid` points
  at unsurfaced raw sub-records, so the parent→uuid tree never connects, the live
  path collapses to one message, and a fork-free session renders almost entirely
  inside `<rewound-branch>` (e.g. 25 wrappers, 1 real turn). Redesign so the
  **ordinal order is the live-path spine** and forks are detected by a
  **shared `source_parent_uuid`** (≥2 messages, the actual fork signal); abandoned
  branches occupy the contiguous ordinal range from each lower-ordinal sibling up
  to the next sibling under that parent, the highest-ordinal sibling staying live.
  Flip the `strict=True` xfail `test_forkfree_stream_with_nonresolving_parents_is_all_live`
  (in `tests/test_transcript_export_forks.py`) to passing, add fixtures for a real
  fork shape, and re-run the live integration tests. See the Working note below.
  `make -C tools check` green.
- [x] **T13 — Retire the prototype.** Delete `tools/transcript-export-prototype/`;
  update any README/pointers. `make -C tools check` green.
