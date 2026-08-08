---
name: code-pr-review
description: Audits the code in a direct-mode issue's PR against its issue brief and the project conventions, and attaches findings to the PR. Use when the issue overwatch dispatches the code track at the `pr_review` stop.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# Code & PR Review

Review a direct-mode issue's PR diff against its issue brief and the project's conventions, and attach your findings to the PR.

A bug-review pass (/bug-pr-review) runs in parallel with you and posts its own PR comment; you add the brief-fidelity and convention findings it does not cover.

**Jurisdiction: code, plus the PR body.** Findings post on the diff's code files — source, tests, scripts, config, build — and on the PR body, for the presence check alone. Docs in the diff are fidelity evidence only: a code change that demands a doc update the diff lacks is a brief-fidelity finding, not a prose finding — the doc track, running in parallel, owns the prose.

## Read first

Before doing anything else, read end-to-end:

- [review contract](~/workspace/dev-playbook/software-factory/review-contract.md) — the stance, the green gate, the cycle count, the findings comment, the escalation boundary.
- [PR feedback](~/workspace/dev-playbook/software-factory/pr-feedback.md) — every comment surface a PR carries, and the command that reaches each.

Then report: `READ: review-contract.md, pr-feedback.md`. Proceed only after.

Your values for the contract's three parameters:

| Parameter | Value |
|---|---|
| Review name | `Code review` |
| Staging filename | `/tmp/code-review-<issue>.md` |
| Blocking | a missing PR-description section, a fidelity gap, a convention breach that matters, a bug |

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- The PR's existing feedback, across every surface — prior review cycles' findings, so you don't re-flag what they caught. The /bug-pr-review pass runs in parallel with you; its comment for this cycle may not exist yet, so don't wait for it or dedup against it.
- Where the change includes code, the tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Read what the diff calls for

The diff's content picks the standards that bind this review. Read the ones it calls for, end-to-end, then report `READ: <what you read>`:

| The diff carries | Read |
|---|---|
| tests | [testing conventions](~/workspace/dev-playbook/standards/testing/conventions.md) |
| Python source | [python style](~/workspace/dev-playbook/standards/python/style.md), plus /codebase-design invoked for the module-design contract |
| shell scripts | [shell conventions](~/workspace/dev-playbook/standards/shell/conventions.md) |

The implementer read at most the testing conventions, so enforcing all of these is yours alone.

## 3. Audit the change

Read the change as a whole — the brief and the change together — against the standards it answers to; pin each finding to its file and line and the rule or criterion it breaches. The presence check always runs — its subject is the PR body, not the diff — and every other dimension below whose content the diff carries is audited; the dimensions that ran are also the ones the comment enumerates when they come back clean.

- **The presence check**, first and mechanical. The PR body carries the
  three mandatory sections of the
  [merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe)
  — `## Summary`, `## Deviation ledger`, `## Deferred` — with the explicit
  empty-markers (`No deviations.`, `Nothing deferred.`) accepted. A missing
  section is an automatic Blocking finding; absence is checkable, so this
  dimension involves no judgment call.
- **Brief fidelity**, always. Every acceptance criterion is satisfied, the desired behavior is captured with no silent gap, and nothing reaches past the brief's stated scope. Where the change carries tests, the gate proves they pass but not that they are honest — check each genuinely exercises the behavior the brief calls for rather than passing vacuously; where it carries none, check the change does what each criterion asks.
- **Testing conventions.** The tests conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python style.** The code conforms to python-style.md — docstrings, the fail-loud rule (no silent fallbacks or defensive guards), the helpers bar (a helper earns its place or stays inline), annotation style.
- **Module design.** The change conforms to /codebase-design — deep modules behind small interfaces, no pass-throughs that fail the deletion test, seams only where something varies — plus clear naming, no dead code or needless duplication.
- **Shell conventions.** The scripts conform to shell-conventions.md — above all the glue-only boundary: an executable script reaching for a function, an array, or argument parsing has outgrown shell and belongs in Python. shellcheck and shfmt already proved the mechanical rules at the gate, so spend the dimension on the boundary call, which is a reviewer's alone.

## 4. Attach findings

Write and post the comment per the review contract, using your parameter values above. Then emit the terminal line and stop:

```
DONE: <repo>#<issue> · phase: pr-review · findings on PR #<n>
```

## 5. Escalations

Your line:

```
ESCALATE: <repo>#<issue> · phase: pr-review · <where you're stuck and the call you need>
```

Your blocks:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.
