---
type: Standard-Card
title: Meta-Standard
description: Governs how the workspace's standards themselves are declared, found, and kept honest — the card, the catalog, the detectors, and the gates
---

# Meta-Standard

Governs how the workspace's standards themselves are declared, found, and
kept honest — the card, the catalog, the detectors, and the gates. What a
Standard is, its card's four cells, its rulesets' populations and rules,
and the views they collapse to are the Standard doc-type
([doc-types/standard/](/doc-types/standard/index.md)). The rulesets
below hold the rules.

## Define

- [Card Catalog](/standards/standard/cards.md)
- [Gates](/standards/standard/gates.md)
- [Detectors](/standards/standard/detectors.md)

## Audit

- [standards-lint](/scripts/standards-lint) — the meta-standard's
  deterministic rules; `--list-rules` is the registry

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
