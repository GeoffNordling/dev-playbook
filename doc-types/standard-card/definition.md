---
type: General-Sheet
title: Standard-Card
description: What a standard card is — the catalog record for one standard, named by the question it governs — its scope axis, and what a standard is not
---

# Standard-Card

A **standard card** is the catalog record for one standard: it names the
question the standard governs and points at the files that define,
audit, enforce, and adopt it. The family is the population of cards, the
flat files under `standards/`. A card points; it never restates. What a standard *is* — a population and the
rules over it — belongs to the Standard doc-type,
[doc-types/standard/](/doc-types/standard/index.md).

## Named by the question

A card is named by the question its standard governs, not by the current
answer. "How knowledge is organized in markdown" is the question; the OKF
spec is today's answer, pointed at by the Define cell. The litmus: if the
implementation could be swapped while the name stays true, the name is a
card's.

- **Membership is non-exclusive.** A file may be pointed at by more than
  one card. Cards are overlapping views over the repository, not a
  partition of it — pointers, not directory placement, say what belongs
  to what.

## What a standard is not

Not everything normative is a standard. A device built to serve a purpose
— an artifact format, a tool, a template — is an answer, so it belongs
inside a cell rather than in the catalog. Such devices are **instruments**;
each carries a prescriptive contract of its own, typed `Instrument-Spec`.
The instrument concept is defined in
[Instruments and Instrument Specs](/standards/instrument/format.md).

## Scope

Every card has a **scope** — the population its standard governs:

- **Workspace-scoped** — declared in dev-playbook, governing every repo in
  `~/workspace`. The bulk of the catalog is workspace-scoped: the
  cross-project standards every repo inherits through dev-playbook's published
  hooks.
- **Repo-scoped** — declared in one consumer repo, governing that repo alone.
  A repo stands one up when it has a convention no other repo shares; the
  recipe is
  [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md).

Exactly two levels — a card governs the whole workspace or a single repo,
never an intermediate group. Deeper nesting is deliberately unsupported
(YAGNI): no third scope is introduced until a real population sits between
"one repo" and "every repo."

**No shadowing.** A repo-scoped card may not reuse a workspace-scoped card's
name. A consumer's `standards/<name>.md` may not collide with a card stem
dev-playbook publishes, because that would silently override the upstream
standard of that name; the rule `standard.card-shadows-upstream` catches the
collision at the consumer's commit gate.
