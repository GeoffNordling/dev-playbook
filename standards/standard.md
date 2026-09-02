---
type: Standard-Card
title: Meta-Standard
description: Governs how the workspace's standards themselves are declared, found, and kept honest — the card format, the catalog, and drift
---

# Meta-Standard

Governs how the workspace's standards themselves are declared, found, and
kept honest — the card format, the catalog, and drift.

## Define

- [Standard-Card](/doc-types/standard-card/definition.md) — what a
  standard card is and is not, and the scope axis
- [Card Cells](/doc-types/standard-card/contract-shape.md) — the card:
  Standard-Card's contract shape, four pointer cells, and the generated
  view every card collapses to
- [Card Cells Encoding](/doc-types/standard-card/encoding.md) — how a
  cell's bullets encode pointers, where a card lives, naming, and the
  catalog
- [Standard](/doc-types/standard/definition.md) — what a Standard is: a
  population and the rules over it, and where it lives
- [Detectors and Drift](/standards/standard/detectors.md) — the detector
  contract and the drift machinery

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
