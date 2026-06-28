# Plan: Transcript-Export Fixes (review follow-ups)

A Ralph loop works this file top to bottom. Each iteration, a fresh agent reads
this plan and `PROGRESS.md`, completes **one** unfinished task, checks it off,
leaves the check gate green, appends one progress line, and commits. Everything
it needs is here.

## What this loop is

The `tools/transcript_export/` tool already exists, works, and ships a green
build. A review of its output against **real** Claude Code sessions found a set
of correctness bugs and missing fail-loud guards. This loop fixes them. It is
**not** a redesign — the architecture stays; these are targeted corrections,
each landed with a test that proves the fix against real data.

## Ground truth (facts found during review — trust these, don't re-derive)

- **Check gate:** `make -C tools check` (ruff format-check, ruff lint, mypy,
  pytest). Every task must leave it green. If ruff/pytest are missing, run
  `uv sync` in `tools/` first.
- **Live daemon is always on.** Real data needs no setup — just shell out:
  `agentsview session messages <id> --json` returns the parsed rows;
  `agentsview session list --format json` lists sessions newest-first. The CLI
  `tools/bin/transcript-export <out_dir> --recent N` renders real sessions.
- **Data-source constraint (already met — keep it):** read only the parsed
  messages API (`session list` / `get` / `messages`). Never parse raw `.jsonl`,
  never call `agentsview session export`.
- **Key files:** classification `tools/transcript_export/classify.py`; rendering
  `tools/transcript_export/render.py`; per-session entry point
  `tools/transcript_export/transcript.py` (`render_session`); fork logic
  `tools/transcript_export/forks.py`; dedup rule 1 `tools/transcript_export/model.py`.
  Tests: `tools/tests/test_transcript_export*.py`.
- **A test whose fixture is shaped unlike real data is worthless.** Two bugs
  below shipped green precisely because their fixtures used a row shape that never
  occurs. When you fix a bug, build the test fixture from the **real** row shape,
  verified against the live daemon — and where practical, add a live-daemon
  assertion.

## Finding live test sessions

To verify a fix against real data, pull a session that actually exhibits the
case. General tools:

- `agentsview session search "<text>" --json` — searches message/tool content;
  each hit carries a `session_id`.
- `agentsview session list --json` — filters/sorts session metadata
  (e.g. `--sort compactions:desc`). Run any subcommand with `--help` to confirm
  flags.

Known sessions on this machine that exhibit each case (good for eyeballing;
confirm one still exists with `agentsview session get <id> --json`, else fall
back to the search recipe):

- **Interrupts (F3):** `agentsview session search "[Request interrupted by user]" --json`.
  Session `4a157204-83b1-4eb0-a47a-958865ca2fd2` has several — real rows are
  `source_type="system"`, `source_subtype="interrupted"`.
- **Bare `[Bash]` haiku markers (F4):** sessions
  `0aff38bc-49ec-476f-82a0-7d5c1c744b77` and
  `774efbe3-81bc-46d6-8cec-7212621424c0` contain `claude-haiku-4-5` turns whose
  markers currently leak.
- **Forks (F2):** find structurally — a `source_parent_uuid` shared by ≥2
  messages with different `source_uuid`. `0aff38bc-…` has 12 rewind branches;
  `d45168f9-7715-4631-afe2-074f8fa2df85` has a clean 3-way fork.
- **Dedup triple (F5):** session `4a157204-…`, ordinals 79–81 — one user message
  re-emitted three times (same `source_parent_uuid`, different `source_uuid`).

## Done when

- Every task below is checked off.
- `make -C tools check` is green, with a new test for each fix.
- Each behaviour fix is verified against a real session from the live daemon.

## Tasks

Ordered: structural fail-loud guards first (they protect everything after), then
the behaviour bugs, then test hygiene and docs.

- [x] **F1 — XML well-formedness guard (production, fail-loud).** A rendered
  transcript is one `<session>…</session>` document. In `render_session`
  (`transcript.py`), after assembling the full document string and before
  returning it, parse it with a strict parser (`xml.etree.ElementTree.fromstring`)
  and re-raise any failure as a clear exception. This guarantees no run ever emits
  malformed XML (unclosed tag, stray close, illegal char) — it crashes at the
  source instead. Validate only the complete top-level document (not each nested
  `<subagent>` fragment). All 5 known real exports are already well-formed, so
  this must not change current output. Test: a deliberately-broken document raises.

- [x] **F2 — Forks conservation guard (fail-loud).** `reconstruct_forks`
  (`forks.py`) partitions messages into the live path plus abandoned branches.
  Add a check that **every input message lands in exactly one place** — live path
  or exactly one abandoned branch, none dropped, none duplicated — and **raise**
  if violated. This turns any future mis-partition (e.g. an unexpected/crossing
  fork shape) into a loud crash instead of silent message loss. Tests:
  conservation holds on a multi-fork input; a constructed violation raises.

- [x] **F3 — Render interrupts (currently silently dropped).** Real interrupt
  rows are `source_type="system"`, `source_subtype="interrupted"`,
  `content="[Request interrupted by user]"`. In `classify.py` the
  `source_type=="system" → DROP` branch runs **before** the interrupt check, so
  every real interrupt is dropped and no `<interrupted/>` ever renders. Fix:
  recognise the interrupt **before** the system→DROP rule (mirror how compaction
  is recognised first). Fix the interrupt test fixtures to the **real** shape
  (`source_type="system"`, `source_subtype="interrupted"`) — they currently use
  `source_type="user"`, which never occurs and masked the bug. Verify a real
  interrupting session (e.g. a recent one) yields `<interrupted/>` in its export.

- [ ] **F4 — Marker-stripping: handle bare markers, then fail loud on mismatch.**
  The prose marker-stripper's regex only matches `[ToolName: detail]` (with a
  colon), but `claude-haiku-4-5` emits bare `[ToolName]` (no colon), so its
  markers leak into prose (confirmed in real exports). (a) Broaden the pattern to
  also match the bare `[ToolName]` form. (b) Then make a count mismatch **fail
  loud**: if the number of matched marker-lines does not equal the message's
  tool-call count, **raise** — do not silently return the prose untouched (that
  silent fallback is the current bug). Tests: a bare-`[Bash]` haiku turn strips
  cleanly; a real mismatch raises; broadening must not eat real prose (guard a
  standalone `[Word: detail]`-shaped prose line). Verify no markers leak on a real
  haiku-model session.

- [ ] **F5 — Dedup rule 2: match the whole message, not just text.**
  `collapse_adjacent_repeats` (`classify.py`) collapses adjacent messages on
  `(role, content)` alone, so it can drop a genuinely distinct turn (e.g. a
  fail-then-pass retry with identical prose but a different tool result).
  Decision: collapse two adjacent messages **only when identical across all
  readily-available distinguishing fields** — content, tool_calls (including their
  result content), thinking text, and `source_parent_uuid`. The real machine
  artifact (re-emitted queued/injection doubles) shares all of these, so it still
  collapses; anything genuinely different is spared. Tests: a real triple-emission
  collapses to one; a same-prose / different-tool-result retry is preserved.

- [ ] **F6 — Live tests fail (not skip) when the daemon is unreachable.** In
  `tools/tests/test_transcript_export_live.py`, remove the
  `skipif(not _RECENT, …)` guard. This machine always runs the daemon, so an
  unreachable daemon means something is actually wrong — the suite must **fail
  loudly**, not skip and hide it.

- [ ] **F7 — Document the tool in `tools/README.md`.** Add a `transcript-export`
  row under the **Utility scripts** table (it's an ad-hoc, human-run tool, not a
  pre-commit validator): one line on purpose plus the command form
  (`transcript-export <out_dir> <session_id… | --recent N | --all>`), pointing at
  `--help` for detail. Terse, matching the existing table style.

## Working notes

Iterations may append durable facts here — keep them short.
