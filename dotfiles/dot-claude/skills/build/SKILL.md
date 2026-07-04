---
name: build
description: Carries out a direct-mode issue that doesn't touch tests — documentation, configuration, chores — against the issue brief, then advances the issue to code review. Use when the agents dashboard launches the build phase.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion
argument-hint: "<issue-number>"
---

# Build

Carry out a direct-mode issue whose work doesn't touch tests — documentation, configuration, chores — against the issue brief, then hand the issue off to code review. The brief's acceptance criteria are the contract.

Work without waiting for approval: plan, make the changes, and commit on your own, pausing only to escalate on the §4 triggers. The user reviews the finished work separately, not mid-build.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** If the session is already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`), proceed. If the worktree exists but the session isn't in it, re-enter it: `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If neither the worktree nor the branch `issue-<issue>` exists yet — this is the issue's first node — create it: confirm local `main` is current with origin (a check, not a pull: compare `git rev-parse origin/main` to `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`; if they differ, escalate (§4) so the user pulls `main`), then `EnterWorktree(name=issue-<issue>)` and `git branch -m worktree-issue-<issue> issue-<issue>`. If the branch exists but the worktree is gone, the issue's work was lost — escalate (§4).

- `gh issue view <issue> --comments` — the body is the contract; its acceptance criteria are what you must satisfy. Comments may carry context the body doesn't.
- **Rework re-entry.** Check for an existing PR (`gh pr view`). If one exists, code review already ran — read **every** comment surface on the PR: its body, top-level conversation comments, review summary bodies, and inline/line-level diff comments alike, from both user and agent reviewers. (`gh pr view --comments` shows the body and conversation but omits the inline diff comments, which live at `gh api repos/{owner}/{repo}/pulls/<pr>/comments`; review summaries are at `.../pulls/<pr>/reviews` — these endpoints are a non-binding hint.) Build the rework work list from that complete feedback. If `gh pr view` finds none, this is first implementation; work from the brief alone. The brief stays the contract — where a finding conflicts with it, the brief wins.
- The existing files the brief concerns — there may be partial work from a prior cycle.
- Read the standard that governs the artifact you're changing, where one applies — e.g. [documentation conventions](~/workspace/dev-playbook/standards/doc-conventions.md) for docs, [the build standard](~/workspace/dev-playbook/standards/build/index.md) for the build or the pre-commit hooks.

## 2. Plan

Before you start, state your plan — to anchor the work and keep it visible to the watching user:

- **Scope.** Which criteria the work covers, and the files it will touch.
- **Approach.** How you'll satisfy each criterion.
- **Ambiguities.** Anything in the brief you expect to resolve; if one stalls the work, escalate per §4.

The plan is your map, not a gate — proceed without waiting for approval.

## 3. Do the work

Carry out the brief in coherent commits, keeping the tree green as you go:

1. Make the changes for a coherent piece of the scope.
2. If the piece touched a Python sub-project, run its gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root) — and resolve failures; you write no tests, but your change must not break the existing ones. A piece touching no Python sub-project has no `make` gate.
3. Commit the piece with /commit.
4. Move to the next piece, or to §5 once the issue's scope is fully carried out.

## 4. Escalations

You work without approval, but when something falls outside the plan — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · current phase: build · <where you're stuck and the call you need>
```

The user reads it, decides, and relaunches; you don't push past the obstacle on your own. In particular:

- **The brief is wrong or underdetermined.** The work reveals the brief is mistaken, or it doesn't pin down what's wanted tightly enough to act. The brief is the user's; you don't edit the issue — surface it and let the user amend the issue or redirect.
- **The work needs tests.** What looked like test-free work turns out to touch behavior that should be covered by tests — the issue was mis-triaged. Surface it; the user re-routes it to /tdd rather than having you build it untested.
- **The issue is too big for one session.** You can see the whole brief won't be carried out in this session before context runs low — a sizing miss. Surface it so the user re-splits it into smaller issues at intake; don't truncate the work silently.
- **Main is behind origin.** The stale-base check at §1 shows local `main` isn't current with origin. Surface it so the user pulls `main`; the worktree must branch off current main.

## 5. Close the phase

With every acceptance criterion satisfied:

1. **Leave the tree green.** If the work touched a Python sub-project, run its gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root); don't commit a red tree.
2. **Commit** the remaining changes with /commit.
3. **Advance to code review:**
   ```bash
   gh issue edit <issue> --remove-label "phase:build" --add-label "phase:code-pr-review"
   ```
4. Emit the terminal line, then stop:
   ```
   DONE: <repo>#<issue> · current phase: build · next phase: code-pr-review · commit <sha> · check green · unpushed
   ```
