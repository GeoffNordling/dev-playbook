---
type: Standard
title: Enforcement
description: The gate ladder — the three rungs where checks block the path to main, and the detector that owns each rule
---

# Enforcement

**Enforcement** is an audit stationed at a **gate** — an automatic, unmanned
blocking point on the path to main. There are exactly three gates, named by
their fixed rung names. The governance vocabulary (Audit, Gate, Enforcement,
Finding) is defined in [CONTEXT.md](/CONTEXT.md); this file is where the
three rungs are defined once, and every card's Enforce cell cites them by
these names.

## The three gates

| Gate | Trigger | What runs |
|---|---|---|
| **commit gate** | `git commit` | the pre-commit hook suite, on staged files |
| **push gate** | `git push` | `make check`, via the pre-push stage |
| **CI gate** | every push and PR on GitHub | [thin CI](/standards/build/ci.md) |

## Outside the gates

Not every place a check runs is a gate. These run checks but block nothing on
the path to main — they are references here, not rungs:

| Non-gate | When | What runs | Blocks |
|---|---|---|---|
| agent ritual | before every commit and before opening every PR | `make check` | no — a node-skill discipline, not a gate; the normative rule lives in [workflow.md's node-skill contract](/workflow/workflow.md#node-skill-contract) |
| workspace sweep | on demand and via the weekly ritual | GitHub settings drift ([repo-settings.md](/standards/tracking/repo-settings.md)) and stale dev-playbook pins, via [`sweep`](/scripts/sweep) | no — reports, never blocks |

The agent ritual re-runs `make check` immediately before opening a PR even
though the push gate already covered the pushed commits — stated explicitly
so the belt-and-braces re-run is not mistaken for a fourth gate. GitHub sits
outside every gate: it hosts the CI gate but is not itself one.

## Map

Where each detector's rules fire. Every pre-commit hook fires at the **commit
gate, in the CI gate, and inside every `make check`** (hence also at the push
gate and in the agent ritual); the table lists only what falls outside that
pattern. Detector names are the current ones — renames are a later slice.

| Detector | Owns | Gates |
|---|---|---|
| repo-audit | structure: presence, forbidden files, layer shape, canonical compares, doc shape, script shebangs, name mapping | hook pattern |
| ruff-check / ruff-format | Python lint + formatting | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| ref-check | Links and Citations | hook pattern, except the CI gate (skipped) |
| judgments-lint | judgment declarations | hook pattern |
| shellcheck | shell scripts | hook pattern |
| internal-skill-audit | skill bundles (skill-authoring repos) | hook pattern |
| mypy | types | push gate only — never the CI gate |
| pytest | tests + judgments stage-1 cache gate | push gate only — never the CI gate |
| `gh api` sweep | GitHub settings ([repo-settings.md](/standards/tracking/repo-settings.md)), stale pins | workspace sweep (outside the gates) |
