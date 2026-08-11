---
type: Standard-Card
title: Semantic Validation
description: Card for the semantic-validation standard — how claims only language can check are validated and kept from drifting
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

- [standards/judgments/](/standards/judgments/index.md) — the contract, one
  concern per document; start at Judgment Declarations

## Audit

- [judgments-lint](/scripts/judgments-lint) — checks declaration shape,
  deterministically
- [the LLM judgments](/standards/judgments/declarations.md) — an LLM judge
  rules on each declared claim against its evidence, dispatched by the
  periodic `judgments-sweep` — for an ungated judgment, the only checker
  there is; the audit-kind detector no deterministic lint can stand in for

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/judgments/cache-gate.md))
  — the **push gate** for gated judgments: a pytest naming a judgment's id
  reds `make check-judgments-cache` until that exact content is
  judged-and-passed; a repo gates all, some, or none of its judgments
- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — judgments-lint at the **commit gate** in every repo's suite,
  dispatched by the published `playbook-lint` hook

## Adopt

- [Consuming Judgments](/standards/judgments/consuming.md) — the
  consumer-repo recipe: dependency, declarations, gate, cache fill
