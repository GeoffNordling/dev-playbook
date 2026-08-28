---
type: Standard-Card
title: Module Design
description: Governs how modules are designed — interfaces, depth, and seams
---

# Module Design

Governs how modules are designed — interfaces, depth, and seams.

## Define

- [Module Design Conventions](/standards/modules/design.md) — the
  contract: the vocabulary and the aliases it retires, the four principles,
  the three rules that make an interface testable, and the dependency
  categories that govern deepening

## Audit

- none

## Enforce

- none

## Adopt

- [improve-codebase-architecture](/dotfiles/dot-claude/skills/improve-codebase-architecture/SKILL.md)
  — the migration procedure: scans a codebase for shallow modules in this
  standard's vocabulary, reports the candidates, then grills the one picked;
  invoke it as `/improve-codebase-architecture`
