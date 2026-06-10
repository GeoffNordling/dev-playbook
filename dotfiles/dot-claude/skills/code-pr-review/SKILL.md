---
name: code-pr-review
description: Reviews a direct-mode issue's PR against its issue brief and the project conventions, attaches findings to the PR, then takes the user's verdict — approve to merge, or rework back to the implementer. Use when the agents dashboard launches the code review phase.
disable-model-invocation: false
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# Code & PR Review

Review a direct-mode issue's PR diff against its issue brief and the project's conventions, attach your findings to the PR, then take the user's verdict on them. One node, two halves: you audit on your own and post the findings, then the user reads them and tells you to approve or rework, and you carry out the transition. You never modify the code under review — a defect routes back to the implementer through the user's rework, not your hand.

An automated bug-review pass (the native `/code-review`) runs before you in the same goal and posts its own PR comment; you add the brief-fidelity and convention findings it does not cover. The audit runs hands-off; finding code problems is its output, not a reason to stop. Once the findings are posted you hand off: the user engages, and you answer their questions and help them weigh the findings, acting only on an explicit verdict.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§6) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- `gh pr view --comments` — the native bug-review pass that ran before you, and any prior review cycle's findings; read them so you don't re-flag what they caught.
- Where the change includes code, the tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root). Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§6) rather than review broken work. Don't run individual lint tools yourself; where there's no `make check` to run, proceed to the audit.

## 3. Audit the change

Read the change as a whole — the brief and the change together — against the standards it answers to. The diff's nature picks the dimensions; pin each finding to its file and line and the rule or criterion it breaches.

**Know your cycle first.** The cycle number is the count of prior `## Code review — …` comments on the PR, plus one. Cycles 1 and 2 are full reviews across the dimensions below. From cycle 3 on, the review is a lockdown: its sole job is verifying the prior review's Blocking findings are fixed — don't hunt for new findings, though anything you notice incidentally still gets reported.

**When the change includes code** — read [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) and [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) first; the build agent saw neither, so enforcing them is yours alone:

- **Brief fidelity.** Every acceptance criterion is satisfied, the desired behavior is captured with no silent gap, and nothing reaches past the brief's stated scope. Where the change carries tests, the gate proves they pass but not that they are honest — check each genuinely exercises the behavior the brief calls for rather than passing vacuously; where it carries none, check the change does what each criterion asks.
- **Testing conventions.** Where the change includes tests, they conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python conventions.** The code conforms to python-conventions.md — docstrings, fail-loudly, annotation style.
- **Code quality.** Deep modules behind small surfaces, clear naming, no dead code or needless duplication — the engineering judgment the standards don't spell out.

**When the change is docs or text only** — read [documentation conventions](~/workspace/dev-playbook/standards/doc-conventions.md) first:

- **Brief fidelity.** Every acceptance criterion is satisfied, with no silent gap, and nothing reaches past the brief's stated scope.
- **Documentation conventions.** The prose conforms to doc-conventions.md — voice, structure, one rule per section, current-state — and reads accurately against what it documents.

## 4. Attach findings

Stage the comment body in a `/tmp` file (e.g. `/tmp/code-review-<issue>.md`) — writes inside the worktree are denied, `/tmp` is allowed — then post one PR comment with `gh pr comment --body-file <path>`.

- **Head it with the reviewed revision and the cycle.** `## Code review — <sha> · cycle <n>`, using the short HEAD sha (`git rev-parse --short HEAD`) and the cycle number from §3. On a re-review — the PR already carries a prior `## Code review — …` comment — head it `## Code review — <sha> · cycle <n> (supersedes review of <prior-sha>)` and open with a one-line disposition of each prior finding (resolved / still open), so neither the user nor a later read treats the stale findings as live.
- **Every finding is a problem plus its fix.** State the believed problem and the action it calls for, grouped by severity — **Blocking** (a fidelity gap, a convention breach that matters, a bug) or **Suggestion** (a non-disqualifying improvement). Write nothing that isn't actionable: no "acceptable as written", "no action needed", "just noting", and no explaining why a clean thing is clean — detail belongs to Blocking and Suggestion findings alone. Where you are genuinely unsure, raise it as a question or risk, naming the decision the user faces.
- **A real problem outside this PR's scope** — highlight it and recommend a follow-up issue; never open one yourself.
- Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or criterion it breaches. Enumerate the clean dimensions bare — names only, no per-dimension justification; if the whole diff is clean, say so plainly — a clean review is a real outcome.

Then emit your terminal line and stop — the goal yields and the user takes over:

```
DONE: <repo>#<issue> · current phase: code-pr-review · findings on PR · awaiting human review
```

## 5. Take the verdict

The user has read the findings. Engage — answer questions, weigh the findings, help them think — but make no change to the code under review; a fix is the implementer's to make on rework. Rework is Blocking-driven by default — Suggestions alone don't call for a rework lap. Act only on an explicit verdict:

- **approve** — the work is ready to merge. The user squash-merges in the GitHub UI; you can't (the PAT can't merge). Their merge drops the origin branch and closes the issue via the PR's `Closes #<issue>`, so no label change follows. Worktree teardown is not yours — overwatch removes the local side after the user confirms the merge.
- **rework** — the work goes back to the implementer. Record the deciding reason, then route the label by the issue's `tests:*` value — `phase:tdd` for `tests:yes`, `phase:build` for `tests:no`:
  ```bash
  gh issue comment <issue> --body "<the user's reason>"
  gh issue edit <issue> --remove-label "phase:code-pr-review" --add-label "phase:<tdd|build>"
  ```

Then report the verdict, the transition, and the issue's new state in one line:

```
<repo>#<issue> · current phase: code-pr-review · next phase: <merged|tdd|build> · <verdict>
```

## 6. Escalations

While auditing — before the hand-off — whenever you can't produce the review, surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · current phase: code-pr-review · <where you're stuck and the call you need>
```

In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment; you escalate only when something stops you from producing the review at all.
