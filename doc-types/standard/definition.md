---
type: General-Sheet
title: Standard
description: What a standard is — a normative target that is defined, audited, enforced, and adopted — its four verbs, the two file kinds it is written across, the family it serves, how it is named and scoped, and where it lives
---

# Standard

A **standard** is a normative target: a state some class of object is
held to, that a reviewer or a lint could cite to reject work. A
standard has no notion of moving toward the state, only of being in or
out of it; driving toward it is [Loop](/doc-types/loop/definition.md)'s.

## The verbs

Four, each a cell of the standard's card:

- **define** — the rulesets that describe the state.
- **audit** — the detectors that measure one member against it.
- **enforce** — the gate or on-demand tool that compels it.
- **adopt** — what brings a repository into it the first time.

## The kinds

A standard is written across two file kinds of the
[document-type registry](/standards/knowledge-organization/document-types.md),
exactly one card and any number of rulesets:

- **The card** — `standards/<name>/card.md`, typed `Standard-Card`. The
  record of the four verbs: it names the question the standard governs
  and holds one cell per verb, each a list of pointers. A card points;
  it never restates.
- **A ruleset** — `standards/<name>/<topic>.md`, typed
  `Standard-Ruleset`. What a Define cell points at: one population and
  its rules, each rule a predicate over one member's state.

The state is described twice. A ruleset's text is the prose form, what
a writer reads to know what to make; the detectors the Audit cell
locates, deterministic or a model returning a value, are the checkable
form, what says whether one member is in the state.

## The family

The directories under `standards/`, one per standard: `standards/prose/`
holds the card and the rulesets that bind an authored document,
`standards/build/` those that bind a repo's tracked tree. A standard
does one thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its question, and the rulesets and detectors that answer it. A rule's
body may carry the reason that keeps the rule from looking wrong;
procedure and a writer's heuristics are other documents' things.

## Named by the question

A standard is named by the question it governs, not by the current
answer. "How knowledge is organized in markdown" is the question; the
OKF spec is today's answer, pointed at by the Define cell. The litmus:
if the implementation could be swapped while the name stays true, the
name is a standard's.

- **Membership is non-exclusive.** A file may be pointed at by more
  than one card. Standards are overlapping views over the repository,
  not a partition of it — pointers, not directory placement, say what
  belongs to what.

## What a standard is not

Not everything normative is a standard. A device built to serve a
purpose — an artifact format, a tool, a template — is an answer, so it
belongs inside a cell rather than in the catalog.

## Scope

Every standard has a **scope** — the population it governs:

- **Workspace-scoped** — declared in dev-playbook, governing every repo
  in `~/workspace`. The bulk of the catalog is workspace-scoped: the
  cross-project standards every repo inherits through dev-playbook's
  published hooks.
- **Repo-scoped** — declared in one consumer repo, governing that repo
  alone. A repo stands one up when it has a convention no other repo
  shares; the recipe is
  [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md).

Exactly two levels — a standard governs the whole workspace or a single
repo, never an intermediate group. Deeper nesting is deliberately
unsupported (YAGNI): no third scope is introduced until a real
population sits between "one repo" and "every repo."

**No shadowing.** A repo-scoped standard's directory name is one no
workspace-scoped standard carries, since a consumer's
`standards/<name>/card.md` on an upstream name would silently override
the upstream standard of that name; the rule and its lint are
[No shadowing](/standards/standard/cards.md#no-shadowing).

## Where a standard lives

Both kinds live under `standards/`, the one tree reserved for them;
nothing outside it claims either label. okf-lint's
`knowledge-organization.type-location` checks it. The card is
`standards/<name>/card.md` and every immediate subdirectory of
`standards/` except `references/` holds one; the rulesets sit beside it.
The layout's rule and its lint are
[Directory layout](/standards/standard/cards.md#directory-layout); the
file forms are [the encoding](/doc-types/standard/encoding.md).
