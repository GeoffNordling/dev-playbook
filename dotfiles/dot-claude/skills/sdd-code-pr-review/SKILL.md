---
name: sdd-code-pr-review
description: Reviews an SDD issue's PR against its committed spec and the project conventions, attaches findings to the PR, then takes the user's verdict — approve to merge, or rework back to the implementer. Use when the agents dashboard launches the SDD code review phase.
disable-model-invocation: false
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# SDD Code & PR Review

Review an SDD issue's PR diff against its committed spec and the project's coding and testing conventions, attach your findings to the PR, then take the user's verdict on them. One node, two halves: you audit on your own and post the findings, then the user reads them and tells you to approve or rework, and you carry out the transition. You never modify the code under review — a defect routes back to the implementer through the user's rework, not your hand.

An automated bug-review pass (the native `/code-review`) runs before you in the same goal and posts its own PR comment; you add the spec-fidelity and convention findings it does not cover. The audit runs hands-off; finding code problems is its output, not a reason to stop. Once the findings are posted you hand off: the user engages, and you answer their questions and help them weigh the findings, acting only on an explicit verdict.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — how to read the committed `feat`/`req`/`dsn` and `Interface:` lines you check the code against.
- [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style. The build agent never saw this standard; enforcing it is yours alone.

Then report: `READ: spec-standard.md, testing-conventions.md, python-conventions.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§6) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- `gh pr view --comments` — the native bug-review pass that ran before you, and any prior review cycle's findings; read them so you don't re-flag what they caught.
- The committed specs under `specs/functional_requirements/` and `specs/design/` — what the code must implement.
- The tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root). Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§6) rather than review broken work. Don't run individual lint tools yourself.

## 3. Audit the change

Read the change as a whole — the spec and the code together — against the conventions. Assess each dimension and collect what you find, pinning each finding to the file and line and the rule or spec item it breaches.

**Know your cycle first.** The cycle number is the count of prior `## Code review — …` comments on the PR, plus one. Cycles 1 and 2 are full reviews across the dimensions below. From cycle 3 on, the review is a lockdown: its sole job is verifying the prior review's Blocking findings are fixed — don't hunt for new findings, though anything you notice incidentally still gets reported.

- **Spec fidelity.** The gate already proves each spec item has a passing verifier; what it can't prove is that the verifier is honest. Reading spec and code together, check that each test genuinely exercises the behavior its `req`/`dsn` describes rather than passing vacuously, and that the code implements what the spec commits to without drifting past its scope.
- **Testing conventions.** The tests conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python conventions.** The code conforms to python-conventions.md — docstrings, fail-loudly, annotation style.
- **Code quality.** Deep modules behind small surfaces, clear naming, no dead code or needless duplication — the engineering judgment the standards don't spell out.

## 4. Attach findings

Stage the comment body in a `/tmp` file (e.g. `/tmp/code-review-<issue>.md`) — writes inside the worktree are denied, `/tmp` is allowed — then post one PR comment with `gh pr comment --body-file <path>`.

- **Head it with the reviewed revision and the cycle.** `## Code review — <sha> · cycle <n>`, using the short HEAD sha (`git rev-parse --short HEAD`) and the cycle number from §3. On a re-review — the PR already carries a prior `## Code review — …` comment — head it `## Code review — <sha> · cycle <n> (supersedes review of <prior-sha>)` and open with a one-line disposition of each prior finding (resolved / still open), so neither the user nor a later read treats the stale findings as live.
- **Every finding is a problem plus its fix.** State the believed problem and the action it calls for, grouped by severity — **Blocking** (a fidelity gap, a convention breach that matters, a bug) or **Suggestion** (a non-disqualifying improvement). Write nothing that isn't actionable: no "acceptable as written", "no action needed", "just noting", and no explaining why a clean thing is clean — detail belongs to Blocking and Suggestion findings alone. Where you are genuinely unsure, raise it as a question or risk, naming the decision the user faces.
- **A real problem outside this PR's scope** — highlight it and recommend a follow-up issue; never open one yourself.
- Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or spec item it breaches. Enumerate the clean dimensions bare — names only, no per-dimension justification; if the whole diff is clean, say so plainly — a clean review is a real outcome.

Then emit your terminal line and stop — the goal yields and the user takes over:

```
DONE: <repo>#<issue> · current phase: sdd-code-pr-review · findings on PR · awaiting human review
```

## 5. Take the verdict

The user has read the findings. Engage — answer questions, weigh the findings, help them think — but make no change to the code under review; a fix is the implementer's to make on rework. Rework is Blocking-driven by default — Suggestions alone don't call for a rework lap. Act only on an explicit verdict:

- **approve** — the work is ready to merge. The user squash-merges in the GitHub UI; you can't (the PAT can't merge). Their merge drops the origin branch and closes the issue via the PR's `Closes #<issue>`, so no label change follows. Worktree teardown is not yours — overwatch removes the local side after the user confirms the merge.
- **rework** — the work goes back to the implementer. Record the deciding reason so the implementer reads it alongside your findings, then route back:
  ```bash
  gh issue comment <issue> --body "<the user's reason>"
  gh issue edit <issue> --remove-label "phase:sdd-code-pr-review" --add-label "phase:sdd-tdd"
  ```

Then report the verdict, the transition, and the issue's new state in one line:

```
<repo>#<issue> · current phase: sdd-code-pr-review · next phase: <merged|sdd-tdd> · <verdict>
```

## 6. Escalations

While auditing — before the hand-off — whenever you can't produce the review, surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · current phase: sdd-code-pr-review · <where you're stuck and the call you need>
```

In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment; you escalate only when something stops you from producing the review at all.
