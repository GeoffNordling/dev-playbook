---
name: sdd-spec-review
description: Reviews an SDD project's authored spec against the issue brief and the spec standard, attaches findings to the issue, then takes the user's verdict — approve to TDD, or rework back to the spec author. Use when the agents dashboard launches the spec-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
argument-hint: "<issue-number>"
---

# SDD Spec Review

Review an SDD project's authored spec — its `feat`, `req`, and `dsn` items — against the issue brief and the spec standard, attach your findings to the issue, then take the user's verdict on them. One node, two halves: you audit on your own and post the findings, then the user reads them and tells you to approve or rework, and you carry out the transition. You never modify the spec under review — a defect routes back to the author through the user's rework, not your hand.

The audit runs hands-off; finding spec problems is its output, not a reason to stop. Once the findings are posted you hand off: the user engages, and you answer their questions and help them weigh the findings, acting only on an explicit verdict.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — the grammar you audit against: keyword reference, EARS templates, coverage chain, the consistency/completeness split (§1.3), the `WIP:` marker (§2.10).
- [design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — what a `dsn` pins, so you can judge whether the design is right-sized.
- [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

Then report: `READ: spec-standard.md, design-layer.md, lessons.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§6) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the brief is your fidelity target; the comments carry any prior review cycle's findings.
- The specs under `specs/functional_requirements/` and `specs/design/` — the full `feat`/`req`/`dsn` set under review.
- Existing code under `src/`, where the design is brownfield — context for judging whether the `Interface:` lines fit what's there.

## 2. Consistency gate

Run the gate — `make check`; it builds and validates the spec graph. The `feat`s under review are still `WIP:`, so completeness is exempt and only **consistency** is enforced (§2.10). Green: proceed to the audit. Red: the graph is malformed and the author should not have closed it — escalate (§6) rather than review a broken spec.

## 3. Audit the spec

Read the whole spec against the brief and the standard. Assess each dimension and collect what you find, pinning each finding to the specific item and the element it breaches.

- **Fidelity to the brief.** Every acceptance criterion maps to a covering `req`/`dsn`; the desired behavior is fully captured with no silent gap; nothing specced lies outside the brief's stated scope.
- **Requirements quality.** Each `req` conforms to an EARS template at a single obligation level, commits to one checkable behavior, describes behavior not method, and keeps `Rationale:`/`Comment:` non-prescriptive.
- **Design quality.** Each `dsn`'s `Interface:` follows the annotation idiom and fully qualifies its symbols; the shape is minimum-viable — every field, method, and type has an actual user you can point to; implementation is not over-pinned, leaving output format, file paths, and internal structure to build unless a `req` constrains them.
- **Chain soundness.** Coverage is meaningful, not merely structural: each `dsn` actually satisfies the `req` it `Covers:`, each `req` actually serves its `feat`, and `Needs:` declares real verification. Every unbuilt `feat` carries `WIP:` — a `feat` without it at this phase is an anomaly worth a finding.

## 4. Attach findings

Stage the comment body in a `/tmp` file (e.g. `/tmp/spec-review-<issue>.md`) — writes inside the worktree are denied, `/tmp` is allowed — then post one comment with `gh issue comment <issue> --body-file <path>`.

- **Head it with the reviewed revision.** `## Spec review — <sha>`, using the short HEAD sha (`git rev-parse --short HEAD`). On a re-review — the issue already carries a prior `## Spec review — …` comment — head it `## Spec review — <sha> (supersedes review of <prior-sha>)` and open with a one-line disposition of each prior finding (resolved / still open), so neither the user nor a later read treats the stale findings as live.
- **Every finding is a problem plus its fix.** State the believed problem and the action it calls for, grouped by severity — **Blocking** (a fidelity gap, a malformed item, an unsound chain) or **Suggestion** (a non-disqualifying improvement). Write nothing that isn't actionable: no "acceptable as written", "no action needed", or "just noting". Where you are genuinely unsure, raise it as a question or risk, naming the decision the user faces.
- **A real problem outside this spec's scope** — highlight it and recommend a follow-up issue; never open one yourself.
- Name the item id and the brief element or standard rule each finding breaches. State which dimensions came back clean; if the whole spec is clean, say so plainly — a clean review is a real outcome.

Then emit your terminal line and stop — the goal yields and the user takes over:

```
DONE: <repo>#<issue> · current phase: sdd-spec-review · findings on issue · awaiting human review
```

## 5. Take the verdict

The user has read the findings. Engage — answer questions, weigh the findings, help them think — but make no change to the spec under review; a fix is the author's to make on rework. Act only on an explicit verdict:

- **approve** — the spec is ready. Advance to TDD:
  ```bash
  gh issue edit <issue> --remove-label "phase:sdd-spec-review" --add-label "phase:sdd-tdd"
  ```
- **rework** — the spec goes back to the author. Record the deciding reason so the author reads it alongside your findings, then route back:
  ```bash
  gh issue comment <issue> --body "<the user's reason>"
  gh issue edit <issue> --remove-label "phase:sdd-spec-review" --add-label "phase:sdd-specs"
  ```

Then report the verdict, the transition, and the issue's new state in one line:

```
<repo>#<issue> · current phase: sdd-spec-review · next phase: <sdd-tdd|sdd-specs> · <verdict>
```

## 6. Escalations

While auditing — before the hand-off — whenever you can't produce the review, surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · current phase: sdd-spec-review · <where you're stuck and the call you need>
```

In particular:

- **Consistency gate red.** The check gate fails: the spec is malformed and the author should not have closed it. Surface it; don't review a broken graph.
- **Specs missing or unreadable.** There is no spec to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A spec problem you can describe goes in the §4 comment; you escalate only when something stops you from producing the review at all.
