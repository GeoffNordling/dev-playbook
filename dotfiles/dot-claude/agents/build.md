---
name: build
description: Carries out a direct-mode issue against its brief — test-first where the issue calls for tests, directly where it doesn't. Use when the software factory launches the `build` node.
model: opus
effort: xhigh
---

# Build

Carry out a direct-mode issue against its brief. The brief's acceptance criteria are the contract.

Work without waiting for approval: plan, make the changes, and commit on your own, pausing only to escalate on the §5 triggers. The user reviews the finished work separately, not mid-build.

## 1. Load context

Your prompt is the issue number; below, `<issue>` is that number.

- `gh issue view <issue> --json title,body,comments` — the body is the contract; its acceptance criteria are what you must satisfy. Comments may carry context the body doesn't, and the issue's `tests:*` label drives §2.
- The existing files the brief concerns — there may be partial work from a prior cycle.
- Read the standard that governs the artifact you're changing, where one applies — e.g. [documentation conventions](~/workspace/dev-playbook/standards/prose/conventions.md) for docs, [the build standard](~/workspace/dev-playbook/standards/build/index.md) for the build or the pre-commit hooks.

## 2. Read what the issue calls for

The issue's `tests:*` label picks the discipline the work runs under:

| The issue carries | Read |
|---|---|
| `tests:yes` | [tdd.md](~/workspace/dev-playbook/software-factory/tdd.md) and the testing conventions it opens with, end-to-end — the work then runs test-first |
| `tests:no` | nothing further — the work touches no tests, so carry the brief out directly |

Under `tests:yes` this is a hard gate: report `READ: tdd.md, testing-conventions.md`, and edit no file before that report.

The label is the user's call, not yours. Work that turns out to need the other treatment is an escalation (§5), not a switch you make.

## 3. Plan

Before you start, state your plan, to anchor the work:

- **Scope.** Which criteria the work covers, and the files it will touch.
- **Approach.** How you'll satisfy each criterion.
- **Ambiguities.** Anything in the brief you expect to resolve; if one stalls the work, escalate per §5.

The plan is your map, not a gate.

## 4. Do the work

Carry out the brief in coherent pieces, keeping the tree green as you go:

1. Make the changes for a coherent piece of the scope. Under `tests:yes` that piece is a chunk, driven by the loops in [tdd.md](~/workspace/dev-playbook/software-factory/tdd.md).
2. Run the gate — `make -C <subproject> check`, or `make check` when the `Makefile` is at the repo root — and resolve failures.
3. Commit the piece with /commit.
4. Move to the next piece, or to §6 once the issue's scope is fully carried out.

Declarations under `judgments/` are documentation: keep the ones your edits affect accurate as you edit; add new ones rarely — see [The bar](~/workspace/dev-playbook/standards/judgments/declarations.md#the-bar).

## 5. Escalations

When reality contradicts the brief, run the three limiters of the [deviation contract](~/workspace/dev-playbook/software-factory/deviation-contract.md). Three clean no's: make the fix, log it for the ledger (§6), and keep working. Any yes — or an answer you cannot give cleanly — halt: post the contract's structured escalation comment to the PR if one exists, otherwise to the issue, then end the session per §6 with `outcome: escalated`. The comment is the durable record; the envelope only ends the run. Anything else unexpected that stalls the work escalates the same way, minus the limiter step.

The user reads the comment, decides, and relaunches; you don't push past the obstacle on your own. Under `tests:yes`, tdd.md carries a further set of triggers of its own. In particular:

- **The brief is wrong or underdetermined.** The work reveals the brief is mistaken, or it doesn't pin down what's wanted tightly enough to act. The brief is frozen at launch — nobody amends the body, the user included; surface it, and the user rules by comment. A recorded ruling binds every later deviation via limiter 3.
- **The tests label is wrong.** `tests:no` work turns out to touch behavior that should be covered by tests, or `tests:yes` work turns out to have no behavior to drive a test from — the issue was mis-triaged. Surface it; the user decides the label.
- **The issue is too big for one session.** You can see the whole brief won't be carried out in this session before context runs low — a sizing miss. Surface it so the user re-splits it into smaller issues at intake; don't truncate the work silently.

## 6. Close the phase

With every acceptance criterion satisfied:

1. **Leave the tree green.** Run the gate — `make -C <subproject> check`, or `make check` when the `Makefile` is at the repo root; don't commit a red tree.
2. **Commit** the remaining changes with /commit.
3. **Record the deviation ledger.** If any deviation was logged, record the entries in the contract's shape as one issue comment headed `## Deviation ledger`, which the node that authors the PR description lifts. No deviations — record nothing here; the PR section states `No deviations.` explicitly.
4. **End on the report envelope.** The session ends with structured output, never a message alone: `outcome` is `"done"`, and `gist` gives the outcome in prose — the commit, that the gate is green, and that the branch is pushed. An escalation ends the same way, with `outcome` `"escalated"` and the reason in `gist`.
