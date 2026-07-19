# intake-batch ledger — dev-playbook

## Batch
issues: 208, 207, 199, 184, 183, 169 · wave: 1 COMPLETE (8/8 returned) · manifest: 8 approved spent: 8

Wave 2 (human-directed at checkpoint 1): probe W2-A — reclassify lint hits
under the pivot rule (169, approved "go"); worker W2-B — primary-doc lookup
on the native Claude Code code-review skill (199, human-directed:
"read the documentation before you propose a solution"). spent: 8+2.

Wave-1 batch findings: edges proposed 208→207 (only if 207 lives) and 184→169
(file collisions: runner.py, loader.py, test_rule_registry.py, the card,
judgements/ docs). Consolidation: none warranted — probed. Cross-cutting:
readings/ generated artifacts are stale (lint-suite.html cites deleted
scripts; file-graph has phantom paths) — fix is regeneration, not editing;
candidate ride-along for 169. Naming rot is batch-wide: issues predate #205
(judgments→judgements) and #166 (detector renames); briefs must use current
names.

Decision (human, verbatim): "Approved." — Wave-1 manifest, 2 Opus maps + 6
Sonnet probes (checkpoint 0)

Decided without the human (batch): ledger lives at tmp/LEDGER.md, not the
worktree root — okf-audit treats root .md as concept docs and reds the commit;
tmp/ is this branch's sanctioned scratch (per commit 5a03cb0).

## Issue 208 — Rename "Workflow" to "Software Factory"
stage: ready-to-land
verdict: AFK-ready (brief assumes full rename incl. paths + internal rule id; objections at checkpoint 1)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | workflow.md and the "Workflow" term are still current reality; no partial rename begun | SURVIVED | workflow/ tree + standards/workflow.md intact; ~599 hits / 68 files sweep (M2) |
| 2 | Rename blast radius is enumerable and mechanical; no consumer-facing identifier (hook names, label values) breaks — distribution.md warns consumer repos pin hook revs | SURVIVED w/ caveats | no hook id or script name carries "workflow"; BUT label descriptions "See workflow.md." mint onto GitHub in every repo (re-bootstrap needed), 17 pinned strings in test_label_scheme.py:20-36, OKF index lockstep, judgement caches invalidate |
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
stage: ready-to-land
verdict: close — human-ratified at checkpoint 1 (premise refuted: scheme-vs-graph judgement already enforces this at pre-push)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The docstring quote and the described two-source layout are still current | SURVIVED | quote verbatim at label_scheme.py:10-12; layout as described |
| 2 | No existing mechanism (hook, audit rule, judgement declaration, test) verifies the two agree | REFUTED | judgement `scheme-vs-graph` (judgements/code-matches-docs.yaml:69-81) covers exactly this, gated at pre-push via test_judgements_gate; orchestrator verified the declaration verbatim |
| 3 | The two artifacts are mechanically comparable — a deterministic cross-check is feasible | SURVIVED | probe extracted+matched both sides live: 7 fixed + 10 phase labels, zero drift today |
| 4 | Disposition (action / fold into 208 / record-only) is an intent decision | resolved | human: mission is to fix the problem; method left to design |
### Decisions (human, verbatim)
- "Oh. I DO WANT the problem fixed. By 'not proposing a fix' in the issue, it meant 'no specific method of fixing is proposed.' But yes the mission of the issue is to fix the problem as described." (checkpoint 0)
- "207 ok good finding. I'm ok closing this." (checkpoint 1)
### Decided without the human
### Probe log
- sonnet · P6: falsify "no cross-check exists"; check docstring; extract+compare both label inventories · H-a REFUTED (scheme-vs-graph judgement exists, pre-push-gated), H-b/H-c SURVIVED (no live drift)

## Issue 199 — Code Review Ran Wild Like Uncle Jeff Was Paying the Bill
stage: blocked-on-human
verdict: needs deeper look before proposing — human open to (c) both but skeptical that "telling agents" works; directed a read of the native code-review skill's primary docs + workflow.md review nodes first
### Decisions (human, verbatim)
- "199- I'm open to (c) both But you think that's the answer? Just telling the agents not to repeat bad behaviors? I'm not quite certain this is going to work. take a closer look at workflow.md and the code review skills for the pr/code review nodes. They involve the *native* Claude Code code review skill (with the effort arguments we're trying to force to medium). You need to look up the anthropic primary documentation on that. And if you find two skills, one a plug in and one a native Claude code function, you can rest assured we are using the native Claude code function. […] It's tricky. It's different from our normal skills." (checkpoint 1)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The failure mode (fork inherits top-level directives and re-executes them) is accurately described and not mooted by harness changes | SURVIVED | docs confirm forks inherit the entire conversation; the re-execution RISK is undocumented upstream — no warning, no prevention guidance (sub-agents.md) |
| 5 | (new, W2-B) mechanical levers exist beyond prompting | facts | CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION (default 200, v2.1.212+, can't be disabled); depth-5 nesting cap fixed; project skill named code-review would REPLACE the bundled one (documented) — no wrap pattern documented; effort→agent-count link NOT documented, so the medium pin is heuristic |
| 2 | Workspace-authored skills that instruct agent fan-out lack leaf clauses / fork prohibitions | SURVIVED | 4 fan-out surfaces, zero guardrails: issue-overwatch SKILL.md:46, run-judgements SKILL.md:44, ralph-loop.js:88, scatter-gather.js:63-76; leaf-clause pattern exists at fill-issue-gaps:56 but nowhere on these |
| 3 | No existing rule file in dotfiles/dot-claude covers fork usage for fan-out workers | SURVIVED | rules/ has exactly 2 files (bash-commands, edit-in-dev-playbook); zero fork/subagent matches there or in CLAUDE.md |
| 4 | The fix surface is workspace-owned (rules + skills), not upstream-only | SURVIVED (narrowed) | incident's /code-review is harness-builtin (issue-overwatch:60 says so itself) — workspace can harden its own 4 surfaces + add a rule, cannot fix the builtin |
### Decisions (human, verbatim)
### Decided without the human
### Probe log
- sonnet · P4: inventory fan-out guardrails across dotfiles/dot-claude · SURVIVED ×3 ("fork" appears nowhere in the tree; no guardrail language anywhere)
- claude-code-guide · W2-B: primary-doc research on native /code-review, forks, spawn limits · returned — local /code-review's agent spawning is undocumented internals; fork inheritance documented but re-execution risk is not; session spawn cap env var + fixed depth-5 limit exist; same-name project skill replaces the bundled one
- orchestrator read (human-directed): workflow.md review sequence + issue-overwatch §3 — native dispatch is a fresh wrapper subagent whose whole context is "Run /code-review medium --comment" (+ model:opus pin); the incident session instead carried a multi-step top-level directive, which is exactly what the fork inherited

## Issue 184 — Remove the circular judgments.refuted ceremony forced by rule-matrix
stage: blocked-on-human
verdict: AFK-ready — human ratified keeping it after translation; brief to be written in plain exterior language (interior detail in an implementer section); HARD CONSTRAINT: human must be fully in the loop on any change to the enforcement standard
### Decisions (human, verbatim)
- "184- Okay, man. The way you just explained it jogged my memory, and it made me understand and remember why we wrote this issue. […] you should talk like that in the issue and instead of the hyper specific gobbley goop that was in there unless you think that will help the implementing agent, which is certainly might. Now I'll just say I'll be interested in how you change the enforcement standard because that is near and dear to my heart. So I want to be fully in the loop on plan to changes to the enforcement standard." (checkpoint 1)
- "184- bro I don't even understand what this issue is trying to say. Do you? I forget why I wrote this or what I thought the problem was when I did. […] It's complaining about a problem inside a black box that I don't understand. I think of 'judgements' as: 'CLI operation that checks the judgements all pass or are all cached as passing their hashes in the past.' The details of this ticket don't make sense to me because they're focused on the middle of the implementation, which is a black box from my perspective." (checkpoint 1)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | #155 is done and post-merge reality matches this issue's description | partly REFUTED | substance holds, names rotted: it's `judgements-run` (not judgments-run), rule id is `semantic-validation.refuted` (runner.py:35), card is semantic-validation |
| 2 | judgments.refuted / --refuted still exist and nothing else emits or reads them | SURVIVED | flag live at runner.py:193-199; whole-repo grep: only runner.py + its tests touch it; run-judgements skill records passes only (SKILL.md:54) |
| 3 | Naive deletion reds rule-matrix exactly as described | SURVIVED (refined) | M1: empty --list-rules is silent success → rule-matrix Direction-2 finding (standards_audit.py:339-349), not a crash; removal is atomic with dropping the card's judgements-run Audit bullet |
| 4 | Direction A (semantic-detector marker) is small and breaks no other detector's matrix check | reframed | M1: dropping the citation ≠ Direction B's dishonesty if removal ships atomically; hook-surfaces unaffected (judgements-run isn't a hook); full touch-list mapped incl. test_rule_registry.py:47,61 |
### Decisions (human, verbatim)
### Decided without the human
- Checked #155 state myself (issue-reading, not delegated): CLOSED — declared dependency satisfied.
### Probe log
- opus · M1: detector-fleet terrain map · returned — per-issue touch-lists for 184/183/169, 6 fragilities, ordering: 184 atomic (rule + card bullet together), 184 before 169 (file collisions), soft 184-before-183
- sonnet · P1: verify post-#155 reality of judgments.refuted (exists? sole emitter? skill passes-only?) · SURVIVED ×3, with naming-rot caveat: real ids are `judgements-run` / `semantic-validation.refuted`; drift-guard test tests/test_rule_registry.py:47,61 pins RULES into --list-rules ground truth

## Issue 183 — standards-audit: consider reducing per-commit cold-start latency
stage: ready-to-land
verdict: close — human-ratified at checkpoint 1; closing comment must be succinct, accurate findings + reasons
### Decisions (human, verbatim)
- "183- fine to close. When closing an issue of post succint and accurate findings and reasons." (checkpoint 1)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | Hook is still always_run: true; ~10 subprocess --list-rules reads per commit still current | SURVIVED | .pre-commit-config.yaml:91-96 always_run:true; 11 detectors cited today (issue said ~10) |
| 2 | Measured warm cost sits in the claimed 1–2s band | REFUTED | 3 warm runs ~0.61–0.62s; ~0.065s per --list-rules subprocess; orchestrator re-verified: 0.636s |
| 3 | The four candidate directions remain the live option set (nothing landed since #151 changes the calculus) | SURVIVED (weakened premise) | M1: the Callable seam (audit()/check_rule_matrix injection) makes cache/in-process swaps clean; but standards-audit is LOCAL_ONLY — cost is dev-playbook-local, and measured at 0.62s |
### Decisions (human, verbatim)
### Decided without the human
### Probe log
- sonnet · P2: confirm always_run + subprocess count, time warm runs · H-a/H-b SURVIVED, H-c REFUTED (0.62s, not 1–2s; counterexample verified by orchestrator)

## Issue 169 — Purge the residual "lint" vocabulary; standardize on "audit"
stage: investigating
verdict: PIVOTED by human at checkpoint 1 — no longer a purge; now: define both terms in CONTEXT.md ("audit" = in the context of a standard; "lint" = default fallback otherwise) and realign only usages violating that rule. Wave-2 reclassification probe approved ("good idea. go") and launched.
### Decisions (human, verbatim)
- "Reading your findings and the issue makes me consider a pivot: 'lint' is a very natural word in common usage in software engineering, and it has a meaning everyone understands and it is good. However, I chose to have 'the standard' be based on 'describe, audit, enforce, adopt' which led me to standardize on 'audit' […] But that could be an overcorrection. Instead, what if we specifically standardized the meaning of vocabulary so that 'lint' and 'audit' are both allowed (and both defined in CONTEXT.md). The difference is that 'audit' is appropriate any time we're in the context of a standard. Lint is a default fallback otherwise. This might also involve understanding how an audit is different or the same as a lint." (checkpoint 1)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The listed instances still exist at the listed paths (#155's reorganization may have moved judgments docs) | REFUTED | 7 of 8 paths stale (PR #205 moved judgments→judgements, docs/, claude-code/, instruments/); no `lint()` function exists at all — content survives, addresses don't (orchestrator verified) |
| 2 | The issue's inventory is incomplete — a fresh grep surfaces more | SURVIVED (5× under) | 242 hits / 48 files vs ~13 listed; missed: Makefile `lint` target (consumer-facing via canonical template!), stale generated readings/ datasheets, okf/python-audit docstrings, argparse texts, whole test surfaces |
| 3 | Renaming internal identifiers (loader:lint_cli console-script target) is contained; no external consumers | SURVIVED | M1: no hook-id/console-script-key/rule-id contains "lint" — no consumer-pin ripple; in-repo ripple: pyproject.toml:14, scripts/judgements-audit import, LintFinding pinned as string in test_rule_registry.py:46 |
| 4 | An anti-lint audit rule can exempt generic English without a big false-positive surface (design Q) | weakened | ~40+ of 242 hits permanently unrenamable: docs/decisions/** (immutable by standard), ruff [tool.ruff.lint*] TOML + its readers/tests, third-party lines, vendored skills — rule needs standing exemption list |
### Decisions (human, verbatim)
### Decided without the human
### Probe log
- sonnet · P3: fresh lint inventory vs issue's list · H-a REFUTED (paths stale), H-b REFUTED-as-complete (242 hits/48 files, bucket-1 5× undercounted); counterexamples verified by orchestrator (Makefile:8, lint-suite.html, judgements/ move)
