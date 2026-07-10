---
name: sdd-code-pr-review
description: Audits an SDD issue's PR against its committed spec and the project conventions, and attaches findings to the PR. Use when the issue overwatch launches the `sdd-code-pr-review` node.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# SDD Code & PR Review

Review an SDD issue's PR diff against its committed spec and the project's conventions, and attach your findings to the PR. The review is an audit only: you never modify the code under review, and the verdict on the findings is not yours to take — post them and stop.

An automated bug-review pass (the native `/code-review`) runs before you and posts its own PR comment; you add the spec-fidelity and convention findings it does not cover. The audit runs hands-off; finding code problems is its output, not a reason to stop.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — how to read the committed `feat`/`req`/`dsn` and `Interface:` lines you check the code against.
- [testing conventions](~/workspace/dev-playbook/standards/testing/conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [python style](~/workspace/dev-playbook/standards/python/style.md) — docstring rules, the fail-loud rule, the helpers bar, annotation style.
- [module design](~/workspace/dev-playbook/standards/modules/design.md) — deep modules, the deletion test, seams; what the Module design dimension audits against.

The implementer read the spec standard and testing conventions only; enforcing the style and design standards is yours alone.

Then report: `READ: spec-standard.md, testing-conventions.md, python-style.md, modules/design.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is the contract the work set out to satisfy.
- `gh pr diff` — the change under review (resolves the current branch's PR).
- The PR's existing feedback — the native bug-review pass that ran before you, and any prior review cycle's findings; to avoid re-flagging what they caught, read **every** comment surface on the PR: its body, top-level conversation comments, review summary bodies, and inline diff comments, from both user and agent reviewers. (`gh pr view --comments` shows the body and conversation but omits the inline diff comments, which live at `gh api repos/{owner}/{repo}/pulls/<pr>/comments`; review summaries are at `.../pulls/<pr>/reviews`.)
- The committed specs under `specs/functional_requirements/` and `specs/design/` — what the code must implement.
- The tests under `tests/` and code under `src/` — the full picture behind the diff.

## 2. Green gate

Run the gate — `make -C <subproject> check` (or `make check` when the `Makefile` is at the repo root). Green: proceed to the audit. Red: build opened a PR over a red tree — escalate (§5) rather than review broken work. Don't run individual lint tools yourself.

## 3. Audit the change

Read the change as a whole — the spec and the code together — against the conventions. Assess each dimension and collect what you find, pinning each finding to the file and line and the rule or spec item it breaches.

**Know your cycle first.** The cycle number is the count of prior `## Code review — …` comments on the PR, plus one. Cycles 1 and 2 are full reviews across the dimensions below. From cycle 3 on, the review is a lockdown: its sole job is verifying the prior review's Blocking findings are fixed — don't hunt for new findings, though anything you notice incidentally still gets reported.

- **Spec fidelity.** The gate already proves each spec item has a passing verifier; what it can't prove is that the verifier is honest. Reading spec and code together, check that each test genuinely exercises the behavior its `req`/`dsn` describes rather than passing vacuously, and that the code implements what the spec commits to without drifting past its scope.
- **Testing conventions.** The tests conform to testing-conventions.md — structure, naming, behavioral focus.
- **Python style.** The code conforms to python-style.md — docstrings, the fail-loud rule (no silent fallbacks or defensive guards), the helpers bar (a helper earns its place or stays inline), annotation style.
- **Module design.** The change conforms to modules/design.md — deep modules behind small interfaces, no pass-throughs that fail the deletion test, seams only where something varies — plus clear naming, no dead code or needless duplication.

**When the diff touches docs** — read [documentation conventions](~/workspace/dev-playbook/standards/prose/conventions.md) first and add:

- **Documentation conventions.** The prose conforms to doc-conventions.md — voice, structure, one rule per section, current-state — and reads accurately against what it documents.

## 4. Attach findings

Stage the comment body in a `/tmp` file (e.g. `/tmp/code-review-<issue>.md`) — writes inside the worktree are denied, `/tmp` is allowed — then post one PR comment with `gh pr comment --body-file <path>`.

- **Head it with the reviewed revision and the cycle.** `## Code review — <sha> · cycle <n>`, using the short HEAD sha (`git rev-parse --short HEAD`) and the cycle number from §3. On a re-review — the PR already carries a prior `## Code review — …` comment — head it `## Code review — <sha> · cycle <n> (supersedes review of <prior-sha>)` and open with a one-line disposition of each prior finding (resolved / still open), so neither the user nor a later read treats the stale findings as live.
- **Every finding is a problem plus its fix.** State the believed problem and the action it calls for, grouped by severity — **Blocking** (a fidelity gap, a convention breach that matters, a bug) or **Suggestion** (a non-disqualifying improvement). Write nothing that isn't actionable: no "acceptable as written", "no action needed", "just noting", and no explaining why a clean thing is clean — detail belongs to Blocking and Suggestion findings alone. Where you are genuinely unsure, raise it as a question or risk, naming the decision the user faces.
- **A real problem outside this PR's scope** — highlight it and recommend a follow-up issue; never open one yourself.
- Anchor each finding to its location with a blob link — `https://github.com/<owner>/<repo>/blob/<full-sha>/<path>#L<start>-L<end>`, using the full SHA from `git rev-parse HEAD` so GitHub renders a code preview — and name the rule or spec item it breaches. Enumerate the clean dimensions bare — names only, no per-dimension justification; if the whole diff is clean, say so plainly — a clean review is a real outcome.

Emit the terminal line, then stop:

```
DONE: <repo>#<issue> · phase: sdd-code-pr-review · findings on PR
```

## 5. Escalations

Whenever you can't produce the review, surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · phase: sdd-code-pr-review · <where you're stuck and the call you need>
```

In particular:

- **Green gate red.** The check gate fails: build opened a PR over a red tree. Surface it; don't review broken work.
- **PR or diff missing.** There is no PR to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A code problem you can describe goes in the §4 comment; you escalate only when something stops you from producing the review at all.
