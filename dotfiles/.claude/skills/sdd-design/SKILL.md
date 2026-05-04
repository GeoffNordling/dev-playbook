---
name: sdd-design
description: Author design items (`dsn`) and pin `Interface:` lines from approved functional requirements
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD Design

Author the project's design layer — `dsn` items pinning `Interface:` lines and design commitments — from approved functional requirements. The user provides free-form input describing what to design.

## Read first

- [Spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md) — full grammar.
- [Design layer](~/workspace/dev-playbook/sdd-standards/design-layer.md) — commitment framing and the four design dimensions (Data, API Shape, Algorithms, Composition).
- [Lessons](~/workspace/dev-playbook/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

## First steps

1. **Require an issue number.** If `$ARGUMENTS` is empty, stop and tell the user to invoke with an issue number (e.g., `/sdd-design 18`). The issue is the per-session contract; without it there is no scope.
2. Run `gh-show $ARGUMENTS` to load the issue. The body sets the per-session contract; the most recent `## Agent Brief` comment pins category, scope, key interfaces, acceptance criteria, and out-of-scope boundaries.
3. Read the project's existing specs:
   - `specs/functional_requirements.md` or, if folder-form, `specs/functional_requirements/index.md` and the files it lists. Without approved requirements, designing is premature.
   - `specs/design.md` or, if folder-form, `specs/design/index.md` and the files it lists.
   - `docs/adr/` for prior architectural decisions in the area being designed (check `docs/adr/README.md` for the index).
4. Read the project's `CLAUDE.md`.
5. **Brownfield reconnaissance.** Read the existing code the area touches. For each new capability, work out whether it extends an existing module or introduces a new one, and what public surface each requirement implies. Record the reasoning in each `dsn`'s `Rationale:` when drafting.
6. Tell the user what you found and align on scope.

## Working with the spec collection

We are bootstrapping `spec-tools`; programmatic views are not available yet. Read existing `dsn` items directly and check coverage by hand against the approved requirements. A future revision of this skill will invoke `spec-tools` for slice views (downstream of a `req` to see which `dsn`s already cover it) and impact-analysis views (reverse slice from a `dsn` when contemplating a revision bump).

## Mandatory plan gate

Before drafting `dsn` text, present a plan covering scope (which requirements the design pass will cover) and approach (the seams you anticipate, the public surfaces you intend to pin). Wait for explicit user approval.

## Drafting

- Walk the dimensions in canonical order: Data first, then API Shape, then Algorithms, then Composition.
- When shaping public surfaces, first read [deep-modules.md](~/workspace/dev-playbook/dotfiles/.agents/skills/tdd/deep-modules.md) (small-interface-deep-implementation principle) and [interface-design.md](~/workspace/dev-playbook/dotfiles/.agents/skills/tdd/interface-design.md) (accept dependencies, return results, keep surface small) from the /tdd skill bundle.
- Write each `dsn` per the spec standard. `Interface:` lines fully qualify symbol paths and use the workspace annotation idiom (built-in generics, `X | None` for optional, no `typing.List`).
- Use the interview pattern. Invoke /grill-me when stress-testing a non-obvious design decision.
- For seam-finding or evaluating module depth at a scale larger than one item, **ask the user to open a fresh terminal** and invoke /improve-codebase-architecture there. Decisions return as edits to this design pass; the analysis itself does not pollute this context.
- Reference relevant ADRs rather than re-explaining their reasoning. Propose a new ADR if a significant new architectural decision emerges.
- Non-mandatory requirements (`SHOULD`, `MAY`) are optional in the design spec. Including one is a commitment to deliver it.
- Iterate with the user until the draft is approved.

Stubs are not produced here. `sdd-implementation` creates them lazily on first contact with a test, matching each committed `Interface:` verbatim.

## Output

Updated design spec markdown only — no stubs, no code, no tests.
