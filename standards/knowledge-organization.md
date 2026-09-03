---
type: Standard-Card
title: Knowledge Organization
description: Governs how knowledge is organized in markdown — document types, indexes, the README and CONTEXT.md, cross-references, and working documentation sets
---

# Knowledge Organization

Governs how knowledge is organized in markdown — document types, indexes,
the README and CONTEXT.md, cross-references, and working documentation
sets.

## Define

- [Document Types](/standards/knowledge-organization/document-types.md)
  — the frontmatter profile every concept document carries, with the
  global type registry as its table
- [Type Registry](/standards/knowledge-organization/type-registry.md)
  — the Types table's shape and the additive law a consumer's local
  extension obeys
- [Indexes](/standards/knowledge-organization/indexes.md) — the
  `index.md` file: typeless, introduction, listing, ordering, authored
- [README Content](/standards/knowledge-organization/readme-content.md)
  — the README floor and what it never holds
- [CONTEXT.md Content](/standards/knowledge-organization/context-content.md)
  — the vocabulary center's shape and its glossary rules
- [Cross-References](/standards/knowledge-organization/cross-references.md)
  — Links in-bundle, Citations across repos, the runbook forms, and
  fragment anchors
- [Working Documentation Sets](/standards/knowledge-organization/working-documentation-sets.md)
  — how one work stream's in-process files relate as a set

## Audit

- [okf-lint](/scripts/okf-lint) — concept-doc frontmatter types and
  `index.md` freshness
- [ref-lint](/scripts/ref-lint) — Links and Citations resolve
- [repo-lint](/scripts/repo-lint) — README and CONTEXT.md doc shape
  (`knowledge-organization.doc-shape`)
- [working-doc-set-deslop](/dotfiles/dot-claude/skills/working-doc-set-deslop/SKILL.md)
  — audit and then fix a working documentation set, the edits left
  uncommitted for diff review; invoke it as /working-doc-set-deslop

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint, ref-lint, and repo-lint at the **commit gate** in every
  repo's suite, all three dispatched by the published `playbook-lint` hook

## Adopt

- none
