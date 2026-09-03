---
type: Standard-Card
title: Module Design
description: Governs how modules are designed — interfaces, depth, and seams
---

# Module Design

Governs how modules are designed — interfaces, depth, and seams.

## Define

- [Module Design Conventions](/standards/modules/design.md) — the contract:
  depth, the deletion test, the seam rules, and the port at a process boundary

## Audit

- none

No detector exists. Whether an interface is small against the behaviour behind
it is a comparison a reader makes, not a state deterministic code reads, and an
Audit cell admits only a lint cited by a `/scripts/` link or a judgment link
([Detectors](/standards/standard/detectors.md#detectors)). The reviewer at code
review is the only check: `dotfiles/dot-claude/agents/code-pr-review.md` routes
every diff carrying Python source to this contract. A code review is a one-time
checkpoint, never an Enforce pointer.

## Enforce

- none

## Adopt

- [improve-codebase-architecture](/dotfiles/dot-claude/skills/improve-codebase-architecture/SKILL.md)
  — the migration procedure: scans a codebase for shallow modules in this
  standard's vocabulary, reports the candidates, then grills the one picked;
  invoke it as `/improve-codebase-architecture`
