---
name: build
description: Carries out a direct-mode issue that doesn't touch tests — documentation, configuration, chores — against the issue brief, then opens the PR and advances the issue to code review. Use when the agents dashboard launches the build phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh pr *) Bash(git *) Edit Write Skill(commit)
argument-hint: "<issue-number>"
---

# Build

Carry out a direct-mode issue whose work doesn't touch tests — documentation, configuration, chores — against the issue brief, then open the PR and hand the issue off to code review. The brief's acceptance criteria are the contract.

Work without waiting for approval: plan, make the changes, and commit on your own, pausing only to escalate on the §4 triggers. The human reviews the finished work separately, not mid-build.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. Work happens on the issue's branch.

- `gh issue view <issue>` — the body is the contract; its acceptance criteria are what you must satisfy.
- The existing files the brief concerns — there may be partial work from a prior cycle.
- Read the standard that governs the artifact you're changing, where one applies — e.g. [documentation conventions](~/workspace/dev-playbook/standards/doc-conventions.md) for docs, [build conventions](~/workspace/dev-playbook/standards/build-conventions.md) for the build or the pre-commit hooks.

## 2. Plan

Before you start, state your plan — to anchor the work and keep it visible to the watching human:

- **Scope.** Which criteria the work covers, and the files it will touch.
- **Approach.** How you'll satisfy each criterion.
- **Ambiguities.** Anything in the brief you expect to resolve; if one blocks the work, escalate per §4.

The plan is your map, not a gate — proceed without waiting for approval.

## 3. Do the work

Carry out the brief in coherent commits, keeping the tree green as you go:

1. Make the changes for a coherent piece of the scope.
2. Run the project's check gate (per `CLAUDE.md` / `Makefile`) — the existing tests, lint, format, and typecheck. You write no tests, but your change must not break the ones there. Resolve failures.
3. Commit the piece with /commit.
4. Move to the next piece, or to §5 once the issue's scope is fully carried out.

## 4. Escalations

You work without approval, but when something falls outside the plan — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: #<issue> — <what's blocking you and the call you need>
```

The human reads it, decides, and relaunches; you don't push past the blocker on your own. In particular:

- **The brief is wrong or underdetermined.** The work reveals the brief is mistaken, or it doesn't pin down what's wanted tightly enough to act. The brief is the human's; you don't edit the issue — surface it and let the human amend the issue or redirect.
- **The work needs tests.** What looked like test-free work turns out to touch behavior that should be covered by tests — the issue was mis-triaged. Surface it; the human re-routes it to /tdd rather than having you build it untested.
- **The issue is too big for one session.** You can see the whole brief won't be carried out in this session before context runs low — a sizing miss. Surface it so the human re-splits it into smaller issues at intake; don't truncate the work silently.

## 5. Close the phase

With every acceptance criterion satisfied:

1. **Leave the tree green.** Run the project's check gate (per `CLAUDE.md` / `Makefile`). Don't commit a red tree.
2. **Commit** the remaining changes with /commit.
3. **Push, then open the PR.** `git push` needs the human's YubiKey — hand them `git push -u origin <branch>` and wait for it to land. Then open the long-lived PR: `gh pr create --body "Closes #<issue> …"`. The `Closes #<issue>` token is mandatory — merging the PR closes the issue.
4. **Advance to code review:**
   ```bash
   gh issue edit <issue> --remove-label "phase:build" --add-label "phase:agent-code-review"
   ```
5. Emit the terminal line, then stop:
   ```
   DONE: carried out #<issue>, PR open, issue at phase:agent-code-review
   ```
   Do not begin the review — the human launches /agent-code-review separately.
