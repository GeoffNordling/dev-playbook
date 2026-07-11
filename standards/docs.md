---
type: Standard Card
title: Knowledge Organization
description: Card for the knowledge-organization standard — how knowledge is organized in markdown
---

# Knowledge Organization

Governs how knowledge is organized in markdown — the bundle, document
types, indexes, and cross-references.

## Define

- [standards/docs/](/standards/docs/index.md) — the contract, one concern
  per document; start at The OKF Bundle

## Audit

- [okf-audit](/scripts/okf-audit) — concept-doc frontmatter types and
  `index.md` freshness
- [ref-audit](/scripts/ref-audit) — Links and Citations resolve

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-audit and ref-audit at the **commit gate** in every repo's suite

## Adopt

- none
