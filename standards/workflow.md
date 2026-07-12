---
type: Standard Card
title: Workflow
description: Card for the workflow standard — how an idea becomes a merged pull request
---

# Workflow

Governs how an idea becomes a merged pull request.

## Define

- [workflow/workflow.md](/workflow/workflow.md) — the intake-to-merge
  state machine: labels, dispatch, worktrees, permissions
- [workflow/skill-authoring.md](/workflow/skill-authoring.md) — voice and
  mechanics for the phase node-skills

## Audit

- [workspace-audit](/scripts/workspace-audit) — four-tuple validity on every
  open post-intake leaf (`workflow.tuple-valid`), across repositories via
  `gh api`

## Enforce

- none — GitHub sits outside every gate: the state machine is operated by the
  human dispatcher, and workspace-audit reports without blocking a skipped
  phase or a malformed tuple

## Adopt

- the phase node-skills in `dotfiles/dot-claude/skills/` — intake, design,
  build, tdd, open-pr, and the review nodes carry an issue through the
  graph ([Skills](/workflow/workflow.md#skills))
