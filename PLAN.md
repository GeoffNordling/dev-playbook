# Software-factory cleanup — working plan

Working memory for branch `2026-07-30-software-factory-cleanup`. Survives compactions; re-read after any `/clear` or compaction to restore state. Not a deliverable — delete before merge (the root `PLAN.md` name is lint-excluded as a transient plan file).

## Context

- One branch, one PR; **everything rolls in here, including issues #276 and #273**.
- Already on branch: `107c920` — reviewers made judgment-blind; overwatch briefs the user in the terminal.

## End goals

1. **Two pauses** in the review/rework stretch (post-implementation only — the HITL front-end is separate scope, see goal 5):
   - **Pause 1 — review verdicts during rework cycles.** The overwatch escalates minimally, assuming no reader knowledge of the code/docs/PR/comments. Brief format, four parts: *current state, goal, proposed new state, specific example*. The user exists only in the terminal chat.
   - **Pause 2 — final PR review.** The product is presented 100% done: judgments green, merge message refreshed, verified push handed over, closing brief. Nothing left but the user's read and the merge.
2. **Dedicated judgments review node** at the end, after all review/rework cycles. Motivation: judgments are expensive, slow, and false-alarm-prone — keep user and agent attention off them during normal cycles.
3. **software-factory.md split** into sub-files (currently a 227-line monolith).
4. **Skills re-evaluated from scratch** against the improved workflow, plus a dedup pass into shared reference files with progressive disclosure.
5. **(added)** **Intake and design move outside the factory** — pre-factory intent extraction whose output is a factory-ready issue. sdd-specs is ambiguous (a spec encodes both intent and instruction — a spec is a kind of code) and gets its own focus session.

## Decisions so far

- Two-pauses scope = the review/rework stretch only.
- Intake + design: pre-factory. sdd-specs: undecided, own session.
- **Spike: remove the node from the graph/docs.** Keep `spike` values in `label_scheme.json` (may return; not a worry now). No spike skill ever existed — nothing to delete there.
- **Rules live in one place** — standing principle for every pass (e.g. the lockdown/cycle rules currently live in 3 places).
- Judgment-node specifics (label name, merge moving to its close = pause 2) are settled at the graph session, not before. Sketch on the table: `phase:judgments`; approve at review = "advance to judgments"; merge at the node's close.
- Push taps (YubiKey) can't be eliminated — mechanical, not cognitive; fold the push command into the adjacent brief.

## Roadmap — work in order

1. [ ] **Focus session: front door** — intake/design outside the factory; where the entry boundary sits; what "factory-ready" requires.
2. [ ] **Focus session: sdd-specs** — intent vs instruction; where it lives.
3. [ ] **Focus session: state-machine graph** — mermaid graph: judgments node, spike removal, entry edges from sessions 1–2, how the skills map onto the settled nodes.
4. [ ] **Restructure the docs** — split software-factory.md (sketch: spine + worktrees + dispatch + review; final shape follows the sessions); four-part brief format; final-presentation contract; one home per rule; re-point 9 inbound anchors; indexes + standards card; `label_scheme.json`.
5. [ ] **Rewrite issue-overwatch** + light touches (agent-view-overwatch, open-pr, intake). Overwatch currently restates the track rules and is the 7th copy of the comment-surfaces paragraph — cite, don't copy.
6. [ ] **#276 dedup** — design review of the draft's ten judgment calls R1–R10 first (design of record: issue #256, comment 5109029948), then the shared reference files + eight node-skill rewrites; includes the intake/tracker-operations dedup.
7. [ ] **#273** — design-it-twice fan-out, seam sketching, decompose-exit text → wherever design lands after session 1.

## Open questions

- **Front door (session 1, asked, awaiting answers):**
  - Overwatch handed an unready issue: hard refusal ("not factory-ready, run /intake first") vs a courtesy path running extraction inline?
  - Does `phase:design` leave the graph — every issue entering the factory at its implementation node, `## Approach` already authored?
- **sdd-specs (session 2):** in or out of the factory; how it's engaged.
- **Graph (session 3):** ratify the judgments node; entry edges; reconcile "the graph is the phase-label inventory" with keeping spike labels in the data while the node leaves the graph.
- **Doc split:** final file shape.
- **#276:** all ten judgment calls unruled; R1 (file placement) re-answered against the new directory layout.

## Key files and references

- `software-factory/software-factory.md` + `skill-authoring.md` — the docs under refactor.
- `dotfiles/dot-claude/skills/` — issue-overwatch, tdd, sdd-tdd, build, open-pr, {bug,code,sdd-code,doc}-pr-review, sdd-spec-review, intake, design, sdd-specs, run-judgments, agent-view-overwatch.
- `src/dev_playbook/label_scheme.json` — labels as policy-as-data; `scripts/bootstrap-labels` mints; consumer repos need a rerun after changes.
- Inbound links to software-factory.md: 12 files, 9 anchor references; ref-lint machine-checks them.
- #276 dedup draft: three reference files, per-skill rewrite maps, word accounting, R1–R10 — at issue #256 comment 5109029948.
