---
type: Standard-Card
title: Decision Records
description: Governs how hard-to-reverse or surprising decisions are recorded — the Decision Record's warrant, template, numbering, immutability, and status vocabulary
---

# Decision Records

Governs how hard-to-reverse or surprising decisions are recorded — the
Decision Record's warrant, template, numbering, immutability, and status
vocabulary.

## Define

- [decisions/records.md](/standards/decisions/records.md) — the contract:
  when a Decision Record is warranted, its template, sequential numbering,
  immutability, status vocabulary, and scope

## Audit

- [decisions-lint](/scripts/decisions-lint) — two rules over
  `docs/decisions/`: sequential numbering
  (`decisions.sequential-numbering`) and the status vocabulary
  (`decisions.status-vocabulary`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where decisions-lint blocks every commit by way
  of the published `playbook-lint` hook

## Adopt

- none
