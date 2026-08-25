---
type: Standard-Card
title: Knowledge Organization
description: Card for the knowledge-organization standard — how knowledge is organized in markdown
---

# Knowledge Organization

Governs how knowledge is organized in markdown — file roles, document
types, indexes, and cross-references.

## Define

- [standards/knowledge-organization/](/standards/knowledge-organization/index.md) — the contract, one concern
  per document; start at File Roles

## Audit

- [okf-lint](/scripts/okf-lint) — concept-doc frontmatter types and
  `index.md` freshness
- [ref-lint](/scripts/ref-lint) — Links and Citations resolve
- [repo-lint](/scripts/repo-lint) — README and CONTEXT.md doc shape
  (`knowledge-organization.doc-shape`)
- /working-doc-set-audit — report drift on a targeted working
  documentation set
- /working-doc-set-deslop — audit and then fix a working documentation
  set, the edits left uncommitted for diff review

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint, ref-lint, and repo-lint at the **commit gate** in every
  repo's suite, all three dispatched by the published `playbook-lint` hook

## Adopt

- none
