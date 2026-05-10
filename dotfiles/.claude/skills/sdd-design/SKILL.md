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

## Read first

- [Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — full grammar.
- [Design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — commitment framing and the four design dimensions (Data, API Shape, Algorithms, Composition).
- [Lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.
- [Workflow standard](~/workspace/dev-playbook/standards/workflow.md) — labels, worktree convention, PR mechanics, spec-tools bootstrap caveat.

## First steps

1. **Require an issue number** in `$ARGUMENTS`. If empty, stop and tell the user to invoke via `/sdd <N>`.
2. Run `gh-show $ARGUMENTS` to load the issue. The body IS the contract.
3. Resolve the worktree per the [workflow standard](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree).
4. Read the project's existing specs:
   - `specs/functional_requirements.md` (or folder-form). Without approved requirements, designing is premature.
   - `specs/design.md` (or folder-form).
   - `docs/adr/` for prior decisions in the area being designed.
5. Read the project's `CLAUDE.md`.
6. **Brownfield reconnaissance.** Read existing code the area touches. For each new capability, work out whether it extends an existing module or introduces a new one, and what public surface each requirement implies. Record reasoning in each `dsn`'s `Rationale:`.
7. Tell the user what you found and align on scope.

## Mandatory plan gate

Before drafting `dsn` text, present a plan covering scope (which requirements the design pass will cover) and approach (the seams you anticipate, the public surfaces you intend to pin). Wait for explicit user approval.

## Drafting

- Walk the dimensions in canonical order: Data first, then API Shape, then Algorithms, then Composition.
- When shaping public surfaces, first read [module design](~/workspace/dev-playbook/standards/module-design.md) — small-interface-deep-implementation, accept dependencies, return results, keep surface small.
- Write each `dsn` per the spec standard. `Interface:` lines fully qualify symbol paths and use the workspace annotation idiom (built-in generics, `X | None` for optional, no `typing.List`).
- Use the interview pattern. Invoke /grill-with-docs when public-boundary terminology needs sharpening.
- For seam-finding or evaluating module depth larger than one item, **ask the user to open a fresh terminal** and invoke /improve-codebase-architecture there. Bring back its proposals through edits to this design pass.
- Reference relevant ADRs rather than re-explaining their reasoning. Propose a new ADR if a significant new architectural decision emerges.
- Non-mandatory requirements (`SHOULD`, `MAY`) are optional in the design spec. Including one is a commitment to deliver it.

Stubs are not produced here. `sdd-tdd` creates them lazily on first contact with a test, matching each committed `Interface:` verbatim.

## Closing review pass

Before declaring the phase done, run the rubric. Each item is a yes/no check.

- [ ] Every `dsn` has a `Covers:` to a `req` (or is a root)?
- [ ] Every `Interface:` is matched by a behavioural commitment in `Description:` (not a signature in isolation)?
- [ ] Every `Interface:` uses the workspace annotation idiom (built-in generics, `X | None`, no `typing.List`)?
- [ ] Every `dsn` declares `Needs:` or carries `AgentReview:`?
- [ ] Every standard rule the design leans on is named explicitly (cited ADRs, `module-design.md`)?

Surface failures and iterate until the rubric is clean.

## Closing the phase

When the user approves and the rubric passes:

1. Run /commit to commit the design spec.
2. Bump the issue's phase label:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase/design" --add-label "phase/build"
   ```
3. Report: phase done. The user re-invokes `/sdd <N>` when ready to build.

## Output

Updated design spec markdown only — no stubs, no code, no tests.
