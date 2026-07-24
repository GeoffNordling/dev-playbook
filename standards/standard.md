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

- [standards-lint](/scripts/standards-lint) — the meta-standard's
  deterministic rules; `--list-rules` is the registry
- [judgments/standard-cards.yaml](/judgments/standard-cards.yaml) — the
  card-honesty judgments, one per card: an LLM judge rules whether each
  card's pointers are truthful, the semantic check the deterministic rules
  cannot make

## Enforce

- the pre-commit hook suite
  ([.pre-commit-config.yaml](/.pre-commit-config.yaml)) — standards-lint
  blocks nonconforming commits at the **commit gate**; dev-playbook dogfoods
  it from its local block, and consumer repos inherit it through the
  published `playbook-lint` hook the canonical template's pinned block wires

## Adopt

- [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md) — the
  consumer-repo recipe: grow the `standards/` tree, write and publish a
  conforming detector, mirror it, gate it
