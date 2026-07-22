---
type: Standard-Card
title: Meta-Standard
description: Card for the meta-standard — how standards are declared as cards, cataloged, and kept honest
---

# Meta-Standard

Governs how the workspace's standards themselves are declared, found, and
kept honest.

## Define

- [Standards and Standard Cards](/standards/standard/format.md) — the
  contract: what a standard is, the card format, the catalog, drift

## Audit

- [standards-lint](/scripts/standards-lint) — the meta-standard's five
  deterministic rules: card layout, catalog order, the bidirectional
  card↔rule matrix, hook-surface agreement, and the consumer-mode
  upstream-shadow guard
- [judgments/standard-cards.yaml](/judgments/standard-cards.yaml) — the
  card-honesty judgments, one per card: an LLM judge rules whether each
  card's pointers are truthful, the semantic check the deterministic rules
  cannot make

## Enforce

- the pre-commit hook suite
  ([.pre-commit-config.yaml](/.pre-commit-config.yaml)) — standards-lint
  blocks nonconforming commits at the **commit gate**; dev-playbook dogfoods
  it from its local block, and consumer repos inherit it as a published hook
  through the canonical template's pinned block

## Adopt

- none
