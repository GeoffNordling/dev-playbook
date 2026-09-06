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

## Enforce

- none

## Adopt

- [improve-codebase-architecture](/dotfiles/dot-claude/skills/improve-codebase-architecture/SKILL.md)
  — the migration procedure: scans a codebase for shallow modules in this
  standard's vocabulary, reports the candidates, then grills the one picked;
  invoke it as `/improve-codebase-architecture`
