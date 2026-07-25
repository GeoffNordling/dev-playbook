---
type: Standard-Card
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
- [ref-lint](/scripts/ref-lint) — Links and Citations resolve
- [repo-lint](/scripts/repo-lint) — README and CONTEXT.md doc shape
  (`knowledge-organization.doc-shape`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint, ref-lint, and repo-lint at the **commit gate** in every
  repo's suite, all three dispatched by the published `playbook-lint` hook

## Adopt

- none
