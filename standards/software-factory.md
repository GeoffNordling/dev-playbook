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
- [software-factory/review-contract.md](/software-factory/review-contract.md) — what the code
  and doc reviews do once dispatched: gate, cycle, findings comment, escalation boundary
- [software-factory/pr-feedback.md](/software-factory/pr-feedback.md) — the comment surfaces a
  PR carries, and how a committing node re-enters on a rework lap
- [software-factory/refactor-catalogue.md](/software-factory/refactor-catalogue.md) — the
  refactor candidates a build node looks for, and the step-size rule governing them

## Audit

- [workspace-lint](/scripts/workspace-lint) — four-tuple validity on every
  open post-intake leaf (`software-factory.tuple-valid`), across repositories via
  `gh api`
- [judgments/code-matches-docs.yaml](/judgments/code-matches-docs.yaml) — the
  LLM-judged `scheme-vs-graph` claim that `src/dev_playbook/label_scheme.json`
  mints exactly the labels this standard states, [the parity
  invariant](/software-factory/software-factory.md#naming) between the graph's
  work nodes and the `phase:*` values included

## Enforce

- the pytest cache gate ([The Cache Gate](/standards/judgments/cache-gate.md))
  — reds `make check-judgments` at the **push gate** until `scheme-vs-graph` is
  judged-and-passed, so a label scheme that has drifted from the graph cannot be
  pushed. This gates the label *vocabulary* only: GitHub itself sits outside
  every gate, so the state machine stays the human dispatcher's to operate and
  workspace-lint reports without blocking a skipped phase or a malformed tuple

## Adopt

- the skills in `dotfiles/dot-claude/skills/` — intake and design carry an issue
  to ready; build, open-pr, and the review skills carry it to merge
  ([delegation](/software-factory/factory-operations.md#engagement))
