---
name: sdd-agent-code-review
description: Reviews an SDD issue's PR diff against its committed spec and the project conventions, attaches findings to the PR, then advances it to human code review. Use when the agents dashboard launches the code-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue view *) Bash(gh issue edit *) Bash(gh pr view *) Bash(gh pr diff *) Bash(gh pr comment *) Bash(make *)
argument-hint: "<issue-number>"
---

# SDD Agent Code Review

Review an SDD issue's PR diff against its committed spec and the project's coding and testing conventions, attach your findings to the PR, then advance it to human review. You audit and report; you never edit the code. A defect routes back to build through the human's reject, not through your hand.

An automated bug-review pass (the native `/code-review`) runs before you and posts its own PR comment; you add the spec-fidelity and convention findings it does not cover, then advance the label.

Work without waiting for approval: run the gate, audit, and post your findings on your own, pausing only to escalate on the §6 triggers. Finding code problems is the job, not a reason to stop — they go in the comment for the human, who decides at the next node whether to approve, iterate, or send the work back to build.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — how to read the committed `feat`/`req`/`dsn` and `Interface:` lines you check the code against.
- [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style. The build agent never saw this standard; enforcing it is yours alone.

Then report: `READ: spec-standard.md, testing-conventions.md, python-conventions.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. Work happens on the issue's branch.

- `gh issue view <issue>` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- `gh pr view --comments` — the bug-review pass that ran before you; read its comment so you don't re-flag what it caught.
- The committed specs under `specs/functional_requirements/` and `specs/design/` — what the code must implement.
- The tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the project's check gate (per `CLAUDE.md` / `Makefile`) — the full chain: tests, lint, typecheck, and the spec graph. Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§6) rather than review broken work.

## 3. Audit the change

Read the change as a whole — the spec and the code together — against the conventions. Assess each dimension and collect what you find, pinning each finding to the file and line and the rule or spec item it breaches.

- **Spec fidelity.** The gate already proves each spec item has a passing verifier; what it can't prove is that the verifier is honest. Reading spec and code together, check that each test genuinely exercises the behavior its `req`/`dsn` describes rather than passing vacuously, and that the code implements what the spec commits to without drifting past its scope.
- **Testing conventions.** The tests conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python conventions.** The code conforms to python-conventions.md — docstrings, fail-loudly, annotation style.
- **Code quality.** Deep modules behind small surfaces, clear naming, no dead code or needless duplication — the engineering judgment the standards don't spell out.

## 4. Attach findings

Post one PR comment with `gh pr comment`. Group findings by severity so the human can act on them:

- **Blocking** — a defect that should send the work back: a fidelity gap, a convention breach that matters, a bug.
- **Suggestion** — an improvement that is not disqualifying.

Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or spec item it breaches. State which dimensions came back clean. If the whole diff is clean, say so plainly — a clean review is a real outcome, not a missing one.

## 5. Close the phase

Nothing changed on disk — there is no commit.

1. Advance to human review:
   ```bash
   gh issue edit <issue> --remove-label "phase:sdd-agent-code-review" --add-label "phase:sdd-human-code-review"
   ```
2. Emit the terminal line, then stop:
   ```
   DONE: reviewed code for #<issue>, findings on the PR, issue at phase:sdd-human-code-review
   ```
   Do not act on your own findings — the human reads them and decides whether to approve, iterate, or route back to build.

## 6. Escalations

You work without approval, but stop, surface the situation, and wait for the human's call whenever you can't complete the review — anything unexpected, or any wish to deviate. In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment and rides to the human at the next node; you escalate only when something stops you from producing the review at all.
