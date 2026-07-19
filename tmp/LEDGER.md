# intake-batch ledger — dev-playbook

## Dashboard

| # | issue | stage | verdict (short) | waiting on |
|---|-------|-------|-----------------|------------|
| 208 | Workflow → Software Factory rename | ✅ ready-to-land | AFK-ready — full rename, labels lose file refs | landing nod |
| 207 | label-scheme drift cross-check | ✅ ready-to-land | close — premise refuted, check already exists | landing nod |
| 199 | fan-out guardrails | ✅ ready-to-land | guard language in the 4 fan-out files; cap dropped | landing nod |
| 184 | judgements dead ceremony (`--refuted`) | ✅ ready-to-land | AFK-ready — plain-language brief; enforcement-std changes come back to you | landing nod |
| 183 | standards-audit latency | ✅ ready-to-land | close — 0.62 s measured, premise refuted | landing nod |
| 169 | lint/audit vocabulary (pivoted) | ✅ ready-to-land | two-direction accounting done — 113 sites; scope flag: audit-vs-review fold-in | landing nod |

## ❓ Open asks — everything currently waiting on you

One item: the **batched nod** on the Landing checkpoint directly below —
respond per issue, or ratify all six at once. The one scope change since
your last ruling is flagged loudly in #169's entry: the reverse sweep found
a third vocabulary blur (LLM review passes called "audits"), and I propose
folding it into 169's mandate rather than minting a new issue.

Resolved-ask archive: the spawn-cap explanation and the probe-vs-fold
options live in the issue blocks' Decisions sections and in git history
(commit b3a0737's version of this section).

## Landing checkpoint — awaiting your nod

The nod authorizes the batch's FIRST GitHub writes: four-tuple labels and
rewritten briefs on 208/184/199/169, blocked-by edges, and closes with
findings comments on 207/183. (I read tmp/references/landing.md only after
the nod, per the skill.)

**#208 — rename "Workflow" → "Software Factory".** Brief: full rename of
our concept — the workflow/ directory and its four docs, the
standards/workflow.md card, every path cross-reference and dotfiles skill
pin, code/data docstrings, judgement declarations, and the internal rule id
`workflow.tuple-valid` (coordinated with its 9 test sites). Label
descriptions drop file references entirely (your ruling) and get
self-contained wording; one re-bootstrap per repo after merge. Untouched:
the Claude Code harness "workflows" feature, GitHub-Actions/generic uses,
frozen Decision Records; readings/ gets regenerated, not edited. Judgement
caches invalidate → re-run rides the change; OKF index descriptions move in
lockstep. Tuple: `category:maintenance` (no new capability) ·
`mode:direct` (mechanical, design already done by this investigation) ·
`tests:yes` (modifies pinned test fixtures) · `phase:tdd` (the graph routes
direct+tests:yes there).

**#207 — close.** Comment: premise refuted — the `scheme-vs-graph`
judgement already enforces label_scheme.json ↔ workflow.md agreement,
gated at pre-push (test_judgements_gate + make check-judgements), and a
live extraction found zero drift (17 labels match both sides). The doc↔JSON
seam is deliberately the judgement's job per label_scheme.py's docstring.

**#183 — close.** Comment: premise refuted — three warm runs measured
0.61–0.62 s (orchestrator re-verified 0.636 s), not the claimed 1–2 s; the
11 `--list-rules` subprocesses cost ~0.065 s each; and the hook is
dev-playbook-local (LOCAL_ONLY), so no consumer repo pays it. If it ever
matters, the existing Callable seam makes a cached/in-process swap clean.

**#184 — remove the unused `--refuted` ceremony.** Brief opens in plain
language: judgements-run carries a `--refuted` flag and a
`semantic-validation.refuted` rule that nothing ever uses — the
run-judgements skill records passes only; the rule exists solely so the
standards-audit bookkeeping check doesn't complain about the card citing
judgements-run. Remove flag, rule, and their tests, AND drop the card's
judgements-run Audit bullet in the same change (atomic, or the always-run
standards-audit reds between edits). Implementer section carries M1's exact
touch-list. Escalation trigger (your hard constraint): any edit to the
enforcement standard → stop and bring the plan to you first. Tuple:
`category:maintenance` · `mode:direct` · `tests:yes` (deletes/updates
tests) · `phase:tdd`.

**#199 — fan-out guard language.** Brief: add the guard clauses to the four
fan-out surfaces (issue-overwatch and run-judgements SKILL.md, ralph-loop.js,
scatter-gather.js), modeled on fill-issue-gaps' existing leaf clause:
bounded workers get fresh agents never forks; every worker prompt ends with
a leaf clause; state the agent count before launching; a silent bounded
worker means stop and investigate; the native /code-review runs only inside
a single-purpose wrapper. Anchored on the verified fact (the review
launched far too many agents); fork inheritance recorded as probable
mechanism. Tuple: `category:maintenance` · `mode:direct` · `tests:no`
(prose/skill edits, no test surface) · `phase:build`.

**#169 — audit/lint vocabulary.** Brief: CONTEXT.md gets the ruled
definitions — **audit** = detector run in a standard's context (matching
its existing glossary), **lint** = the fallback word outside standard
context and for third-party linters; docs may bridge ("audit — a lint for
standards") as analogy. Realign 113 sites, all listed with file:line and
suggested wording on disk: 68 lint-side (W2-A: 27 violations + 41
ex-borderline internals incl. `lint_cli`/`LintFinding`/`lint_findings`) and
45 audit-side (W3-A: 6 "Audited:" → "Surveyed:" in the third-party survey;
39 skill/doc sites where an LLM review pass is called an "audit" →
"review"). Judgment calls baked into the brief: enforcement.md:43 →
"review"; sdd-review "audits against the grammar" → "reviews against";
"audit log" in testing/conventions.md stays (universal term in a
hypothetical example). Untouchables: readings/ (regeneration is a candidate
ride-along), frozen DRs. OKF index↔frontmatter lockstep on the judgements
docs. Tuple: `category:maintenance` · `mode:direct` · `tests:yes` (renames
test-mirrored identifiers) · `phase:tdd`.
> ⚠ **SCOPE FLAG** — folding W3-A's audit-vs-review blur into 169 is the
> one decision not yet ratified by you. Alternative: a separate new issue.
> I recommend the fold: same definitional pass in CONTEXT.md, same
> mechanical sweep, and a split would touch the same files twice.

**Dependency picture** (blocked-by edges to be written):
- 208 and 184 are collision-free with each other → land first, in parallel.
- 199 blocked-by 208 (soft: both edit issue-overwatch/SKILL.md and other
  dotfiles pins of workflow.md paths).
- 169 blocked-by 184 (hard: runner.py, loader.py, test_rule_registry.py,
  the card, judgements docs), blocked-by 208 (hard: 169 edits lines inside
  files 208 renames/moves — workflow.md, skill-authoring.md), blocked-by
  199 (soft: issue-overwatch/SKILL.md again). The sweep lands last.
- Landing order: **208 ∥ 184 → 199 → 169**; 207 and 183 close on the nod.

## Δ log — on a repeat pass, read only the newest section

### Δ wave 3 + landing checkpoint (LATEST)

- **169**: W3-A returned — H-a REFUTED. 844 total hits; all 10 detectors
  verified tracing to standard cards (no orphan); 80 prose lines read
  per-line; **45 counterexamples in 2 clusters**: the third-party survey's
  "Audited:" lines (×6 → "Surveyed:") and the skill family calling
  LLM-driven review passes "audits" (×39 → "review" — violating CONTEXT.md's
  own glossary, Audit = a run of detectors). Orchestrator verified 4 sites +
  the glossary. Return persisted to tmp/worker-returns/W3-A. → ✅
  ready-to-land; scope flag (fold the blur into 169) goes to the nod.
- **batch**: landing checkpoint authored (section above) — 4
  briefs-in-miniature with four-tuples, 2 closes, edges, landing order
  208 ∥ 184 → 199 → 169. Awaiting the batched nod; wave 3 complete,
  manifest fully spent at 11.

### Δ checkpoint 2 — post-compact answers

- **199**: spawn cap DROPPED — human approved the drop recommendation
  ("everything you said in the last turn is approved"). Scope final: guard
  language in the 4 fan-out files, nothing else. → ✅ ready-to-land.
- **batch**: all human asks resolved; W3-A (reverse audit-sweep, wave 3)
  is the only thing between here and the landing checkpoint.
- **169**: borderline RESOLVED — the judgements-audit internals are
  in-standard-context ("this thing is literally an auditor"); internal code
  and naming go to audit vocabulary; docs say audit but may bridge to lint
  as an analogy. Workset: 27 + 41 = 68 sites. One open point remains: the
  reverse-direction sweep ("audit" outside standard contexts) — probe
  proposed at manifest +1. → ASK 2.
- **199**: piece 2 RATIFIED (guard language in the 4 fan-out files),
  absorbing piece 1's clauses at skill level, where the human expects agents
  to actually listen; piece 1 (rule file) REJECTED — "a sledgehammer";
  piece 4 (upstream report) REJECTED — "waste of time." Piece 3 (spawn cap):
  explanation delivered in Open asks #1; my recommendation revised to DROP
  (an effective cap collides with scatter-gather's 1,000-job envelope; the
  default-200 tier already exists). Human also flags the issue's fork
  narrative as unverified memory — the verified core is the agent-count
  blowout; the guard language binds regardless of mechanism. → ASK 1.

### Δ wave 2

- **POST-COMPACT RECOVERY (verified):** all four ready-to-land issues
  (208, 207, 184, 183) re-certified from disk state alone — ledger +
  worker-returns suffice to author every brief and closing comment with no
  session memory. No recovery probes needed.
- **RESUME STATE (post-compact, read first):** both open asks (199, 169) are
  deferred — the human compacted before answering. Next contact: take their
  answers, then present the landing checkpoint (per-issue brief-in-miniature,
  four-tuples, edges) for the batched nod. tmp/references/landing.md is read
  ONLY after the nod. Worker returns live in tmp/worker-returns/; lessons in
  tmp/LESSONS_LEARNED.md. No GitHub has been written.
- **199**: open-ask rewritten in full prose (human: prior version was "word
  salad" — over-compressed); answer deferred to post-compact.
- **169**: ask understood but answer deferred to post-compact.
- **batch**: all 10 worker returns persisted verbatim to `tmp/worker-returns/`
  (M1, M2, P1–P6, W2-A, W2-B) — compaction-proof; landing briefs author from
  these files, not from context memory. (Lesson 5.)

- **169**: reclassification under your pivot rule (W2-A): **27 violations** in 5 clusters (type-lint ×9, ref-audit-as-"linter" ×3, detector "Lint…" self-descriptions ×7, judgements "lint hook" ×3, test prose ×5); **41 borderline hits = one single question** — do the judgements-audit internals (`lint_cli`/`LintFinding`/`lint_findings` + test mirrors) count as "in the context of a standard"? Fleet evidence favors yes (every other carrier class is `Finding`). 45 legal-fallback, 136 untouchable. The issue's anti-lint grep rule is dead under the pivot. → ASK below.
- **199**: primary-doc research done (W2-B): local /code-review's agent spawning is **undocumented internals** executed by our own session (so rules do bind the spawner); fork inheritance documented but the re-execution hazard is **not** — real upstream doc gap; mechanical lever exists: `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` (default 200); a project skill named `code-review` would REPLACE the bundled one (rejected — loses native quality). I read workflow.md + issue-overwatch myself: the overwatch's one-line wrapper dispatch already isolates inherited context. Four-piece proposal delivered in the terminal. → ASK below.
- **208**: your decision recorded — label descriptions drop repo-file references entirely (labels never go stale against file moves again).
- **184**: you ratified keeping it after the plain-language translation; brief will be written that way (interior detail in an implementer section); hard constraint added: enforcement-standard changes come back to you before execution.
- **207 / 183**: your closes ratified; no new evidence. Closing comments will be succinct findings + reasons.

### Δ wave 1 (8 workers, all returned)

- 208: blast radius mapped (M2+P5, agree independently): ~32 our-concept files, zero consumer-pinned identifiers break; caveats = GitHub label descriptions, 17 pinned test strings, OKF index lockstep, judgement-cache re-run, frozen DRs exempt.
- 207: premise refuted (P6): `scheme-vs-graph` judgement already enforces JSON↔workflow.md at pre-push; zero live drift (17 labels match both sides).
- 199: 4 workspace fan-out surfaces have zero guardrails; no rule covers fork; incident's /code-review is harness-builtin (P4).
- 184: premise confirmed in code; names rotted (`judgements-run`, `semantic-validation.refuted`); removal atomic with card-bullet drop; full touch-list mapped (M1+P1).
- 183: 0.61–0.62 s measured (not 1–2 s), 11 subprocesses, LOCAL_ONLY (P2; orchestrator re-verified 0.636 s).
- 169: old inventory stale (7/8 paths moved) and 5× undercounted — 242 hits/48 files (P3). Superseded by the wave-2 pivot.

## Batch

issues: 208, 207, 199, 184, 183, 169 · wave: 3 COMPLETE · manifest: 8 (wave 1) + 2 (wave 2, human-directed) + 1 (wave 3, human-directed) spent: 11

Decision (human, verbatim): "Approved." — Wave-1 manifest, 2 Opus maps + 6
Sonnet probes (checkpoint 0)

Wave 2 (human-directed at checkpoint 1): probe W2-A — reclassify lint hits
under the pivot rule (169, approved "go"); worker W2-B — primary-doc lookup
on the native Claude Code code-review skill (199, human-directed:
"read the documentation before you propose a solution").

Batch findings: edges proposed 208→207 (moot if 207 closes) and 184→169
(file collisions: runner.py, loader.py, test_rule_registry.py, the card,
judgements/ docs). Consolidation: none warranted — probed. Cross-cutting:
readings/ generated artifacts are stale (lint-suite.html cites deleted
scripts; file-graph has phantom paths) — fix is regeneration, not editing;
candidate ride-along for 169. Naming rot is batch-wide: issues predate #205
(judgments→judgements) and #166 (detector renames); briefs must use current
names.

Decided without the human (batch): ledger lives at tmp/LEDGER.md, not the
worktree root — okf-audit treats root .md as concept docs and reds the commit;
tmp/ is this branch's sanctioned scratch (per commit 5a03cb0).

## Issue 208 — Rename "Workflow" to "Software Factory"

stage: ✅ ready-to-land
verdict: AFK-ready (brief assumes full rename incl. paths + internal rule id; label descriptions drop file references entirely)
ASK: none — ratify at landing.

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | workflow.md and the "Workflow" term are still current reality; no partial rename begun | SURVIVED | workflow/ tree + standards/workflow.md intact; ~599 hits / 68 files sweep (M2) |
| 2 | Rename blast radius is enumerable and mechanical; no consumer-facing identifier (hook names, label values) breaks — distribution.md warns consumer repos pin hook revs | SURVIVED w/ caveats | no hook id or script name carries "workflow"; BUT label descriptions "See workflow.md." mint onto GitHub in every repo (per human: drop file refs entirely + one re-bootstrap), 17 pinned strings in test_label_scheme.py:20-36, OKF index lockstep, judgement caches invalidate, frozen DRs exempt (P5) |
| 3 | "workflow" genuinely collides with Claude Code's workflows feature somewhere in-repo | SURVIVED | bucket-2 sites: dotfiles/dot-claude/workflows/*.js, settings.json:85 workflowKeywordTriggerEnabled, harness-recipes "Workflow runtime" |
| 4 | The "organize/improve/simplify" rider is separable scope (intent Q — human's call) | resolved | human dropped the rider — #208 is rename-only |

### Decisions (human, verbatim)
- "I'm ok removing 'simplify and improve' from the factory rename issue mandate (208). I agree that could be complex and might be too much for this batch workflow." (checkpoint 0)
- "208 caveat: '"See workflow.md." mint onto GitHub in every repo (re-bootstrap needed),' find but in the pass, remove reference to specific files in a github. Github should be labels only not references to Git files that will become stale again in the future at some point." (checkpoint 1) — interpreted: during the rename pass, label descriptions drop file references entirely (no "See <file>.md." successor); one final re-bootstrap, then descriptions can never go stale against file moves again.

### Decided without the human
### Probe log
- opus · M2: terrain map of workflow.md + label_scheme, rename blast radius, cross-check seams · returned — 3-bucket sweep, 5 fragilities, ordering: 208 before 207 (both center on workflow.md + label_scheme.json; a 207 checker would hard-code the path 208 moves)
- sonnet · P5: falsify "blast radius bounded/mechanical" · SURVIVED w/ caveats — 354 hits/74 files, all bucketed; zero consumer-pinned identifiers carry "workflow"; risks: frozen DRs must be exempted, workflow.tuple-valid is a 9-test-site internal rename, run-judgements SKILL.md is pure bucket-2 despite living in bucket-1 territory

## Issue 207 — label_scheme.json and workflow.md can drift silently

stage: ✅ ready-to-land
verdict: close — human-ratified at checkpoint 1 (premise refuted: scheme-vs-graph judgement already enforces this at pre-push)
ASK: none — closing comment lands after the batched nod.

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The docstring quote and the described two-source layout are still current | SURVIVED | quote verbatim at label_scheme.py:10-12; layout as described |
| 2 | No existing mechanism (hook, audit rule, judgement declaration, test) verifies the two agree | REFUTED | judgement `scheme-vs-graph` (judgements/code-matches-docs.yaml:69-81) covers exactly this, gated at pre-push via test_judgements_gate; orchestrator verified the declaration verbatim |
| 3 | The two artifacts are mechanically comparable — a deterministic cross-check is feasible | SURVIVED | probe extracted+matched both sides live: 7 fixed + 10 phase labels, zero drift today |
| 4 | Disposition (action / fold into 208 / record-only) is an intent decision | resolved | human: close as covered |

### Decisions (human, verbatim)
- "Oh. I DO WANT the problem fixed. By 'not proposing a fix' in the issue, it meant 'no specific method of fixing is proposed.' But yes the mission of the issue is to fix the problem as described." (checkpoint 0)
- "207 ok good finding. I'm ok closing this." (checkpoint 1)

### Decided without the human
### Probe log
- sonnet · P6: falsify "no cross-check exists"; check docstring; extract+compare both label inventories · H-a REFUTED (scheme-vs-graph judgement exists, pre-push-gated), H-b/H-c SURVIVED (no live drift)

## Issue 199 — Code Review Ran Wild Like Uncle Jeff Was Paying the Bill

stage: ✅ ready-to-land
verdict: AFK-ready — scope final (checkpoint 2): guard language in the 4 fan-out files (piece 2, absorbing piece 1's clauses: fresh-not-fork, leaf clause on every worker prompt, count-stating, silent-worker-means-stop, /code-review only via a single-purpose wrapper); rule file, upstream report, and spawn cap all rejected/dropped
ASK: none — ratify at landing.

### Incident narrative (preserved from the checkpoint-1 ask; mechanism caveat below)

A session was told to run a code review and then a second review skill. It
invoked the built-in `/code-review` skill, whose loaded instructions said to
launch 8 parallel "finder" agents. Per the issue's account it launched them
as forks — a fork inherits the entire conversation, including the original
multi-step directive — and at least one fork re-executed that directive,
spawning its own agents in turn. Result: ~37 agents, PR comments posted by
rogue children, no way to stop the grandchildren (TaskStop refused on
ownership grounds).

CAVEAT (human, checkpoint 2): the fork mechanism is unverified memory — "It
may be true, may not be." The verified core: "code review launched way too
many damn agents." The guard language binds regardless of mechanism — a leaf
clause stops any child from spawning, and count-stating surfaces a blowout
however it starts.

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The failure mode (fork inherits top-level directives and re-executes them) is accurately described and not mooted by harness changes | SURVIVED | docs confirm forks inherit the entire conversation; the re-execution RISK is undocumented upstream — no warning, no prevention guidance (sub-agents.md) |
| 5 | (new, W2-B) mechanical levers exist beyond prompting | facts | CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION (default 200, v2.1.212+, can't be disabled); depth-5 nesting cap fixed; project skill named code-review would REPLACE the bundled one (documented) — no wrap pattern documented; effort→agent-count link NOT documented, so the medium pin is heuristic |
| 2 | Workspace-authored skills that instruct agent fan-out lack leaf clauses / fork prohibitions | SURVIVED | 4 fan-out surfaces, zero guardrails: issue-overwatch SKILL.md:46, run-judgements SKILL.md:44, ralph-loop.js:88, scatter-gather.js:63-76; leaf-clause pattern exists at fill-issue-gaps:56 but nowhere on these |
| 3 | No existing rule file in dotfiles/dot-claude covers fork usage for fan-out workers | SURVIVED | rules/ has exactly 2 files (bash-commands, edit-in-dev-playbook); zero fork/subagent matches there or in CLAUDE.md |
| 4 | The fix surface is workspace-owned (rules + skills), not upstream-only | SURVIVED (narrowed) | incident's /code-review is harness-builtin (issue-overwatch:60 says so itself) — workspace can harden its own 4 surfaces + add a rule, cannot fix the builtin; BUT the builtin's fan-out instructions execute in OUR session, so our rules bind the spawner |

### Decisions (human, verbatim)
- "199- I'm open to (c) both But you think that's the answer? Just telling the agents not to repeat bad behaviors? I'm not quite certain this is going to work. take a closer look at workflow.md and the code review skills for the pr/code review nodes. They involve the *native* Claude Code code review skill (with the effort arguments we're trying to force to medium). You need to look up the anthropic primary documentation on that. And if you find two skills, one a plug in and one a native Claude code function, you can rest assured we are using the native Claude code function. […] It's tricky. It's different from our normal skills." (checkpoint 1)
- "199- I'm actually not sure from memory that /fork was the primary problem. It may be true, may not be. I know that's how it was written but that doesn't mean it is true. In general, "code review launched way too many damn agents." THAT is true at least! In terms of how to handle this, honestly, I'm really only optimistic about #2: adding guard language to the four fan out files. I don't like the rule files because I believe a rule file is just a sledgehammer that tries to cover everything all at once. If the agent will listen to the rule, then it will certainly listen to the skill. Indeed, it's more likely to listen to the skill, I believe. I'm not sure how the spawn cap works. You could try explaining that a little better to me. we're not gonna report to anthropic. That's a waste of time." (checkpoint 2) — interpreted: piece 2 yes, absorbing piece 1's guard clauses into the four files; pieces 1 and 4 no; piece 3 awaits the cap explanation (now in Open asks #1); the brief anchors on the verified fact (agent-count blowout) and treats fork inheritance as probable-but-unverified mechanism.
- "Otherwise, everything you said in the last turn is approved" (checkpoint 2) — resolves the last open piece: spawn cap dropped per recommendation (an effective cap collides with scatter-gather's 1,000-job envelope; default-200 tier already exists; count-stating in the guard language gives the visibility).

### Decided without the human
### Probe log
- sonnet · P4: inventory fan-out guardrails across dotfiles/dot-claude · SURVIVED ×3 ("fork" appears nowhere in the tree; no guardrail language anywhere)
- claude-code-guide · W2-B: primary-doc research on native /code-review, forks, spawn limits · returned — local /code-review's agent spawning is undocumented internals; fork inheritance documented but re-execution risk is not; session spawn cap env var + fixed depth-5 limit exist; same-name project skill replaces the bundled one
- orchestrator read (human-directed): workflow.md review sequence + issue-overwatch §3 — native dispatch is a fresh wrapper subagent whose whole context is "Run /code-review medium --comment" (+ model:opus pin); the incident session instead carried a multi-step top-level directive, which is exactly what the fork inherited

## Issue 184 — Remove the circular judgments.refuted ceremony forced by rule-matrix

stage: ✅ ready-to-land
verdict: AFK-ready — human ratified keeping it after translation; brief in plain exterior language (interior detail in an implementer section); HARD CONSTRAINT: human fully in the loop on any change to the enforcement standard
ASK: none — ratify at landing.

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | #155 is done and post-merge reality matches this issue's description | partly REFUTED | substance holds, names rotted: it's `judgements-run` (not judgments-run), rule id is `semantic-validation.refuted` (runner.py:35), card is semantic-validation |
| 2 | judgments.refuted / --refuted still exist and nothing else emits or reads them | SURVIVED | flag live at runner.py:193-199; whole-repo grep: only runner.py + its tests touch it; run-judgements skill records passes only (SKILL.md:54) |
| 3 | Naive deletion reds rule-matrix exactly as described | SURVIVED (refined) | M1: empty --list-rules is silent success → rule-matrix Direction-2 finding (standards_audit.py:339-349), not a crash; removal is atomic with dropping the card's judgements-run Audit bullet |
| 4 | Direction A (semantic-detector marker) is small and breaks no other detector's matrix check | reframed | M1: dropping the citation ≠ Direction B's dishonesty if removal ships atomically; hook-surfaces unaffected (judgements-run isn't a hook); full touch-list mapped incl. test_rule_registry.py:47,61 |

### Decisions (human, verbatim)
- "184- Okay, man. The way you just explained it jogged my memory, and it made me understand and remember why we wrote this issue. […] you should talk like that in the issue and instead of the hyper specific gobbley goop that was in there unless you think that will help the implementing agent, which is certainly might. Now I'll just say I'll be interested in how you change the enforcement standard because that is near and dear to my heart. So I want to be fully in the loop on plan to changes to the enforcement standard." (checkpoint 1)
- "184- bro I don't even understand what this issue is trying to say. Do you? I forget why I wrote this or what I thought the problem was when I did. […] It's complaining about a problem inside a black box that I don't understand. I think of 'judgements' as: 'CLI operation that checks the judgements all pass or are all cached as passing their hashes in the past.' The details of this ticket don't make sense to me because they're focused on the middle of the implementation, which is a black box from my perspective." (checkpoint 1)

### Decided without the human
- Checked #155 state myself (issue-reading, not delegated): CLOSED — declared dependency satisfied.

### Probe log
- opus · M1: detector-fleet terrain map · returned — per-issue touch-lists for 184/183/169, 6 fragilities, ordering: 184 atomic (rule + card bullet together), 184 before 169 (file collisions), soft 184-before-183
- sonnet · P1: verify post-#155 reality of judgments.refuted (exists? sole emitter? skill passes-only?) · SURVIVED ×3, with naming-rot caveat: real ids are `judgements-run` / `semantic-validation.refuted`; drift-guard test tests/test_rule_registry.py:47,61 pins RULES into --list-rules ground truth

## Issue 183 — standards-audit: consider reducing per-commit cold-start latency

stage: ✅ ready-to-land
verdict: close — human-ratified at checkpoint 1; closing comment must be succinct, accurate findings + reasons
ASK: none — closing comment lands after the batched nod.

### Decisions (human, verbatim)
- "183- fine to close. When closing an issue of post succint and accurate findings and reasons." (checkpoint 1)

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | Hook is still always_run: true; ~10 subprocess --list-rules reads per commit still current | SURVIVED | .pre-commit-config.yaml:91-96 always_run:true; 11 detectors cited today (issue said ~10) |
| 2 | Measured warm cost sits in the claimed 1–2s band | REFUTED | 3 warm runs ~0.61–0.62s; ~0.065s per --list-rules subprocess; orchestrator re-verified: 0.636s |
| 3 | The four candidate directions remain the live option set (nothing landed since #151 changes the calculus) | SURVIVED (weakened premise) | M1: the Callable seam (audit()/check_rule_matrix injection) makes cache/in-process swaps clean; but standards-audit is LOCAL_ONLY — cost is dev-playbook-local, and measured at 0.62s |

### Decided without the human
### Probe log
- sonnet · P2: confirm always_run + subprocess count, time warm runs · H-a/H-b SURVIVED, H-c REFUTED (0.62s, not 1–2s; counterexample verified by orchestrator)

## Issue 169 — Purge the residual "lint" vocabulary; standardize on "audit"

stage: ✅ ready-to-land
verdict: two-direction accounting complete — 113 sites, all with file:line + suggested wording on disk: 68 lint-side (W2-A: 27 violations + 41 ex-borderline internals) + 45 audit-side (W3-A: 6 survey "Audited:" → "Surveyed:", 39 LLM-review-pass "audit" → "review"); CONTEXT.md defines both terms, docs may bridge to lint as analogy; anti-lint grep rule dead under the pivot (enforcement, if ever, = a judgement)
ASK: none beyond the nod — the audit-vs-review fold-in is flagged in the Landing checkpoint's #169 entry.

### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The listed instances still exist at the listed paths (#155's reorganization may have moved judgments docs) | REFUTED | 7 of 8 paths stale (PR #205 moved judgments→judgements, docs/, claude-code/, instruments/); no `lint()` function exists at all — content survives, addresses don't (orchestrator verified) |
| 2 | The issue's inventory is incomplete — a fresh grep surfaces more | SURVIVED (5× under) | 242 hits / 48 files vs ~13 listed; missed: Makefile `lint` target (consumer-facing via canonical template!), stale generated readings/ datasheets, okf/python-audit docstrings, argparse texts, whole test surfaces |
| 3 | Renaming internal identifiers (loader:lint_cli console-script target) is contained; no external consumers | SURVIVED | M1: no hook-id/console-script-key/rule-id contains "lint" — no consumer-pin ripple; in-repo ripple: pyproject.toml:14, scripts/judgements-audit import, LintFinding pinned as string in test_rule_registry.py:46 |
| 4 | An anti-lint audit rule can exempt generic English without a big false-positive surface (design Q) | superseded | pivot makes "lint" legal outside standard contexts; a grep can't judge context — rule dropped from scope |

### Decisions (human, verbatim)
- "Reading your findings and the issue makes me consider a pivot: 'lint' is a very natural word in common usage in software engineering, and it has a meaning everyone understands and it is good. However, I chose to have 'the standard' be based on 'describe, audit, enforce, adopt' which led me to standardize on 'audit' […] But that could be an overcorrection. Instead, what if we specifically standardized the meaning of vocabulary so that 'lint' and 'audit' are both allowed (and both defined in CONTEXT.md). The difference is that 'audit' is appropriate any time we're in the context of a standard. Lint is a default fallback otherwise. This might also involve understanding how an audit is different or the same as a lint." (checkpoint 1)
- "169- good idea. go" (checkpoint 1, wave-2 reclassification probe)
- "169- Yes judgements-audit is called "audit" because it comes directly from a standard. Internal code and naming should say "audit" not lint since this thing is literally an auditor. Documentation should say audit but may bridge to lint as an analogy." (checkpoint 2)
- "Yes, send a Sonnet agent to do the reverse sweep for the word audit." (checkpoint 2 — manifest +1 approved; probe W3-A launched)

### Decided without the human
### Probe log
- sonnet · P3: fresh lint inventory vs issue's list · H-a REFUTED (paths stale), H-b REFUTED-as-complete (242 hits/48 files, bucket-1 5× undercounted); counterexamples verified by orchestrator (Makefile:8, lint-suite.html, judgements/ move)
- sonnet · W2-A: reclassify 249 hits under the pivot rule · H-a REFUTED (27 violations > ~15, in 5 clusters: type-lint ×9, ref-audit-"linter" ×3, detector "Lint…" docstrings/argparse ×7, judgements "lint hook" ×3, test prose ×5); 41 BORDERLINE = one bundled identifiers question; 45 legal-fallback; 136 untouchable (readings/ 121 + frozen DRs 15); orchestrator verified decisions_audit prog/description inconsistency + LintFinding outlier
- sonnet · W3-A: reverse sweep — falsify "every 'audit' is in-standard-context" · REFUTED — 844 hits, 684 classified (≈604 fleet identifiers, all 10 detectors verified tracing to a standard card; 80 prose lines read per-line); 45 counterexamples in 2 clusters (survey "Audited:" ×6; LLM review passes called "audits" ×39, against CONTEXT.md's own Audit-=-detector-run glossary); 4 near-line judgment calls flagged for the brief; orchestrator verified 4 sites + the glossary definition
