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
| **push gate** | `git push` | `make check`, via the pre-push stage |
| **CI gate** | every push and PR on GitHub | [thin CI](/standards/build/ci.md) |

The commit and push gates block locally, through the git hooks that invoke
them. The CI gate has no branch protection behind it —
[repo-settings.md](/standards/tracking/repo-settings.md) configures no required
status checks — so its block executes through the human's standing rule: **a
red CI run is never merged**. That rule is nondiscretionary — no judgment is
exercised — which is what keeps the CI gate a gate rather than a review; the
block sits at the merge button, not in branch-protection settings.

## Outside the gates

Not every place a check runs is a gate. These run checks but block nothing on
the path to main — they are references here, not rungs:

| Non-gate | When | What runs | Blocks |
|---|---|---|---|
| agent ritual | before finishing every committing phase | `make check` | no — a node-skill discipline, not a gate; the normative rule lives in [workflow.md's node-skill contract](/workflow/workflow.md#node-skill-contract) |
| workspace-audit | on demand and via the weekly review ([rules.md](~/workspace/select-measure-learn/rules.md)) | GitHub settings drift ([repo-settings.md](/standards/tracking/repo-settings.md)), label/issue/epic tracking conformance, four-tuple validity, and stale dev-playbook pins, via [`workspace-audit`](/scripts/workspace-audit) | no — reports, never blocks |

The re-run of `make check` at review start is the review node's **green gate**:
the code-review skills run it before auditing and escalate if it is red, even
though the push gate already covered the pushed commits — stated explicitly so
this belt-and-braces re-run is not mistaken for a fourth gate. GitHub sits
outside every gate: it hosts the CI gate but is not itself one.

## Map

Where each detector's rules fire. Every pre-commit hook fires at the **commit
gate, in the CI gate, and inside every `make check`** (hence also at the push
gate and in the agent ritual); the table lists only what falls outside that
pattern.

| Detector | Owns | Gates |
|---|---|---|
| repo-audit | structure: presence, forbidden files, layer shape, canonical compares, doc shape, script shebangs, name mapping | hook pattern |
| ruff-check / ruff-format | Python lint + formatting + docstrings (`D`) | hook pattern, plus `lint`/`format-check` targets |
| python-audit | workspace Python-source rules | hook pattern |
| testing-audit | test privacy, mirror layout, no-logic | hook pattern |
| okf-audit | concept-doc types, `index.md` freshness | hook pattern |
| decisions-audit | Decision Record sequential numbering, status vocabulary | hook pattern |
| ref-audit | Links and Citations | hook pattern, except the CI gate (skipped) |
| judgments-audit | judgment declarations | hook pattern |
| standards-audit | the meta-standard's card layout, catalog order, card↔rule matrix, hook surfaces, doc coverage | hook pattern (dev-playbook only) |
| shellcheck | shell scripts | hook pattern |
| shfmt | shell formatting | hook pattern |
| skill-audit | skill bundles (skill-authoring repos) | hook pattern |
| mypy | types | push gate only — never the CI gate |
| pytest | tests + judgments stage-1 cache gate | push gate only — never the CI gate |
| workspace-audit | GitHub settings ([repo-settings.md](/standards/tracking/repo-settings.md)), label-scheme and issue/epic tracking conformance, four-tuple validity, stale pins | workspace-audit (outside the gates) |
