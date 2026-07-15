---
type: Standard-Card
title: Semantic Validation
description: Card for the semantic-validation standard — how claims only language can check are validated and kept from drifting
---

# Semantic Validation

Governs how claims only language can check — accuracy, honesty, scope —
are validated and kept from drifting as the underlying files change.

## Define

- [standards/judgments/](/standards/judgments/index.md) — the contract, one
  concern per document; start at Judgment Declarations

## Audit

- [judgments-audit](/scripts/judgments-audit) — checks declaration shape,
  deterministically
- [judgments-run](/scripts/judgments-run) — the deterministic engine of the
  semantic-detection workflow: plans the docket, renders the judge prompts,
  and records the verdicts

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/judgments/cache-gate.md))
  — reds `make check-judgments`, wired to the **push gate** by the canonical
  pre-push hook, until every judgment's exact content is judged-and-passed
- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — judgments-audit at the **commit gate** in every repo's suite

## Adopt

- [Consuming Judgments](/standards/judgments/consuming.md) — the
  consumer-repo recipe: dependency, declarations, gate, cache fill
