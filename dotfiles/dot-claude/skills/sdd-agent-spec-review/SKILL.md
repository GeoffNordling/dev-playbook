---
name: sdd-agent-spec-review
description: Reviews an SDD project's authored spec — its `feat`/`req`/`dsn` items — against the issue brief and the spec standard, attaches findings to the issue, then advances it to human spec review. Use when the agents dashboard launches the spec-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue view *) Bash(gh issue comment *) Bash(gh issue edit *) Bash(make *)
argument-hint: "<issue-number>"
---

# SDD Agent Spec Review

Review an SDD project's authored spec — its `feat`, `req`, and `dsn` items — against the issue brief and the spec standard, attach your findings to the issue, then advance it to human review. You audit and report; you never edit the spec. A defect routes back to design through the human's reject, not through your hand.

Work without waiting for approval: run the gate, audit, and post your findings on your own, pausing only to escalate on the §6 triggers. Finding spec problems is the job, not a reason to stop — they go in the comment for the human, who decides at the next node whether to approve, review it again, or send the spec back to design.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — the grammar you audit against: keyword reference, EARS templates, coverage chain, the consistency/completeness split (§1.3), the `WIP:` marker (§2.10).
- [design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — what a `dsn` pins, so you can judge whether the design is right-sized.
- [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

Then report: `READ: spec-standard.md, design-layer.md, lessons.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. Work happens on the issue's branch.

- `gh issue view <issue>` — the brief is your fidelity target: every acceptance criterion should land in the spec, and nothing in the spec should reach past the brief's scope.
- The specs under `specs/functional_requirements/` and `specs/design/` — the full `feat`/`req`/`dsn` set under review.
- Existing code under `src/`, where the design is brownfield — context for judging whether the `Interface:` lines fit what's there.

## 2. Consistency gate

Run the project's check gate (per `CLAUDE.md` / `Makefile`) — it builds the spec graph. The `feat`s under review are still `WIP:`, so completeness is exempt (§2.10); the build still enforces **consistency**, which never is. Green: proceed to the audit. Red: the graph is malformed and design should not have closed it — escalate (§6) rather than review a broken spec.

## 3. Audit the spec

Read the whole spec against the brief and the standard. Assess each dimension and collect what you find, pinning each finding to the specific item and the element it breaches.

- **Fidelity to the brief.** Every acceptance criterion maps to a covering `req`/`dsn`; the desired behavior is fully captured with no silent gap; nothing specced lies outside the brief's stated scope.
- **Requirements quality.** Each `req` conforms to an EARS template at a single obligation level, commits to one checkable behavior, describes behavior not method, and keeps `Rationale:`/`Comment:` non-prescriptive.
- **Design quality.** Each `dsn`'s `Interface:` follows the annotation idiom and fully qualifies its symbols; the shape is minimum-viable — every field, method, and type has an actual user you can point to; implementation is not over-pinned, leaving output format, file paths, and internal structure to build unless a `req` constrains them.
- **Chain soundness.** Coverage is meaningful, not merely structural: each `dsn` actually satisfies the `req` it `Covers:`, each `req` actually serves its `feat`, and `Needs:` declares real verification. Every unbuilt `feat` carries `WIP:` — a `feat` without it at this phase is an anomaly worth a finding.

## 4. Attach findings

Post one comment with `gh issue comment <issue>`. Group findings by severity so the human can act on them:

- **Blocking** — a defect that should send the spec back: a fidelity gap, a malformed item, an unsound chain.
- **Suggestion** — an improvement that is not disqualifying.

Each finding names the item id and the brief element or standard rule it breaches. State which dimensions came back clean. If the whole spec is clean, say so plainly — a clean review is a real outcome, not a missing one.

## 5. Close the phase

Nothing changed on disk — there is no commit.

1. Advance to human review:
   ```bash
   gh issue edit <issue> --remove-label "phase:sdd-agent-spec-review" --add-label "phase:sdd-human-spec-review"
   ```
2. Emit the terminal line, then stop:
   ```
   DONE: reviewed spec for #<issue>, findings attached, issue at phase:sdd-human-spec-review
   ```
   Do not act on your own findings — the human reads them and decides whether to approve, review it again, or route back to design.

## 6. Escalations

You work without approval, but stop, surface the situation, and wait for the human's call whenever you can't complete the review — anything unexpected, or any wish to deviate. In particular:

- **Consistency gate red.** The check gate fails: the spec is malformed and design should not have closed it. Surface it; don't review a broken graph.
- **Specs missing or unreadable.** There is no spec to review, or the issue isn't in the state this phase expects.

Findings are not escalations. A spec problem you can describe goes in the §4 comment and rides to the human at the next node; you escalate only when something stops you from producing the review at all.
