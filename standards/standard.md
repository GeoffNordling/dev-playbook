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

- [okf-lint](/scripts/okf-lint) — keeps the catalog
  ([standards/index.md](/standards/index.md)) complete and every card typed
- [ref-check](/scripts/ref-check) — keeps every card pointer resolving
- [judgments/doc-consistency.yaml](/judgments/doc-consistency.yaml) — one
  judgment per card: its pointers really do define, audit, and enforce
  their standard

## Enforce

- the pre-commit hook suite
  ([.pre-commit-config.yaml](/.pre-commit-config.yaml)) — okf-lint,
  ref-check, and judgments-lint block nonconforming commits at the
  **commit gate**; the judgment cache gate reds the **push gate**
  (`make check`)

## Adopt

- none
