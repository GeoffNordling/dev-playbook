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

- [okf-lint](/scripts/okf-lint) — concept-doc frontmatter types and
  `index.md` freshness
- [ref-check](/scripts/ref-check) — Links and Citations resolve

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint and ref-check in every repo's suite

## Adopt

- none
