---
type: Standard-Card
title: Semantic Validation
description: Card for the semantic-validation standard — how claims only language can check are validated and kept from drifting
---

# Semantic Validation

Governs how claims only language can check — accuracy, honesty, scope —
are validated and kept from drifting as the underlying files change.

The [`judgements-run`](/scripts/judgements-run) CLI is the deterministic engine
the `run-judgements` skill drives: it plans the docket, renders the judge
prompts, and records the passing verdicts.

## Define

- [standards/judgements/](/standards/judgements/index.md) — the contract, one
  concern per document; start at Judgement Declarations

## Audit

- [judgements-lint](/scripts/judgements-lint) — checks declaration shape,
  deterministically
- [the LLM judgements](/standards/judgements/declarations.md) — an LLM judge
  rules on each declared claim against its evidence; the audit-kind detector
  no deterministic lint can stand in for

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/judgements/cache-gate.md))
  — reds `make check-judgements`, wired to the **push gate** by the canonical
  pre-push hook, until every judgement's exact content is judged-and-passed
- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — judgements-lint at the **commit gate** in every repo's suite

## Adopt

- [Consuming Judgements](/standards/judgements/consuming.md) — the
  consumer-repo recipe: dependency, declarations, gate, cache fill
