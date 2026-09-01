---
type: General-Sheet
title: Standard
description: What a standard is and is not, and the scope axis — the population a standard governs
---

# Standard

A **standard** states a rule the workspace holds itself to, named by
the question it governs. The family is the population of cards under
`standards/`, and the Standard doc-type hands it its contract shape:
the card, declared in
[contract-shape.md](/doc-types/standard/contract-shape.md).

## What a standard is

A standard is named by the question it governs, not by the current answer.
"How knowledge is organized in markdown" is a standard; the OKF spec is
today's answer, pointed at by its define cell. The litmus: if the
implementation could be swapped while the name stays true, it is a
standard.

- **Membership is non-exclusive.** A file may belong to more than one
  standard at once. Standards are overlapping views over the repository,
  not a partition of it — pointers, not directory placement, say what
  belongs to what.

## What a standard is not

Not everything normative is a standard. A device built to serve a purpose
— an artifact format, a tool, a template — is an answer, so it belongs
inside a cell rather than in the catalog. Such devices are **instruments**;
each carries a prescriptive contract of its own, typed `Instrument-Spec`.
The instrument concept is defined in
[Instruments and Instrument Specs](/standards/instrument/format.md).

## Scope

Every standard has a **scope** — the population it governs:

- **Workspace-scoped** — declared in dev-playbook, governing every repo in
  `~/workspace`. The bulk of the catalog is workspace-scoped: the
  cross-project standards every repo inherits through dev-playbook's published
  hooks.
- **Repo-scoped** — declared in one consumer repo, governing that repo alone.
  A repo stands one up when it has a convention no other repo shares; the
  recipe is
  [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md).

Exactly two levels — a standard governs the whole workspace or a single repo,
never an intermediate group. Deeper nesting is deliberately unsupported
(YAGNI): no third scope is introduced until a real population sits between
"one repo" and "every repo."

**No shadowing.** A repo-scoped card may not reuse a workspace-scoped card's
name. A consumer's `standards/<name>.md` may not collide with a card stem
dev-playbook publishes, because that would silently override the upstream
standard of that name; the rule `standard.card-shadows-upstream` catches the
collision at the consumer's commit gate.
