---
name: agent-code-review
description: Reviews a direct-mode issue's PR diff against its issue brief and the project conventions, attaches findings to the PR, then advances it to human code review. Use when the agents dashboard launches the code-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion Edit Write MultiEdit NotebookEdit
argument-hint: "<issue-number>"
---

# Agent Code Review

Review a direct-mode issue's PR diff against its issue brief and the project's conventions, attach your findings to the PR, then advance it to human review. You audit and report; you never edit the code. A defect routes back to build through the user's reject, not through your hand.

An automated bug-review pass (the native `/code-review`) runs before you and posts its own PR comment; you add the brief-fidelity and convention findings it does not cover, then advance the label.

Work without waiting for approval: run the gate, audit, and post your findings on your own, pausing only to escalate on the §6 triggers. Finding code problems is the job, not a reason to stop — they go in the comment for the user, who decides at the next node whether to approve, review it again, or send the work back to build.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§6) — don't start a fresh tree.

- `gh issue view <issue>` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- `gh pr view --comments` — the bug-review pass that ran before you; read its comment so you don't re-flag what it caught.
- Where the change includes code, the tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root). Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§6) rather than review broken work. Don't run individual lint tools yourself — where there's no `make check` to run, proceed to the audit.

## 3. Audit the change

Read the change as a whole — the brief and the change together — against the standards it answers to. The diff's nature picks the dimensions; pin each finding to its file and line and the rule or criterion it breaches.

**When the change includes code** — read [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) and [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) first; the build agent saw neither, so enforcing them is yours alone:

- **Brief fidelity.** Every acceptance criterion is satisfied, the desired behavior is captured with no silent gap, and nothing reaches past the brief's stated scope. Where the change carries tests, the gate proves they pass but not that they are honest — check each genuinely exercises the behavior the brief calls for rather than passing vacuously; where it carries none, check the change does what each criterion asks.
- **Testing conventions.** Where the change includes tests, they conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python conventions.** The code conforms to python-conventions.md — docstrings, fail-loudly, annotation style.
- **Code quality.** Deep modules behind small surfaces, clear naming, no dead code or needless duplication — the engineering judgment the standards don't spell out.

**When the change is docs or text only** — read [documentation conventions](~/workspace/dev-playbook/standards/doc-conventions.md) first:

- **Brief fidelity.** Every acceptance criterion is satisfied, with no silent gap, and nothing reaches past the brief's stated scope.
- **Documentation conventions.** The prose conforms to doc-conventions.md — voice, structure, one rule per section, current-state — and reads accurately against what it documents.

## 4. Attach findings

Post one PR comment with `gh pr comment`. Group findings by severity so the user can act on them:

- **Blocking** — a defect that should send the work back: a fidelity gap, a convention breach that matters, a bug.
- **Suggestion** — an improvement that is not disqualifying.

Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or criterion it breaches. State which dimensions came back clean. If the whole diff is clean, say so plainly — a clean review is a real outcome, not a missing one.

## 5. Close the phase

1. Advance to human review:
   ```bash
   gh issue edit <issue> --remove-label "phase:agent-code-review" --add-label "phase:human-code-review"
   ```
2. Emit the terminal line, then stop:
   ```
   DONE: reviewed code for #<issue>, findings on the PR, issue at phase:human-code-review
   ```
   Do not act on your own findings — the user reads them and decides whether to approve, review it again, or route back to build.

## 6. Escalations

You work without approval, but whenever you can't complete the review — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: #<issue> — <where you're stuck and the call you need>
```

The user reads it, decides, and relaunches. In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment and rides to the user at the next node; you escalate only when something stops you from producing the review at all.
