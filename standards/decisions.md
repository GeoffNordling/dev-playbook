---
type: Standard Card
title: Decision Records
description: Card for the decision-records standard — how hard-to-reverse decisions are recorded
---

# Decision Records

Governs how hard-to-reverse or surprising decisions are recorded.

## Define

- [decisions/records.md](/standards/decisions/records.md) — the contract:
  when a Decision Record is warranted, its template, sequential numbering,
  immutability, status vocabulary, and scope

## Audit

- [decisions-audit](/scripts/decisions-audit) — two rules over
  `docs/decisions/`: sequential numbering
  (`decisions.sequential-numbering`) and the status vocabulary
  (`decisions.status-vocabulary`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where decisions-audit blocks every commit

## Adopt

- none
