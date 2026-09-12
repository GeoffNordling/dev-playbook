---
type: General-Sheet
title: Stale Findings
description: Incorrect, stale, or broken things found while designing the Loop doc-type, parked so they are fixed later and do not divert the work
---

# Stale Findings

Things found wrong on the way to the Loop doc-type, unrelated to the
peers themselves; findings about the peers live in
[Three Peers](/worktree-loop-document-type-working-docs/three-peers.md#where-the-peers-are-not-yet-parallel).
Each is a record and a guess at the fix; none is acted on in this set. The set's root is
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

## Findings

- **Dead link in three consumer repos.** `story-forge`, `mission-control`,
  and `spec-tools` each have a `standards/index.md` that links to
  `~/workspace/dev-playbook/standards/standard/format.md`, renamed to
  `cards.md`.
- **`workspace-lint` roster omits `spec-tools`.** The `GOVERNED` list in
  `scripts/workspace-lint` names seven repos; `spec-tools` carries a
  dev-playbook pin and is not among them.
- **A JS file registered as a family.** The registry table in
  [Doc-Type System](/doc-types/doc-type-system.md#registry-rulings) has a
  row `.claude/workflows/*.js | workflows | Pending`. A workflow script
  is a JS file, not a loop; the Loop doc-type sits above any runtime.
  The row is a category error and needs re-ruling.
- **Doc-type import is prose only.**
  [Doc-Type System](/doc-types/doc-type-system.md#the-import-surface)
  says a consumer writes its own doc-type-system file; no consumer repo
  has one, and nothing lints for it. Standards import through the
  pinned `playbook-lint` hook; doc-types have no equivalent. Not wrong,
  but a gap the Loop doc-type inherits.

## Acronyms

None.
