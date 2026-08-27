---
type: Standard
title: Enforcement
description: The gate ladder — the three rungs where checks block the path to main, and the detector that owns each rule
---

# Enforcement

**Enforcement** is an audit stationed at a **gate** — an automatic, unmanned
blocking point on the path to main. The gates are named by their fixed rung
names. The governance vocabulary (Audit, Lint, Detector, Gate, Enforcement)
is defined in [CONTEXT.md](/CONTEXT.md); this file is where the three rungs
are defined once, and every card's Enforce cell cites them by these names.

## The three gates

| Gate | Trigger | What runs |
|---|---|---|
| **commit gate** | `git commit` | the pre-commit hook suite, on staged files |
| **push gate** | `git push` | `make check-judgments-cache`, via the pre-push stage |
| **CI gate** | every push and PR on GitHub | [thin CI](/standards/build/ci.md) |

The commit and push gates block locally, through the git hooks that invoke
them — hooks that live in `.git/`, so `uvx pre-commit install` has to run in
every clone. The CI gate has no branch protection behind it —
[repo-settings.md](/standards/tracking/repo-settings.md) configures no required
status checks — so its block executes through the user's standing rule: **a
red CI run is never merged**. That rule is nondiscretionary, which is what
keeps the CI gate a gate rather than a review; the block sits at the merge
button.

## Non-gate checks

Not every place a check runs is a gate. These run checks but block nothing on
the path to main — they are references here:

| Non-gate | When | What runs | Blocks |
|---|---|---|---|
| agent ritual | before finishing every committing phase | `make check` | no — a node-skill discipline; the normative rule lives in [the node-skill contract](/software-factory/factory-operations.md#the-node-skill-contract) |
| workspace-lint | on demand and via the periodic review | GitHub settings drift and default-branch protection ([repo-settings.md](/standards/tracking/repo-settings.md)), label/issue/epic tracking conformance, four-tuple validity, and stale dev-playbook pins, via [`workspace-lint`](/scripts/workspace-lint) | no — reports |

The re-run of `make check` at review start is the review node's **green gate**:
the reviewers run it before auditing and escalate if it is red, even
though the push gate already covered the pushed commits — stated explicitly so
this redundant re-run is not mistaken for a fourth gate. GitHub sits
outside every gate: it hosts the CI gate but is not itself one.

## Map

Where each detector's rules fire. Every pre-commit hook fires at the **commit
gate, in the CI gate, and inside every `make check`** (hence also in the agent
ritual, and at the push gate via `make check-judgments-cache`); the table lists only
what falls outside that pattern. The dev-playbook detectors reach those gates
through the single published `playbook-lint` hook, which dispatches its whole
roster ([distribution.md](/standards/build/distribution.md)); a per-detector
skip is a `SKIP=<detector>` environment entry the dispatcher honors. A skip is
legitimate only where a detector's input is machine-local rather than held in
the repository — the cited repos ref-lint resolves against, the judgment cache
pytest reads — so the detector would otherwise report the environment as a
defect in the code. Which machine skips what is recorded in
[machines.md](/docs/machines.md); every skip announces itself on each run.

| Detector | Owns | Gates |
|---|---|---|
| repo-lint | structure: presence, forbidden files, layer shape, canonical compares, doc shape, script shebangs, name mapping | hook pattern |
| ruff-check / ruff-format | Python lint + formatting + docstrings (`D`) | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| testing-lint | test privacy, mirror layout, no-logic | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| decisions-lint | Decision Record sequential numbering, status vocabulary | hook pattern |
| ref-lint | Links and Citations | hook pattern, except the CI gate and the secondary machines (skipped — neither carries the cited repos) |
| prose-lint | prose spelling (the American `judgment`); the banned actor noun; the first person in harness-loaded agent instructions | hook pattern |
| judgments-lint | judgment declarations | hook pattern |
| standards-lint | the meta-standard's card layout, catalog order, card↔rule matrix, hook surfaces | hook pattern (dev-playbook only) |
| shellcheck | shell scripts | hook pattern |
| shfmt | shell formatting | hook pattern |
| harness-files-lint | runbooks — skill bundles and agent definitions (runbook-authoring repos); the global CLAUDE.md source's shape (dev-playbook only) | hook pattern |
| mypy | types | push gate only — never the CI gate |
| pytest | tests + judgments cache gate | push gate only — never the CI gate; the judgments cache gate is skipped on the secondary machines |
| workspace-lint | GitHub settings and default-branch protection ([repo-settings.md](/standards/tracking/repo-settings.md)), label-scheme and issue/epic tracking conformance, four-tuple validity, stale pins | workspace-lint (outside the gates) |
