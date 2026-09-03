---
type: Standard-Card
title: Semantic Validation
description: Governs how claims only language can check — accuracy, honesty, scope — are validated and kept from drifting as the underlying files change
---

# Semantic Validation

Governs how claims only language can check — accuracy, honesty, scope —
are validated and kept from drifting as the underlying files change.

The [`judgments-run`](/scripts/judgments-run) CLI is the deterministic engine
behind the
[`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
skill: it plans one docket across any number of repos, renders the judge
prompts, and records the passing verdicts. The skill runs `plan` and `record`
as shell commands and passes the docket to the
[judgments workflow](/harness-recipes/recipes/judgments.md), which fans the
judges out and produces the verdicts outside any context window — so the skill
copies two opaque strings and is left with only the refutations to weigh.

## Define

- [Judgment Declarations](/standards/semantic-validation/declarations.md) — a
  repo's opt-in table, its family files, an entry's fields, and the bar a
  claim clears

## Audit

- [judgments-lint](/scripts/judgments-lint) — deterministically, over every
  declaration file the opt-in table names: a malformed table, file, or entry,
  and a duplicate id (`semantic-validation.declaration`); an absolute,
  `..`-bearing, or missing evidence or reference path
  (`semantic-validation.evidence-path`)

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/semantic-validation/cache-gate.md))
  — the **push gate** for gated judgments: a pytest naming a judgment's id
  reds `make check-judgments-cache` until that exact content is
  judged-and-passed; a repo gates all, some, or none of its judgments
- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — judgments-lint at the **commit gate** in every repo's suite,
  dispatched by the published `playbook-lint` hook

The push gate holds a gated judgment's verdict current with the content it
names, a state no rule of Judgment Declarations covers: that Standard binds a
declaration's shape, and only the LLM judge rules on whether a claim still
holds.

## Adopt

- [Consuming Judgments](/standards/semantic-validation/consuming.md) — the
  consumer-repo recipe: dependency, declarations, gate, cache fill
