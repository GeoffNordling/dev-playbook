---
type: Standard
title: Enforcement
description: The gate ladder — the three rungs where checks block the path to main, and the detector that owns each rule
---

# Enforcement

**Enforcement** is an audit stationed at a **gate** — an automatic, unmanned
blocking point on the path to main. There are exactly three gates, named by
their fixed rung names. The governance vocabulary (Audit, Detector, Gate,
Enforcement, Finding) is defined in [CONTEXT.md](/CONTEXT.md); this file is
where the three rungs are defined once, and every card's Enforce cell cites
them by these names.

## The three gates

| Gate | Trigger | What runs |
|---|---|---|
| **commit gate** | `git commit` | the pre-commit hook suite, on staged files |
| **push gate** | `git push` | `make check-judgements`, via the pre-push stage |
| **CI gate** | every push and PR on GitHub | [thin CI](/standards/build/ci.md) |

The commit and push gates block locally, through the git hooks that invoke
them. The CI gate has no branch protection behind it —
[repo-settings.md](/standards/tracking/repo-settings.md) configures no required
status checks — so its block executes through the human's standing rule: **a
red CI run is never merged**. That rule is nondiscretionary — no judgement is
exercised — which is what keeps the CI gate a gate rather than a review; the
block sits at the merge button, not in branch-protection settings.

## Outside the gates

Not every place a check runs is a gate. These run checks but block nothing on
the path to main — they are references here, not rungs:

| Non-gate | When | What runs | Blocks |
|---|---|---|---|
| agent ritual | before finishing every committing phase | `make check` | no — a node-skill discipline, not a gate; the normative rule lives in [software-factory.md's node-skill contract](/software-factory/software-factory.md#node-skill-contract) |
| workspace-lint | on demand and via the periodic review | GitHub settings drift ([repo-settings.md](/standards/tracking/repo-settings.md)), label/issue/epic tracking conformance, four-tuple validity, and stale dev-playbook pins, via [`workspace-lint`](/scripts/workspace-lint) | no — reports, never blocks |

The re-run of `make check` at review start is the review node's **green gate**:
the code-review skills run it before auditing and escalate if it is red, even
though the push gate already covered the pushed commits — stated explicitly so
this belt-and-braces re-run is not mistaken for a fourth gate. GitHub sits
outside every gate: it hosts the CI gate but is not itself one.

## Map

Where each detector's rules fire. Every pre-commit hook fires at the **commit
gate, in the CI gate, and inside every `make check`** (hence also in the agent
ritual, and at the push gate via `make check-judgements`); the table lists only
what falls outside that pattern.

| Detector | Owns | Gates |
|---|---|---|
| repo-lint | structure: presence, forbidden files, layer shape, canonical compares, doc shape, script shebangs, name mapping | hook pattern |
| ruff-check / ruff-format | Python lint + formatting + docstrings (`D`) | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| testing-lint | test privacy, mirror layout, no-logic | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| decisions-lint | Decision Record sequential numbering, status vocabulary | hook pattern |
| ref-lint | Links and Citations | hook pattern, except the CI gate (skipped) |
| judgements-lint | judgement declarations | hook pattern |
| standards-lint | the meta-standard's card layout, catalog order, card↔rule matrix, hook surfaces | hook pattern (dev-playbook only) |
| shellcheck | shell scripts | hook pattern |
| shfmt | shell formatting | hook pattern |
| skill-lint | skill bundles (skill-authoring repos) | hook pattern |
| mypy | types | push gate only — never the CI gate |
| pytest | tests + judgements cache gate | push gate only — never the CI gate |
| validate | spec graph | push gate only — never the CI gate (sdd repos) |
| workspace-lint | GitHub settings ([repo-settings.md](/standards/tracking/repo-settings.md)), label-scheme and issue/epic tracking conformance, four-tuple validity, stale pins | workspace-lint (outside the gates) |
