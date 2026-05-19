---
name: sdd-requirements
description: Use when the `/sdd` dispatcher routes a `phase/requirements` issue to this skill. Authors functional requirements — `feat` and `req` items — per the workspace SDD standards. Not invoked directly. `/sdd` loads the issue and sets up the worktree first.
disable-model-invocation: false
model: opus
effort: xhigh
---

# SDD Requirements

Author the project's functional requirements — `feat` (high-level capability) and `req` (functional requirement) items — following the workspace SDD standards.

The flow has three phases: context loading, interview-driven planning, skeleton-then-prose drafting. The interview is the value of this skill.<!--  -->

## 1. Context loading

The dispatcher has already loaded the issue (its body IS the contract) and placed you in its worktree.

1. **Required reading.** Use the Read tool on each file below before any other action. If any file is missing or unreadable, stop and surface that to the user — do not proceed without the standards loaded.
   - [Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — full grammar.
   - [Lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

   After reading, post exactly this confirmation line to the user before proceeding: `Loaded: spec-standard, lessons`.
2. Read the project's existing specs:
   - `specs/functional_requirements.md` (or folder-form).
   - `CONTEXT.md` for domain vocabulary, if present.
3. Read the project's `CLAUDE.md`.

## 2. Area discovery interview

Before any planning, ask the user which behavior areas matter. Start with this small list:

- **Success path.** The headline behavior the feat exists for.
- **Edge / error behavior.** What counts as malformed; raise vs return-as-data; what's silently accepted.
- **Scope boundary.** What's explicitly out of scope for this feat.

Other areas may surface naturally as the conversation goes — add them as they come up rather than enumerating up front.

Surface these to the user with your judgment on which look load-bearing for this issue. Ask the user to confirm, add areas you missed, and drop areas they don't care about.

## 3. Per-area preference interview

For each flagged area, surface the real choices as options with brief pros/cons and a recommendation. Use the AskUserQuestion tool when the area has discrete options.

## 4. Plan synthesis

Present a plan for explicit approval:

- **Scope.** Which behaviors this pass captures, and which `req` covers each.
- **Skeletons.** For each planned `feat` / `req`: id + heading + role + `Covers:` + `Needs:`. No `Description:` prose yet.
- **Decisions made.** Obligation level, granularity, edge-case treatment, etc., as resolved by interview.
- **Decisions deferred.** Anything still open.

Wait for approval before drafting prose.

## 5. Drafting

Principles:

- **Skeleton holds.** The `Covers:` and `Needs:` lines from the plan are locked. Add prose now.
- **Minimum viable shape.** Each `req` commits to one checkable behavior. Don't add a clause unless it adds a check.
- **Behavior, not method.** Describe what holds, not how. Implementation choices belong in the design phase.
- **One obligation level per item.** If `SHALL` and `SHOULD` content mixes, split into separate items.
- **Non-mandatory inclusion is a commitment.** Including a `SHOULD` / `MAY` means you intend to deliver it.
- **No roadmap in `Comment:`.** Comments describe the current item; future plans live on the GitHub tracker. Often, `Comment:` is omitted.

Mechanics:

- Write each item per the spec standard. `Description:` follows the spec standard's EARS templates and obligation vocabulary.
- Invoke /grill-with-docs when domain terminology is fuzzy or `CONTEXT.md` needs updating.
- Each `feat` has an out-of-scope section. Ask whether anything belongs there; if not, `NA` is fine.
- Reference relevant ADRs rather than re-explaining them.

## 6. Closing review pass

Re-read each new `feat` / `req`:

- [ ] Chains up to a `feat` via `Covers:` (or is a root). `Needs:` declares verification.
- [ ] `Description:` conforms to the spec standard (EARS template, single obligation level).
- [ ] Honors the section 5 principles: minimum viable shape, behavior not method, no roadmap in `Comment:`.
- [ ] Every `feat`'s out-of-scope section is answered (`NA` is fine).

Iterate until clean.

## 7. Closing the phase

When the user approves and the rubric passes:

1. **Final check sweep — leave the tree green.** Run the project's test suite, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). If a command is not defined, note the absence and continue. If any defined command fails, stop and surface it. Do not commit or bump the phase label on a red tree.
2. Run /commit to commit the spec markdown.
3. Bump the issue's phase label:
   ```bash
   gh issue edit <issue-number> --remove-label "phase/requirements" --add-label "phase/design"
   ```
4. Report: phase done. The user re-invokes `/sdd <issue-number>` when ready for design.

## Output

Spec markdown only — no code, no tests, no design items.
