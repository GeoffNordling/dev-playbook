---
type: Standard-Card
title: Semantic Validation
description: Card for the semantic-validation standard — how claims only language can check are validated and kept from drifting
---

# Semantic Validation

Governs how claims only language can check — accuracy, honesty, scope —
are validated and kept from drifting as the underlying files change.

The [`judgments-run`](/scripts/judgments-run) CLI is the deterministic engine
behind the `run-judgments` skill: it plans the docket, renders the judge
prompts, and records the passing verdicts. The skill reaches it through the
[judgments workflow](/harness-recipes/recipes/judgments.md), which runs those
three steps and the judge fan-out outside any context window, so the skill is
left with only the refutations to weigh.

## Define

- [standards/judgments/](/standards/judgments/index.md) — the contract, one
  concern per document; start at Judgment Declarations

## Audit

- [judgments-lint](/scripts/judgments-lint) — checks declaration shape,
  deterministically
- [the LLM judgments](/standards/judgments/declarations.md) — an LLM judge
  rules on each declared claim against its evidence; the audit-kind detector
  no deterministic lint can stand in for

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/judgments/cache-gate.md))
  — reds `make check-judgments`, wired to the **push gate** by the canonical
  pre-push hook, until every judgment's exact content is judged-and-passed
- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — judgments-lint at the **commit gate** in every repo's suite,
  dispatched by the published `playbook-lint` hook

## Adopt

- [Consuming Judgments](/standards/judgments/consuming.md) — the
  consumer-repo recipe: dependency, declarations, gate, cache fill
