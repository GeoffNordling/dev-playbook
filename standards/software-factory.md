---
type: Standard-Card
title: Software Factory
description: Card for the software factory standard — how an idea becomes a merged pull request
---

# Software Factory

Governs how an idea becomes a merged pull request.

## Define

- [software-factory/software-factory.md](/software-factory/software-factory.md) — the states an
  issue moves through, idea to merge, and the labels naming them
- [software-factory/factory-operations.md](/software-factory/factory-operations.md) — the
  factory's operating contract: dispatch, worktrees, node contracts, review, judgments
- [software-factory/human-checkpoints.md](/software-factory/human-checkpoints.md) — every
  point where the factory stops for the human, and what it owes them there
- [software-factory/skill-authoring.md](/software-factory/skill-authoring.md) — voice and
  mechanics for the node skills

## Audit

- [workspace-lint](/scripts/workspace-lint) — four-tuple validity on every
  open post-intake leaf (`software-factory.tuple-valid`), across repositories via
  `gh api`

## Enforce

- none — GitHub sits outside every gate: the state machine is operated by the
  human dispatcher, and workspace-lint reports without blocking a skipped
  phase or a malformed tuple

## Adopt

- the skills in `dotfiles/dot-claude/skills/` — intake and design carry an issue
  to ready; build, open-pr, and the review skills carry it to merge
  ([delegation](/software-factory/factory-operations.md#engagement))
