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
  factory's operating contract: dispatch, worktrees, node contracts, review
- [software-factory/user-checkpoints.md](/software-factory/user-checkpoints.md) — every
  point where the factory stops for the user, and what it owes them there
- [software-factory/node-skill-authoring.md](/software-factory/node-skill-authoring.md) — the
  authoring style behind the node skills: voice, content, robustness, mechanics
- [software-factory/review-contract.md](/software-factory/review-contract.md) — what the code
  and doc reviews do once dispatched: gate, cycle, findings comment, escalation boundary
- [software-factory/pr-feedback.md](/software-factory/pr-feedback.md) — the comment surfaces a
  PR carries, and how a committing node re-enters on a rework lap
- [software-factory/refactor-catalogue.md](/software-factory/refactor-catalogue.md) — the
  structural candidates with their cues and moves, and the step-size rule governing them
- [software-factory/deviation-contract.md](/software-factory/deviation-contract.md) — what a
  build agent does when reality contradicts its brief: the three limiters, escalation,
  the deviation ledger

## Audit

- [workspace-lint](/scripts/workspace-lint) — four-tuple validity on every
  open post-intake leaf (`software-factory.tuple-valid`), across repositories via
  `gh api`
- [judgments/code-matches-docs.yaml](/judgments/code-matches-docs.yaml) — the
  LLM-judged `scheme-vs-graph` claim that the scheme's factory dimensions mint
  exactly the labels this standard states, [the parity
  invariant](/software-factory/software-factory.md#naming) between the graph's
  work nodes and the `phase:*` values included

## Enforce

- nothing blocks: `scheme-vs-graph` is sweep-only, so a label scheme that has
  drifted from the graph surfaces at the next periodic judgments sweep.
  GitHub itself sits outside every gate, so the state
  machine stays the user dispatcher's to operate and workspace-lint reports
  without blocking a skipped phase or a malformed tuple

## Adopt

- the skills in `dotfiles/dot-claude/skills/` — intake and design carry an issue
  to ready; build, open-pr, and the review skills carry it to merge
  ([delegation](/software-factory/factory-operations.md#engagement))
