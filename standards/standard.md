---
type: Standard Card
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

- [standards-audit](/scripts/standards-audit) — the meta-standard's five
  deterministic rules: card layout, catalog order, the bidirectional
  card↔rule matrix, hook-surface agreement, and doc coverage

## Enforce

- the pre-commit hook suite
  ([.pre-commit-config.yaml](/.pre-commit-config.yaml)) — standards-audit
  blocks nonconforming commits at the **commit gate**; it is wired in
  dev-playbook's local block alone, since the `standards/` tree it audits
  exists only here

## Adopt

- none
