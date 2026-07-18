# intake-batch ledger — dev-playbook

## Batch
issues: 208, 207, 199, 184, 183, 169 · wave: 1 · manifest: 8 approved spent: 8

Decision (human, verbatim): "Approved." — Wave-1 manifest, 2 Opus maps + 6
Sonnet probes (checkpoint 0)

Decided without the human (batch): ledger lives at tmp/LEDGER.md, not the
worktree root — okf-audit treats root .md as concept docs and reds the commit;
tmp/ is this branch's sanctioned scratch (per commit 5a03cb0).

## Issue 208 — Rename "Workflow" to "Software Factory"
stage: investigating
verdict: — (early read: bigger than it looks — mechanical rename + open-ended "simplify" rider)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | workflow.md and the "Workflow" term are still current reality; no partial rename begun | untested | — |
| 2 | Rename blast radius is enumerable and mechanical; no consumer-facing identifier (hook names, label values) breaks — distribution.md warns consumer repos pin hook revs | untested | — |
| 3 | "workflow" genuinely collides with Claude Code's workflows feature somewhere in-repo | untested | — |
| 4 | The "organize/improve/simplify" rider is separable scope (intent Q — human's call) | resolved | human dropped the rider — #208 is rename-only |
### Decisions (human, verbatim)
- "I'm ok removing 'simplify and improve' from the factory rename issue mandate (208). I agree that could be complex and might be too much for this batch workflow." (checkpoint 0)
### Decided without the human
### Probe log

## Issue 207 — label_scheme.json and workflow.md can drift silently
stage: investigating
verdict: — (early read: needs your call — issue is flag-only, "not proposing a fix here")
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The docstring quote and the described two-source layout are still current | untested | — |
| 2 | No existing mechanism (hook, audit rule, judgement declaration, test) verifies the two agree | untested | — |
| 3 | The two artifacts are mechanically comparable — a deterministic cross-check is feasible | untested | — |
| 4 | Disposition (action / fold into 208 / record-only) is an intent decision | resolved | human: mission is to fix the problem; method left to design |
### Decisions (human, verbatim)
- "Oh. I DO WANT the problem fixed. By 'not proposing a fix' in the issue, it meant 'no specific method of fixing is proposed.' But yes the mission of the issue is to fix the problem as described." (checkpoint 0)
### Decided without the human
### Probe log

## Issue 199 — Code Review Ran Wild Like Uncle Jeff Was Paying the Bill
stage: investigating
verdict: —
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The failure mode (fork inherits top-level directives and re-executes them) is accurately described and not mooted by harness changes | untested | — |
| 2 | Workspace-authored skills that instruct agent fan-out lack leaf clauses / fork prohibitions | untested | — |
| 3 | No existing rule file in dotfiles/dot-claude covers fork usage for fan-out workers | untested | — |
| 4 | The fix surface is workspace-owned (rules + skills), not upstream-only | untested | — |
### Decisions (human, verbatim)
### Decided without the human
### Probe log

## Issue 184 — Remove the circular judgments.refuted ceremony forced by rule-matrix
stage: investigating
verdict: —
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | #155 is done and post-merge reality matches this issue's description | partly confirmed | #155 CLOSED (orchestrator check); post-merge reality unverified |
| 2 | judgments.refuted / --refuted still exist and nothing else emits or reads them | untested | — |
| 3 | Naive deletion reds rule-matrix exactly as described | untested | — |
| 4 | Direction A (semantic-detector marker) is small and breaks no other detector's matrix check | untested | — |
### Decisions (human, verbatim)
### Decided without the human
- Checked #155 state myself (issue-reading, not delegated): CLOSED — declared dependency satisfied.
### Probe log

## Issue 183 — standards-audit: consider reducing per-commit cold-start latency
stage: investigating
verdict: — (early read: needs your call — deliverable is a decision; timing data feeds it)
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | Hook is still always_run: true; ~10 subprocess --list-rules reads per commit still current | untested | — |
| 2 | Measured warm cost sits in the claimed 1–2s band | untested | — |
| 3 | The four candidate directions remain the live option set (nothing landed since #151 changes the calculus) | untested | — |
### Decisions (human, verbatim)
### Decided without the human
### Probe log

## Issue 169 — Purge the residual "lint" vocabulary; standardize on "audit"
stage: investigating
verdict: —
### Hypotheses
| # | claim | status | evidence (one line) |
|---|-------|--------|---------------------|
| 1 | The listed instances still exist at the listed paths (#155's reorganization may have moved judgments docs) | untested | — |
| 2 | The issue's inventory is incomplete — a fresh grep surfaces more | untested | — |
| 3 | Renaming internal identifiers (loader:lint_cli console-script target) is contained; no external consumers | untested | — |
| 4 | An anti-lint audit rule can exempt generic English without a big false-positive surface (design Q) | untested | — |
### Decisions (human, verbatim)
### Decided without the human
### Probe log
