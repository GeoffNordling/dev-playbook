---
type: General-Sheet
title: Registry Refactor
description: The decisions aligned on for the document-type registry refactor — the rejection axis, the abstractions, the software factory's position, and the open questions
---

# Registry Refactor

The decisions the user and Claude aligned on in the 2026-09-02 session
that opened the registry refactor. Member of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md). The
file counts and per-file readings behind these decisions are the audit
record, [Registry Audit](/no-more-slop-branch-working-files/REGISTRY-AUDIT.md);
nothing there is a decision.

Only what was said in that session is written here. Where a question was
raised and not settled, it sits under Open questions with no lean.

## Goal

Refactor the document-type registry before building any new doc-type:
settle what a Standard is, what a Guide is, and how the kinds are
organized. The settling happens at one level, parsimonious and precise
enough to show on screen as pseudocode, definitions and instantiations
together. Decisions are made at that level; everything below it is
implementation, audit, and enforcement.

## Decisions

**The axis.** Can a reviewer or a lint cite the document to reject work?
Yes is a Standard. No is something else: possibly a Guide, possibly a
file type not yet defined.

**State, never process.** "Reject", based on a Standard, means the state of an object at one
moment. Standards govern objects. A process is never audited by its
trace; it is checked only through the objects it produces. Auditing that
an agent followed a documented process step for step, and rejecting the
result on a deviation, is the wrong kind of audit and the wrong kind of
enforcement.

**Object.** A thing with a state readable at one moment: a file, a tree,
a pull request, an issue, a label set.

**Process.** Actions by actors over time, consuming and producing
objects. A process is described for a reader or executed by an agent.

Object and Process are provisional: it is not settled that either
needs defining precisely.

**Standard-Card.** What the built doc-type today named Standard actually
is: its own definition file says the family is the population of cards
under `standards/`, so the shape, the cells, and the lint belong to the
card. Rename it.

**Standard.** The kind a card's Define cell points at, and the doc-type
not yet built. One object class as its population, plus named rules,
each a predicate over that class's state. Today's 38 files typed
`Standard` are this kind's population.

**Three collections, computed correspondence.** Think of it as code: a
collection of rules, a collection of audits, a collection of
enforcements. No rule states whether an audit or an enforcement
corresponds to it. Whether one does is a computation over the three
collections, and drift is what that computation finds.

**Rule IDs as atoms.** The rule ID already in the code,
`knowledge-organization.type-location` being one, is the atom that
joins the collections. Lean into it wherever it makes sense; sometimes
a judgment call is required instead.

**Every object becomes a doc-type.** Once the high-level pseudocode
objects are aligned on, each becomes a doc-type. That is the
innovation of doc-type: complex documentation expressed as simple,
precise pseudocode, which lets it all be scaffolded by 100%
deterministic code rising from the bedrock of determinism.

**Guide.** Explanation of a process or a system, read to understand it.
Never cited to reject. The registry's sentence "not to be measured
against" is retired and replaced by what a Guide is.

**Location.** Cards stay flat under `standards/`, Standards stay under
`standards/<name>/`, and both lints stay. The documents a card points at
may live anywhere. A Define cell points only at Standards; a Guide is
linked from a Standard's prose, never from a card.

**The software factory.** Its current documentation is not worth
reorganizing around, and it is not the long-term state. It stays typed
`Guide` for now, knowingly mislabeled, and the factory needs no card
until its rules exist. The intended split, when the rewrite comes:
object-state rules (the pull request body's sections, the cycle header,
the label four-tuple) become a Standard under
`standards/software-factory/`; the two regions and the moves between
them become a Guide where they are; the `gh` mechanics move into the
review runbooks. Rules that link to no standard are acceptable.

## The rule/procedure split

Located, because the user wanted to remember where it is. One home:
[File Roles](/standards/knowledge-organization/file-roles.md). A rule
binds every actor who touches the thing, whatever job that actor is
doing; a procedure binds one actor for the length of one run. The split
is declared "a general aim, not a strict gate". The
imperative-versus-declarative voice rule is a separate rule, in
[Doc Conventions](/standards/prose/conventions.md#person-of-address).

## Open questions

Raised, not settled. No lean recorded.

- The fate of the existing card `standards/software-factory.md`, which
  lists all nine factory documents in its Define cell.
- What replaces `General-Sheet`, which the user named a cop-out, and
  what type working-set files carry.
- The type the doc-type family's own files carry.
- The three files typed `Standard` that describe themselves as recipes.
- Which of this file's decisions move to a permanent home in the
  repository, and where. Some will; not all; which is not yet known.
- Edge cases not yet examined.

## Out of scope

The instrument, the instrument spec, and anything to do with
instruments. The user is not happy with the current implementation and
does not want to delete it either. Set aside; not thought about in this
refactor.

## Done when

Every area of the repository's documentation is covered, in one of two
ways: excluded explicitly in the registry as not important, or
expressed reliably, precisely, and parsimoniously as high-level
abstract pseudocode, deterministically connectable to CLOA objects
that connect to the bedrock of determinism. None of it needs to be
implemented in code yet. The high-level abstract objects must be
complete, with low residuals.

## Next step

Write the abstractions as pseudocode on screen: Object, Process,
Standard-Card, Standard, Guide, Runbook, their definitions and this
repo's instantiations. Then work the open questions at that level.

## Acronyms

None. CLOA is defined in the root, [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#acronyms).
