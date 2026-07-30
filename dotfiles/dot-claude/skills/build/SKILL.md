---
name: build
description: Carries out a direct-mode issue against its brief — test-first where the issue calls for tests, directly where it doesn't. Use when the issue overwatch launches the `build` node.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion
argument-hint: "<issue-number>"
---

# Build

Carry out a direct-mode issue against its brief. The brief's acceptance criteria are the contract.

Work without waiting for approval: plan, make the changes, and commit on your own, pausing only to escalate on the §5 triggers. The user reviews the finished work separately, not mid-build.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the body is the contract; its acceptance criteria are what you must satisfy. Comments may carry context the body doesn't, and the issue's `tests:*` label drives §2.
- **Rework re-entry.** Follow [PR feedback](~/workspace/dev-playbook/software-factory/pr-feedback.md) — read it now if `gh pr view` finds a PR, and skip it otherwise. The brief is the contract it names: where a finding conflicts with the brief, the brief wins.
- The existing files the brief concerns — there may be partial work from a prior cycle.
- Read the standard that governs the artifact you're changing, where one applies — e.g. [documentation conventions](~/workspace/dev-playbook/standards/prose/conventions.md) for docs, [the build standard](~/workspace/dev-playbook/standards/build/index.md) for the build or the pre-commit hooks.

## 2. Read what the issue calls for

The issue's `tests:*` label picks the discipline the work runs under:

| The issue carries | Read |
|---|---|
| `tests:yes` | [tdd.md](references/tdd.md) and the testing conventions it opens with, end-to-end — the work then runs test-first |
| `tests:no` | nothing further — the work touches no tests, so carry the brief out directly |

Under `tests:yes` this is a hard gate: report `READ: tdd.md, testing-conventions.md`, and edit no file before that report.

The label is the user's call, not yours. Work that turns out to need the other treatment is an escalation (§5), not a switch you make.

## 3. Plan

Before you start, state your plan — to anchor the work and keep it visible to the watching user:

- **Scope.** Which criteria the work covers, and the files it will touch.
- **Approach.** How you'll satisfy each criterion.
- **Ambiguities.** Anything in the brief you expect to resolve; if one stalls the work, escalate per §5.

The plan is your map, not a gate — proceed without waiting for approval.

## 4. Do the work

Carry out the brief in coherent pieces, keeping the tree green as you go:

1. Make the changes for a coherent piece of the scope. Under `tests:yes` that piece is a chunk, driven by the loops in [tdd.md](references/tdd.md).
2. Run the gate — `make -C <subproject> check`, or `make check` when the `Makefile` is at the repo root — and resolve failures.
3. Commit the piece with /commit.
4. Move to the next piece, or to §6 once the issue's scope is fully carried out.

## 5. Escalations

You work without approval, but when something falls outside the plan — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · phase: build · <where you're stuck and the call you need>
```

The user reads it, decides, and relaunches; you don't push past the obstacle on your own. Under `tests:yes`, tdd.md adds its own triggers to these:

- **The brief is wrong or underdetermined.** The work reveals the brief is mistaken, or it doesn't pin down what's wanted tightly enough to act. The brief is the user's; you don't edit the issue — surface it and let the user amend the issue or redirect.
- **The tests label is wrong.** `tests:no` work turns out to touch behavior that should be covered by tests, or `tests:yes` work turns out to have no behavior to drive a test from — the issue was mis-triaged. Surface it; the user decides the label.
- **The issue is too big for one session.** You can see the whole brief won't be carried out in this session before context runs low — a sizing miss. Surface it so the user re-splits it into smaller issues at intake; don't truncate the work silently.

## 6. Close the phase

With every acceptance criterion satisfied:

1. **Leave the tree green.** Run the gate — `make -C <subproject> check`, or `make check` when the `Makefile` is at the repo root; don't commit a red tree.
2. **Commit** the remaining changes with /commit.
3. Emit the terminal line, then stop:
   ```
   DONE: <repo>#<issue> · phase: build · commit <sha> · check green · unpushed
   ```
