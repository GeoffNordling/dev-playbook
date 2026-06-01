---
name: agent-code-review
description: Reviews a direct-mode issue's PR diff against its issue brief and the project conventions, attaches findings to the PR, then advances it to human code review. Use when the agents dashboard launches the code-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue view *) Bash(gh issue edit *) Bash(gh pr view *) Bash(gh pr diff *) Bash(gh pr comment *) Bash(make *)
argument-hint: "<issue-number>"
---

# Agent Code Review

Review a direct-mode issue's PR diff against its issue brief and the project's coding and testing conventions, attach your findings to the PR, then advance it to human review. You audit and report; you never edit the code. A defect routes back to build through the human's reject, not through your hand.

An automated bug-review pass (the native `/code-review`) runs before you and posts its own PR comment; you add the brief-fidelity and convention findings it does not cover, then advance the label.

Work without waiting for approval: run the gate, audit, and post your findings on your own, pausing only to escalate on the §6 triggers. Finding code problems is the job, not a reason to stop — they go in the comment for the human, who decides at the next node whether to approve, review it again, or send the work back to build.

## Read first

Before doing anything else, read end-to-end:

- [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style. The build agent never saw this standard; enforcing it is yours alone.

Then report: `READ: testing-conventions.md, python-conventions.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. Work happens on the issue's branch.

- `gh issue view <issue>` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- `gh pr view --comments` — the bug-review pass that ran before you; read its comment so you don't re-flag what it caught.
- The tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the project's check gate (per `CLAUDE.md` / `Makefile`) — the full chain: tests, lint, and typecheck. Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§6) rather than review broken work.

## 3. Audit the change

Read the change as a whole — the brief and the code together — against the conventions. Assess each dimension and collect what you find, pinning each finding to the file and line and the rule or criterion it breaches.

- **Brief fidelity.** Every acceptance criterion is satisfied, the desired behavior is captured with no silent gap, and nothing in the change reaches past the brief's stated scope. Where the change carries tests, the gate proves they pass but not that they are honest — check each genuinely exercises the behavior the brief calls for rather than passing vacuously; where it carries none, check the change does what each criterion asks.
- **Testing conventions.** Where the change includes tests, they conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python conventions.** Where the change is Python, it conforms to python-conventions.md — docstrings, fail-loudly, annotation style.
- **Code quality.** Deep modules behind small surfaces, clear naming, no dead code or needless duplication — the engineering judgment the standards don't spell out.

## 4. Attach findings

Post one PR comment with `gh pr comment`. Group findings by severity so the human can act on them:

- **Blocking** — a defect that should send the work back: a fidelity gap, a convention breach that matters, a bug.
- **Suggestion** — an improvement that is not disqualifying.

Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or criterion it breaches. State which dimensions came back clean. If the whole diff is clean, say so plainly — a clean review is a real outcome, not a missing one.

## 5. Close the phase

Nothing changed on disk — there is no commit.

1. Advance to human review:
   ```bash
   gh issue edit <issue> --remove-label "phase:agent-code-review" --add-label "phase:human-code-review"
   ```
2. Emit the terminal line, then stop:
   ```
   DONE: reviewed code for #<issue>, findings on the PR, issue at phase:human-code-review
   ```
   Do not act on your own findings — the human reads them and decides whether to approve, review it again, or route back to build.

## 6. Escalations

You work without approval, but whenever you can't complete the review — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: #<issue> — <what's blocking you and the call you need>
```

The human reads it, decides, and relaunches. In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment and rides to the human at the next node; you escalate only when something stops you from producing the review at all.
