# intake-batch ledger — dev-playbook

## Dashboard

| # | issue | stage | verdict (short) | waiting on |
|---|-------|-------|-----------------|------------|
| 208 | Workflow → Software Factory rename | ✅ ready-to-land | AFK-ready — full rename, labels lose file refs | landing nod |
| 207 | label-scheme drift cross-check | ✅ ready-to-land | close — premise refuted, check already exists | landing nod |
| 199 | fork-recursion guardrails | 🟡 blocked-on-human | 4-piece proposal delivered | **your yes/no + cap number** |
| 184 | judgements dead ceremony (`--refuted`) | ✅ ready-to-land | AFK-ready — plain-language brief; enforcement-std changes come back to you | landing nod |
| 183 | standards-audit latency | ✅ ready-to-land | close — 0.62 s measured, premise refuted | landing nod |
| 169 | lint/audit vocabulary (pivoted) | 🟡 blocked-on-human | 27 violations ready; 41 borderline = one question | **your borderline call** |

## ❓ Open asks — everything currently waiting on you

1. **#199 — the fork-recursion incident. Deferred to post-compact; written
   out in full here so nothing depends on session memory.**

   **What happened (the incident the issue records).** A session was told to
   run a code review and then a second review skill. It invoked the built-in
   `/code-review` skill, whose loaded instructions said to launch 8 parallel
   "finder" agents. The session launched them as **forks**. A fork inherits
   the entire conversation — including the original "run the review, then run
   the other skill" instruction — and at least one fork re-executed that
   whole directive on its own, spawning its own agents in turn. Result: ~37
   agents, PR comments posted by rogue children, and no way to stop the
   grandchildren (TaskStop refused on ownership grounds).

   **What investigation established (wave 1 + wave 2):**
   - Four workspace files instruct launching parallel agents, and none of
     them carries any guard language: the issue-overwatch skill, the
     run-judgements skill, and the two workflow scripts ralph-loop.js and
     scatter-gather.js. No rule file about subagent use exists at all. (The
     guard-language pattern does exist in one skill, fill-issue-gaps, so
     there is house precedent.)
   - The built-in `/code-review` is not a sealed program. Its instructions
     load into OUR session, and OUR agent is the one that chooses fork vs
     fresh when obeying them. So a workspace rule genuinely binds the agent
     doing the spawning — "telling agents" is not wishful in this specific
     failure, because the teller and the spawner share one context.
   - The fork hazard is real and UNDOCUMENTED upstream: Anthropic's docs say
     forks inherit the whole conversation, but never warn that a fork can
     re-execute inherited instructions, and offer no prevention guidance.
   - Our own overwatch design already contains the main protection: it runs
     `/code-review` inside a wrapper subagent whose entire conversation is
     the one line "Run /code-review medium --comment", so a fork born in
     there inherits nothing dangerous. The incident happened in a session
     that carried a rich multi-step directive instead — exactly what the
     wrapper pattern prevents.
   - One hard mechanical lever exists that works even if every agent
     ignores every rule: the env var CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION
     (default 200). Set lower, the harness itself refuses to spawn agent
     N+1 and fails loudly.

   **The proposal — four independent pieces, answer yes/no to each:**
   1. **Write a rule file** under dotfiles/dot-claude/rules/ that teaches
      every session: bounded worker tasks get fresh agents, never forks;
      every worker prompt ends with a "you are a leaf — do not spawn agents,
      do not invoke skills, do not write" clause; before launching a
      multi-agent skill, state how many agents it will run; a bounded worker
      that goes silent is a signal to stop and investigate, not wait; and
      the native /code-review runs only inside a single-purpose wrapper
      agent, never inline in a session with other pending directives.
   2. **Add that same guard language to the four fan-out files** named above,
      so an agent following any of them verbatim is bound even if it never
      read the rule.
   3. **Set the spawn cap** in workspace settings. Needs a number from you:
      25 would have strangled this incident (37 agents) but could choke a
      legitimately big scatter-gather run; 50 still stops runaway recursion
      and leaves headroom. Or say "drop it" and we rely on pieces 1–2.
   4. **Draft an upstream report to Anthropic** describing the undocumented
      fork re-execution hazard (they document the inheritance, not the risk).

   **My recommendation: yes to 1, 2, and 4; a cap of 50 for 3.**
2. **#169 — the one borderline call:** do the judgements-audit internals
   (`lint_cli`, `LintFinding`, `lint_findings` + their test mirrors, ~41
   sites) count as "in the context of a standard" and get renamed to audit
   vocabulary? Evidence favors yes — `LintFinding` is the fleet's lone
   non-`Finding` carrier and the console script is already `judgements-audit`
   — cost is ~41 sites of internal churn.

## Δ log — on a repeat pass, read only the newest section

### Δ wave 2 (LATEST)

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

issues: 208, 207, 199, 184, 183, 169 · wave: 2 COMPLETE · manifest: 8 (wave 1) + 2 (wave 2, human-directed) spent: 10

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

stage: 🟡 blocked-on-human
verdict: four-piece proposal delivered (post-W2-B)

> ❓ **ASK** — yes/no on the proposal's four pieces + a cap number. Full text in [Open asks](#-open-asks--everything-currently-waiting-on-you) #1.

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

stage: 🟡 blocked-on-human
verdict: pivoted (checkpoint 1) to "define both terms in CONTEXT.md; realign violations only." 27 violations in 5 clusters are ready work; anti-lint grep rule dead under the pivot (enforcement, if ever, = a judgement).
> ❓ **ASK** — the one borderline call on renaming the judgements-audit internals. Full text in [Open asks](#-open-asks--everything-currently-waiting-on-you) #2.

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

### Decided without the human
### Probe log
- sonnet · P3: fresh lint inventory vs issue's list · H-a REFUTED (paths stale), H-b REFUTED-as-complete (242 hits/48 files, bucket-1 5× undercounted); counterexamples verified by orchestrator (Makefile:8, lint-suite.html, judgements/ move)
- sonnet · W2-A: reclassify 249 hits under the pivot rule · H-a REFUTED (27 violations > ~15, in 5 clusters: type-lint ×9, ref-audit-"linter" ×3, detector "Lint…" docstrings/argparse ×7, judgements "lint hook" ×3, test prose ×5); 41 BORDERLINE = one bundled identifiers question; 45 legal-fallback; 136 untouchable (readings/ 121 + frozen DRs 15); orchestrator verified decisions_audit prog/description inconsistency + LintFinding outlier
