---
type: Standard
title: Gates
description: The three gates on the path to main — what each runs, the local two in every clone, the red CI rule, and when a detector is skipped
population: "a gate: an automatic, unmanned blocking point on the path to main"
---

# Gates

An audit stationed at a gate is Enforcement's blocking mode: its findings
stop the path to main there ([Vocabulary](/CONTEXT.md#governance)); the
other mode, a tool invoked on demand, is no gate. This Standard fixes
the gates: what each is, where it blocks, and what may be skipped at one.
A card's Enforce cell names a gate by its rung name
([Card Cells Encoding](/doc-types/standard-card/encoding.md#cells)).

## Three rungs

A gate is one of three, named by its rung: the **commit gate**,
`git commit`, running the pre-commit hook suite on the staged files; the
**push gate**, `git push`, running `make check-judgments-cache` through
the pre-push stage; and the **CI gate**, every push and pull request on
GitHub, running the canonical workflow.

| Gate | Trigger | What runs |
|---|---|---|
| **commit gate** | `git commit` | the pre-commit hook suite, on staged files |
| **push gate** | `git push` | `make check-judgments-cache`, via the pre-push stage |
| **CI gate** | every push and PR on GitHub | the canonical [ci.yml](/standards/build/canonical.md#ciyml) |

A pre-commit hook fires at every rung: the commit gate runs it on the
staged files, `make check` runs the suite on all files and so the push
gate does, and the CI gate runs the suite; an Enforce cell cites the rung
where the detector's wiring lives. mypy and pytest run only inside the
`make` targets, so they reach the push gate and never the CI gate.

Not every place a check runs is a gate. `make check` before a committing
phase ends is a node-skill discipline
([the node-skill contract](/software-factory/factory-operations.md#the-node-skill-contract)),
and its re-run at review start is the review node's green gate, not a
fourth rung. workspace-lint reports and blocks nothing. GitHub hosts the
CI gate and is not itself one.

## Installed in every clone

The commit and push gates are present in every clone: both pre-commit
stages installed, `uvx pre-commit install`, which the canonical config
declares.

The two gates block through git hooks that live in `.git/`, which no clone
inherits.

## A red CI run is never merged

The CI gate has no branch protection behind it, and its block is the
user's standing rule: a pull request whose CI run is red is not merged.

[Repository Settings](/standards/tracking/repo-settings.md) configures no
required status check, so the block sits at the merge button. The rule is
nondiscretionary, which is what keeps the CI gate a gate rather than a
review.

## Skips

A detector is skipped at a gate only where its input is machine-local
rather than held in the repository: the cited repos ref-lint resolves
against, the judgment cache pytest reads; a skip is a `SKIP=<detector>`
environment entry the `playbook-lint` dispatcher honors, it announces
itself on every run, and which machine skips what is recorded in
[Machines](/docs/machines.md).

The canonical workflow skips ref-lint this way, since a CI runner checks
out one repo and a cross-repo Citation cannot resolve there. Local
pre-commit stays the strict reference gate. okf-lint runs in CI, since
everything it checks is in the repo.
