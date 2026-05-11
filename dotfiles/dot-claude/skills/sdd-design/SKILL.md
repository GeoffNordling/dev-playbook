---
name: sdd-design
description: Author design items (`dsn`) and pin `Interface:` lines from approved functional requirements. Use when an SDD-mode issue is in `phase/design` and needs `dsn` items / `Interface:` declarations, or when the user asks to design the implementation surface for approved `feat`/`req` items.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD Design

Author the project's design layer — `dsn` items pinning `Interface:` lines and design commitments — from approved functional requirements.

The flow has three phases: context loading, interview-driven planning, skeleton-then-prose drafting. The interview is the value of this skill.<!--  -->

## 1. Context loading

1. **Required reading — do not skip.** Use the Read tool on each file below before any other action. If any file is missing or unreadable, stop and surface that to the user — do not proceed without the standards loaded.
   - [Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — full grammar.
   - [Design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — commitment framing.
   - [Lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.
   - [Workflow standard](~/workspace/dev-playbook/standards/workflow.md) — labels, worktree convention, PR mechanics, spec-tools bootstrap caveat.

   After reading, post exactly this confirmation line to the user before proceeding: `Loaded: spec-standard, design-layer, lessons, workflow`.
2. **Run `pwd`.** The dispatcher cd's into the worktree before invoking this skill, but the env header's CWD was captured before that. Trust `pwd`, not the header — composing paths from a stale CWD lands outside the worktree.
3. **Require an issue number** in `$ARGUMENTS`. If empty, stop and tell the user to invoke via `/sdd <N>`.
4. Run `gh-show $ARGUMENTS` to load the issue. The body IS the contract.
5. If `pwd` did not already show a worktree path, resolve the worktree per the [workflow standard](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree).
6. Read the project's existing specs:
   - `specs/functional_requirements.md` (or folder-form). Without approved requirements, designing is premature.
   - `specs/design.md` (or folder-form).
   - `docs/adr/` for prior decisions in the area being designed.
7. Read the project's `CLAUDE.md`.
8. **Brownfield reconnaissance.** Read existing code the area touches. For each new capability, work out whether it extends an existing module or introduces a new one, and what public surface each requirement implies.

## 2. Area discovery interview

Before any planning, ask the user which design areas matter. Common areas:

- **Data shapes.** Field count and types on each proposed dataclass / exception.
- **API shape.** Public function signatures, module structure.
- **Exception strategy.** Plain `ValueError` vs structured exception types; raise-vs-return-as-data.
- **Naming.** Type and symbol names — each name's semantic load should read clearly.
- **CLI shape.** Subcommand dispatcher vs independent scripts; flag conventions.
- **Cross-cutting infrastructure.** Loaders, central types, dispatchers, etc.
- **Output format / packaging detail.** Whether the design pins these or leaves them to the build phase.
- **Module decomposition.** One module per `feat` vs grouping; where new modules sit.

Surface these to the user with your judgment on which look load-bearing for this issue. Ask the user to confirm, add areas you missed, and drop areas they don't care about.

## 3. Per-area preference interview

For each flagged area, surface the real choices as options with brief pros/cons and a recommendation. Use the AskUserQuestion tool when the area has discrete options.

## 4. Plan synthesis

Present a plan for explicit approval:

- **Scope.** Which requirements this pass covers, and which `dsn` satisfies each.
- **Skeletons.** For each planned `dsn`: id + heading + role + proposed `Interface:` line(s) + `Covers:` + `Needs:` + `Depends:`. No prose yet.
- **Decisions made.** Type names, exception strategy, CLI shape, etc., as resolved by interview.
- **Decisions deferred.** Anything still open.

Wait for approval before drafting prose.

## 5. Drafting

Principles:

- **Skeleton holds.** The `Interface:`, `Covers:`, `Needs:`, `Depends:` lines from the plan are locked. Add prose now.
- **Minimum viable shape.** Don't add a field, method, or new type unless you can name its caller. Prefer two fields over four.
- **Don't pin implementation.** Output format, packaging, internal walk shape, file paths — leave to the build phase unless a req constrains them.
- **No roadmap in `Comment:`.** Comments describe the current `dsn`; future plans live on the GitHub tracker. Often, `Comment:` is omitted.

Mechanics:

- When shaping public surfaces, first read [module design](~/workspace/dev-playbook/standards/module-design.md) — small-interface-deep-implementation, accept dependencies, return results, keep surface small.
- Write each `dsn` per the spec standard. `Interface:` lines fully qualify symbol paths and follow the spec standard's annotation idiom.
- Invoke /grill-with-docs when public-boundary terminology needs sharpening.
- For seam-finding or evaluating module depth larger than one item, **ask the user to open a fresh terminal** and invoke /improve-codebase-architecture there. Bring back its proposals through edits.
- Reference relevant ADRs rather than re-explaining them. Propose a new ADR for significant architectural decisions.
- Non-mandatory requirements (`SHOULD`, `MAY`) are optional in the design spec. Including one is a commitment to deliver it.

## 6. Closing review pass

Re-read each new `dsn`:

- [ ] Chains up to a `req` via `Covers:` (or is a root). `Needs:` declares verification.
- [ ] `Interface:` annotations and obligation prose conform to the spec standard.
- [ ] Honors the section 5 principles: minimum viable shape, no implementation pinning, no roadmap in `Comment:`.

Iterate until clean.

## 7. Closing the phase

When the user approves and the rubric passes:

1. **Final check sweep — leave the tree green.** Run the project's test suite, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). If a command is not defined, note the absence and continue. If any defined command fails, stop and surface it. Do not commit or bump the phase label on a red tree.
2. Run /commit to commit the design spec.
3. Bump the issue's phase label:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase/design" --add-label "phase/build"
   ```
4. Report: phase done. The user re-invokes `/sdd <N>` when ready to build.

## Output

Updated design spec markdown only — no stubs, no code, no tests.
