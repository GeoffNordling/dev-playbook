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
- [software-factory/node-agent-and-skill-authoring.md](/software-factory/node-agent-and-skill-authoring.md) — the
  authoring style behind the node agent definitions and the node skills: voice,
  content, robustness, mechanics
- [software-factory/review-contract.md](/software-factory/review-contract.md) — what a review
  does once launched: gate, severities, threads, cycle, escalation boundary
- [software-factory/pr-feedback.md](/software-factory/pr-feedback.md) — the comment surfaces a
  PR carries, and how a committing node re-enters on a rework lap
- [software-factory/tdd.md](/software-factory/tdd.md) — the test-first
  discipline `tests:yes` work runs under: the chunk, the slice loop, and the
  whole-chunk refactor pass
- [software-factory/refactor-catalogue.md](/software-factory/refactor-catalogue.md) — the
  structural candidates with their cues and moves, and the step-size rule governing them
- [software-factory/deviation-contract.md](/software-factory/deviation-contract.md) — what a
  build agent does when reality contradicts its brief: the three limiters, the
  halt-commit-escalate lane, the deviation ledger

## Audit

- none: the graph and the contracts its regions run under are prose an agent
  reads, with no deterministic check over them. What *is* checked is the label
  half — the four-tuple on every leaf and the `phase:*` values' parity with this
  graph's work nodes — and both answer the
  [tracking](/standards/tracking.md) card, where the label contract
  ([factory-labels.md](/standards/tracking/factory-labels.md)) lives

## Enforce

- nothing blocks: GitHub itself sits outside every gate, so the state machine
  stays the user dispatcher's to operate — no gate stops a skipped phase

## Adopt

- the typed agent definitions in `dotfiles/dot-claude/agents/` and the skills in
  `dotfiles/dot-claude/skills/` — the intake and design skills carry an issue to
  ready; the `build`, `open-pr`, `bug-pr-review`, `code-pr-review`, and
  `doc-pr-review` definitions carry it to merge
  ([delegation](/software-factory/factory-operations.md#engagement))
