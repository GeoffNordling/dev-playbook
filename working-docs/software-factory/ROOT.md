---
type: General-Sheet
title: Software Factory, Isolated
description: The software factory moved whole out of the tree on 2026-09-20 and touched by nothing — what is here, where each piece came from, what stayed, and that its future, rewrite or deletion, is undecided
---

# Software Factory, Isolated

This set is speculative: nothing in it is decided, and every member
writes a guess as a guess. It holds the software factory whole, moved
here on 2026-09-20 by the doc-type system refactor
([its plan](/working-docs/doc-type-system/doc-type-system/ROOT.md)) so
that no step of that work trips over it. The factory is out of that
work's scope, and its future, a rewrite or deletion, is a later
session's decision. Until then nothing in the repo links to, imports,
runs, tests, stows, or lints as a harness file any member of this set.
Each member is as it was on the day of the move, except that links
among the members follow the move.

## Goal

Keep the factory whole and findable while it waits, so that the session
that decides its fate has every piece in one place.

## What is here, and where it came from

- **`docs/`** — the ten files of `software-factory/` at the repo root,
  with that directory's `index.md` and `README.md`. They were typed
  `Guide`; the doc-type plan's step 5 gave `Guide` one home, `guides/`,
  so these carry `General-Sheet`, the type of an unsettled working-set
  member, until the factory's fate is decided.
- **`agents/`** — six agent definitions from `dotfiles/dot-claude/agents/`:
  `adjudicator`, `bug-pr-review`, `build`, `code-pr-review`,
  `doc-pr-review`, `open-pr`.
- **`skills/`** — eight skills from `dotfiles/dot-claude/skills/`:
  `issue-overwatch`, `agent-view-overwatch`, `issue-review-claims`,
  `issue-review-simulation`, `wayfinder-to-build`, `intake`, `design`,
  `user-intent-mini-interview`. They leave `~/.claude` at the next stow.
- **`code/factory/`** — the package `src/dev_playbook/factory/`, imported
  as `dev_playbook.factory`: `launcher.py`, `ledger.py`, `traverse.py`.
  **`code/traverse-issue`** — its `scripts/` entry point. mypy and pytest
  no longer read them.
- **`tests/`** — the three modules of `tests/dev_playbook/factory/` and,
  in `conftest.py`, the four helpers the shared `tests/conftest.py` held
  for them alone: `StoredRow`, `ledger_rows`, `write_definition`,
  `process_state`. The modules also import `init_repo` and `commit_all`
  from the shared conftest, which stayed.

## What stayed in the tree

- The tracking Standard: the `phase:*` and `mode:*` labels in
  `src/dev_playbook/label_scheme.json`, which bootstrap-labels mints into
  every governed repo, and the workspace-lint rules over them.
- The frozen Decision Records that cite the factory.
- `wayfinder`, `commit`, and `candidate-promote`, which name the
  factory in a phrase. `candidate-promote`'s fourth step still runs
  `/intake`, which is here, so that skill does not work until the
  factory's fate is decided.
- The Runbook doc-type's residual ledger keeps its sections for the
  moved runbooks, and `doc-types/runbook/contract-shape.md` its
  `adjudicator` excerpt; the doc-type plan's step 7 tidies both.

## Planned

- **Decide the factory's fate.** Rewrite or delete; a later session's
  call, made with the user.

## Completed

- **Isolated, 2026-09-20.** Moved whole by step 4 of the doc-type
  plan; the inbound links from `standards/tracking/card.md`,
  the tracking guide, `docs/headless.md`, the root `README.md`
  and `index.md`, `scripts/README.md`, and `CANDIDATES.md` were cut or
  repointed there.

## Acronyms

None.
