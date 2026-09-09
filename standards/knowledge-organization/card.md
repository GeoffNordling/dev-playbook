---
type: Standard-Card
title: Knowledge Organization
description: Governs how knowledge is organized in markdown — document types, indexes, the README and CONTEXT.md, cross-references, and documentation sets
---

# Knowledge Organization

Governs how knowledge is organized in markdown — document types, indexes,
the README and CONTEXT.md, cross-references, and documentation sets.

## Define

- [Document Types](/standards/knowledge-organization/document-types.md)
- [Type Registry](/standards/knowledge-organization/type-registry.md)
- [Indexes](/standards/knowledge-organization/indexes.md)
- [README Content](/standards/knowledge-organization/readme-content.md)
- [CONTEXT.md Content](/standards/knowledge-organization/context-content.md)
- [Cross-References](/standards/knowledge-organization/cross-references.md)
- [Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)
- [Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)

## Audit

- [okf-lint](/scripts/okf-lint) — concept-doc frontmatter types, and
  `index.md` presence, introduction, and freshness
- [ref-lint](/scripts/ref-lint) — Links and Citations resolve
- [repo-lint](/scripts/repo-lint) — README and CONTEXT.md doc shape
  (`knowledge-organization.doc-shape`)
- [working-doc-set-auditor](/dotfiles/dot-claude/agents/working-doc-set-auditor.md)
  — the LLM judge over one working documentation set, one slice of the
  Standards per launch, reporting and editing nothing

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint, ref-lint, and repo-lint at the **commit gate** in every
  repo's suite, all three dispatched by the published `playbook-lint` hook
- [working-doc-set-deslop](/dotfiles/dot-claude/skills/working-doc-set-deslop/SKILL.md)
  — **on demand**, audits a working documentation set through three
  auditor slices and then fixes it, the edits left uncommitted for diff
  review; invoke it as /working-doc-set-deslop

## Adopt

- none
