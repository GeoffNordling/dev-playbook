---
name: tdd
description: Implements a direct-mode issue via vertical-slice TDD against the issue brief's acceptance criteria, then advances the issue to code review. Use when the agents dashboard launches the tdd phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh api *) Bash(git *) Bash(make *) EnterWorktree ExitWorktree Edit Write Skill(commit)
argument-hint: "<issue-number>"
---

# TDD

Implement a direct-mode issue with vertical-slice TDD against the issue brief — its acceptance criteria are the contract. Then hand the issue off to code review. Implementation proceeds in **chunks** — each runs an inner red/green/refactor loop per slice and closes with a whole-chunk refactor pass.

Work without waiting for approval: plan, implement, refactor, and commit on your own, pausing only to escalate on the §5 triggers. The human reviews the finished work separately, not mid-build.

## Read first

Before doing anything else, read end-to-end:

- [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.

Then report: `READ: testing-conventions.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Create the issue's worktree.** First confirm local `main` is current with origin — a check, not a pull: compare `git rev-parse origin/main` to `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`. If they differ, escalate (§5) so the human pulls `main`. Otherwise create it: `EnterWorktree(name=issue-<issue>)`, then `git branch -m worktree-issue-<issue> issue-<issue>`.

- `gh issue view <issue>` — the body is the contract; its acceptance criteria are the behaviors you must discharge.
- Existing tests under `tests/` and code under `src/` — there may be partial work or stubs from a prior cycle.
- Run the test suite to see the current state: `make test`. Run all `make` commands from the Python sub-project the issue lives in (`make -C <subproject> …`, or the repo root when the `Makefile` is there).

## 2. Plan the chunk

A **chunk** is a coherent piece of implementation work — typically the slices covering one acceptance criterion, or a small cluster of tightly related ones. Implementation proceeds one chunk at a time.

Before each chunk, state your plan — to anchor the work and keep it visible to the watching human:

- **Scope.** Which criteria and behaviors the chunk covers.
- **Slice ordering.** The sequence of red/green/refactor slices you'll drive.
- **Ambiguities.** Anything in the brief you expect to resolve; if one stalls the next slice, escalate per §5.

The plan is your map, not a gate — proceed without waiting for approval.

## 3. The chunk loop (outer)

For each chunk:

1. Run the inner slice loop until every behavior in the chunk's scope is covered with passing tests.
2. **Whole-chunk refactor pass.** With the suite green, review every module the chunk touched for refactor candidates not visible inside a single slice — cross-module duplication, deeper-module opportunities now that several call sites exist, abstraction misalignments, primitive obsession. Run `make test` after each step. A refactor that surfaces a structural problem beyond one module's seam is an escalation — see §5.
3. Run `make check`. Resolve failures.
4. Commit the chunk with /commit.
5. Move to the next chunk, or to §6 once the issue's scope is fully implemented.

## 4. The slice loop (inner)

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior the brief calls for. Write a single failing test exercising it through the public surface. Run `make test`; confirm it fails for the expected reason.

**Never modify a written test.** Once you've written a test, make it pass by changing code, not the test. If you feel the need to change the test, escalate (§5) — don't edit it yourself.

**Stub on first contact.** When a test names a symbol that doesn't exist yet, create the stub it needs — you design the signature here, since the brief pins behavior, not interfaces. Body is `raise NotImplementedError` for functions and methods, `pass` for `__init__`. Don't pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass. Don't add code for behaviors not yet tested. Run `make test`; confirm green.

**Refactor.** With the suite green, look for refactor candidates inside the module: extract duplication, deepen modules, simplify primitives. Run `make test` after each step. A refactor that surfaces a structural problem beyond one module's seam is an escalation — see §5.

Refactor candidate catalogue:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on the public interface)
- **Shallow modules** → Combine or deepen
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic

For test-quality patterns and mocking guidance, see [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md).

## 5. Escalations

You work without approval, but when something falls outside the plan — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: #<issue> — <where you're stuck and the call you need>
```

The human reads it, decides, and relaunches; you don't push past the obstacle on your own. In particular:

- **Stuck test.** A slice's test won't pass after two implementation attempts.
- **A written test looks wrong.** You want to change a test you already wrote — surface why; the human decides whether you mis-encoded it or the brief needs to change.
- **The brief is wrong or underdetermined.** Building reveals the brief is mistaken, or it doesn't pin down the next behavior tightly enough to write the assertion. The brief is the human's; you don't edit the issue — surface it and let the human amend the issue or redirect.
- **The issue is too big for one session.** You can see the whole brief won't be implemented in this build before context runs low — a sizing miss. Surface it so the human re-splits it into smaller issues at intake; don't truncate the work silently.
- **Main is behind origin.** The stale-base check at §1 shows local `main` isn't current with origin. Surface it so the human pulls `main`; the worktree must branch off current main.

## 6. Close the phase

With every acceptance criterion met by a passing test:

1. **Leave the tree green.** Run `make check`. Don't commit a red tree.
2. **Commit** the remaining changes with /commit.
3. **Release the worktree.** `ExitWorktree(keep)`.
4. **Advance to code review:**
   ```bash
   gh issue edit <issue> --remove-label "phase:tdd" --add-label "phase:agent-code-review"
   ```
5. Emit the terminal line, then stop:
   ```
   DONE: implemented #<issue> on issue-<issue> — push it (git push -u origin issue-<issue>), then launch /agent-code-review
   ```
   Do not push or begin the review — the human pushes the branch and launches /agent-code-review.
