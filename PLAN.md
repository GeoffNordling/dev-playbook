# Software-factory cleanup — working plan

Working memory for branch `2026-07-30-software-factory-cleanup`. Re-read after any `/clear` or compaction to restore state. Each unit closes by updating this file: decisions in, questions out, checkbox ticked. Not a deliverable — delete before merge (root `PLAN.md` is lint-excluded as transient).

## Context

- One branch, one PR; everything rolls in here. Issues #276 and #273 are subsumed below (U4, U6) — they close when this PR lands.
- Already on branch: `107c920` (reviewers judgment-blind; overwatch briefs in terminal), `51b6bf3` (this file), `8538b3d` (orchestrate tweak).
- **Sidequest landed (uncommitted):** agent-facing voice. `conventions.md` claimed repo-lint enforced the first-person ban over skills and rules; it only ever inspected `CLAUDE.md`. Widened the rule to first-party skill and rule bodies, added `me` to the banned tokens, exempted vendored `.agents/` skills and quoted speech, fixed every violation it surfaced, and deleted the `caveman` and `zoom-out` vendored skills. Consumer impact at the next pin bump: none — all three governed repos scan clean.

## Operating model

Two terminals, side by side. This file is the sole handoff artifact: any fresh session, either side, must be able to resume from it alone.

- **Left — the orchestrator (Fable).** Runs the design sessions with the user, sharpens each unit's brief here before launch, keeps this file current, delegates deep dives to Opus/Sonnet subagents (naming the model tier per dispatch), and never executes units itself. `/clear` between sessions; this file restores state.
- **Right — one active implementation session (Opus).** Executes the last briefed-and-aligned unit. Launch prompt, pasted fresh per unit (one line):

  `Confirm you are in the worktree ~/workspace/dev-playbook/.claude/worktrees/2026-07-30-software-factory-cleanup on branch 2026-07-30-software-factory-cleanup — if not, enter it with the EnterWorktree tool (path=.claude/worktrees/2026-07-30-software-factory-cleanup). Then read PLAN.md at its root and execute the next unchecked unit exactly as briefed. I am present — ask me the moment intent is ambiguous; never improvise. When done: update PLAN.md (tick the unit, record decisions and deviations), report, and stop before committing.`

- **The user is in the loop throughout** — this is not the factory and nothing is AFK. Execution sessions ask the user on the spot instead of improvising; the user reviews each unit's diff in VS Code and says when to commit (one commit per unit, so the PR reads unit-by-unit).
- **Both sessions share this one worktree and branch.** For the orchestrator: re-read PLAN.md before editing it (the implementer updates it at unit close); don't edit factory files while a unit is in flight — brief-sharpening in PLAN.md and design-session notes only; `git status`/`git diff` will show the implementer's work-in-progress — expected, not an anomaly; any commit stages named files only, never `git add -A`. For the implementer: PLAN.md may carry fresher briefs than your launch context — the file on disk wins.
- Runtime skills are stowed from the **main checkout**, so nothing edited in this worktree changes live behavior until merge; main's review skills stay usable on this PR at the end.

## End goals

1. **Two pauses** in the review/rework stretch (post-implementation only):
   - **Pause 1 — review verdicts during rework cycles.** Overwatch escalates minimally, assuming no reader knowledge of code/docs/PR/comments. Brief format, four parts: *current state, goal, proposed new state, specific example*. The user exists only in the terminal chat.
   - **Pause 2 — final PR review.** Presented 100% done: judgments green, merge message refreshed, verified push handed over, closing brief. Nothing left but the user's read and the merge.
2. **Dedicated judgments node** at the end, after all review/rework cycles — judgments are expensive, slow, false-alarm-prone; keep attention off them during normal cycles.
3. **software-factory.md split** into sub-files (currently a 227-line monolith).
4. **Skills re-evaluated from scratch**, plus dedup into shared reference files with progressive disclosure.
5. **Intake and design move outside the factory** — pre-factory intent extraction producing a factory-ready issue.
6. **SDD frozen** (ratified 2026-07-30) — the factory refuses SDD work fail-loud; no SDD modernization in this pass.

## Decisions so far

- Two-pauses scope = the review/rework stretch only.
- Intake + design: pre-factory.
- **SDD freeze (ratified):** graph marks the SDD subgraph frozen; front door stops minting `mode:sdd`; overwatch orienting onto any `phase:sdd-*` issue escalates "SDD temporarily disabled." Skills stay on disk untouched; labels stay in the data (tests asserting label rows keep passing); the sdd-specs focus session is cancelled; #276 scope shrinks to the live skills.
- Spike: node removed from graph/docs; `spike` labels stay in the data.
- Rules live in one place — standing principle for every pass.
- Judgment-node specifics settle at U2. Sketch: `phase:judgments`; approve at review = advance to judgments; merge at the node's close = pause 2.
- Push taps (YubiKey) can't be eliminated — fold the push command into the adjacent brief.

## Units — work in order

Each unit lands whole before the next starts. U4→U5 is a real dependency (overwatch cites U4's files); U6 needs only U1+U3.

**Next:** U0 is briefed and ready to launch on the right; U1 (front door) runs on the left.

- [ ] **U0 — SDD freeze.** Annotate, don't restructure (U2/U3 redraw the graph later). One authoritative freeze rule in `software-factory/software-factory.md`: the SDD path is frozen — intake must not mint `mode:sdd`, and an overwatch orienting onto any `phase:sdd-*` issue escalates "SDD temporarily disabled" instead of dispatching. In the mermaid graph, keep the SDD subgraph but mark it frozen (retitle the subgraph; annotate the `intake -->|mode:sdd|` edge). Leave the skill-table rows, the four sdd-* skills on disk, the label data, and all code untouched (workspace-lint's `mode:sdd ⇒ tests:yes` pairing stays valid for existing issues). Check `intake/SKILL.md`'s mode-decision text: if it would still instruct minting `mode:sdd`, add the minimal deference to the graph's freeze rule — no rewrite (that's U6). Acceptance: `make check` green; the factory docs carry exactly one freeze rule.
- [ ] **U1 — front door (design session, HITL).** The intent-heavy one. Decide: where the boundary sits; what "factory-ready" requires; how pre-factory work is represented on the tracker — `phase:intake` is workspace-lint's only "not yet in scope" sentinel (`_post_intake()`), the highest-leverage call; who owns decomposition (documented in two standards, implemented in neither skill); the `## Approach` contract (today written by design, defined by no standard, checked by no lint, read by no downstream skill); where pre-factory design prototypes without an issue worktree; fate of the parallel front doors (intake-batch already models the end state — "no issue lands at `phase:design`"; candidate-promote hard-depends on /intake's return contract; fill-issue-gaps is a third readiness pass).
- [ ] **U2 — the graph (design session, HITL).** Ratify judgments node + two-pause structure; spike removal; frozen-SDD representation; entry edges per U1; reconcile "the graph IS the phase-label inventory" with retained spike/sdd label values; map skills onto settled nodes.
- [ ] **U3 — doc restructure.** Split software-factory.md per U1/U2; author the four-part brief format and final-presentation contract; one home per rule; re-point 12 inbound files / 9 anchors (ref-lint validates anchors; okf-lint forces index entries + frontmatter); `label_scheme.json` edits; fix un-linted stale refs: `scripts/bootstrap-labels` + `label_scheme.py` docstrings cite software-factory.md, `scripts/README.md:134` claims bootstrap-labels is "auto-invoked by /intake" (false), `dotfiles/settings/base.json` allows stale skill names `Skill(sdd-agent-spec-review)`/`Skill(sdd-agent-code-review)`. No consumer pin bump (doc/label/dotfiles changes don't touch the published playbook-lint hook); consumers re-run bootstrap-labels after label changes.
- [ ] **U4 — #276 dedup** (design of record: issue #256 comment 5109029948; scope minus frozen SDD skills). Rule R1–R10 first, then three reference files flat under `software-factory/` (`review-contract.md` Standard, `pr-feedback.md` Guide, `refactor-catalogue.md` Guide opening with the new Fowler smallest-step rule), then rewrite live citers: code-pr-review, doc-pr-review, bug-pr-review (partial), tdd, build. **New absorbed-block candidate found this session:** the "Judgments are not yours" clause (added by 107c920, postdates the draft) is now ×4 across review skills → belongs in review-contract.md. R1–R10 one-liners: R1 placement dir (re-answer against the new split layout); R2 overwatch as 7th comment-surfaces citer (rec: yes, lands in U5); R3 bug-pr-review verbatim constraint (rec: partial citer); R4 deliberately-not-extracted list (rec: accept); R5 near-duplicate variations a–f need per-item rulings (sdd items moot under freeze); R6 doc-pr-review's degraded copy — extraction silently upgrades it, call out in PR body; R7 contract-wins clause — generic rule in reference, skill-local naming clause (sdd-tdd variant moot); R8 sdd-tdd drift (moot under freeze); R9 OKF types Standard/Guide/Guide; R10 unpinned cross-repo reads (rec: accept, existing class).
- [ ] **U5 — overwatch rewrite** + agent-view-overwatch and open-pr light touches. Encodes the two-pause briefs; runs the judgments node (machinery unchanged: run-judgments skill → judgments-run plan/render/record CLIs → machine-local SQLite seen-set; endgame text re-homes from overwatch §6 into the node); cites U4's references instead of carrying the 7th comment-surfaces copy.
- [ ] **U6 — front-door implementation** per U1: new intake/design homes; **#273 lands in design** — design-it-twice parallel fan-out (cheap variant: fan out 3–4 agents on minimize-surface / max-flexibility / common-caller / ports-and-adapters axes only when the interview flags the public surface as load-bearing; compare on depth, locality, seam placement), seam sketching before writing, decompose-exit text (no round-trip through intake); intake/tracker-operations dedup (intake ~L91–106 cites `standards/tracking/tracker-operations.md` instead of carrying gh recipes); re-point candidate-promote / intake-batch / fill-issue-gaps; workspace-lint `_post_intake` change per U1 + its tests.
- [ ] **U7 — closeout.** Delete PLAN.md; full gate; PR body notes (R6 silent upgrade; consumer action: bootstrap-labels rerun); final presentation per pause-2 contract.

## Open questions

- **U1 session:** unready issue → hard refusal vs courtesy inline extraction? Does `phase:design` leave the graph entirely? Plus the five U1 decision points listed above.
- **U2 session:** judgments-node label/edges; graph-vs-label-inventory invariant wording.
- **U4:** the R1–R10 rulings.

## System map (scout digest, 2026-07-30)

- **Judgments:** declarations in `judgments/*.yaml` → content-addressed SHA-256 keys (root-invariant) → machine-local SQLite seen-set (`~/.cache/skipcache/seen.sqlite`). Pytest gate `assert_judgment_cached`; `SKIP_JUDGMENTS=1` default (visible skip); `make check-judgments` arms; canonical pre-push hook runs it; `--no-verify` skips it (the factory's intermediary pushes). Only /run-judgments (main loop, scatter-gather Workflow) fills the cache. Docs: `standards/judgments/*`, `standards/semantic-validation.md`.
- **Automation surface:** ref-lint validates `~/workspace` citations incl. `#fragment` anchors against GitHub-style heading slugs (skills are rootless → Citation form correct there; fixed-root docs must use Links). okf-lint: index freshness + frontmatter `type`. skill-lint: frontmatter, name=dir, model/effort enums, references/ one level deep, dotfiles symlink mirror. standards-lint: card cells; rule-matrix ties `standards/software-factory.md`'s Audit cell to workspace-lint's emitted rule ids. workspace-lint hardcodes: `_post_intake()` sentinel, `mode:sdd⇒tests:yes` / `spike⇒tests:no` pairings, BUILD/SPIKE_HEADINGS mirroring issues.md. Single published hook (playbook-lint); pin bump only if detector logic changes — none planned.
- **SDD blast radius:** two independent layers — the factory layer (freeze target: 4 sdd-* skills, graph subgraph, `mode:sdd` + 4 phase values, intake/overwatch routing) and the build-layer mechanism (`Makefile.sdd`, repo-lint `Layers.sdd`, standards/build docs) — the latter untouched by the freeze.
- **Front door:** 43 couplings cataloged (Opus scout, in transcript); the real-decision subset is in U1 above; the rest are mechanical renames.

## Key files

- `software-factory/software-factory.md` + `skill-authoring.md` — docs under refactor.
- `dotfiles/dot-claude/skills/` — issue-overwatch, tdd, build, open-pr, {bug,code,doc}-pr-review, intake, design, run-judgments, agent-view-overwatch (+ frozen: sdd-specs, sdd-tdd, sdd-spec-review, sdd-code-pr-review).
- `src/dev_playbook/label_scheme.json`, `scripts/bootstrap-labels`, `src/dev_playbook/workspace_lint.py`.
- #276 design of record: issue #256 comment 5109029948 (full R1–R10 text and per-skill rewrite maps).
