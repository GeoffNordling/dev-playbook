---
type: General-Sheet
title: Standard
description: What a Standard is — a description of a state, one class of object as its population plus named rules over one member's state, in prose and in checkers — the family it serves, and where it lives
---

# Standard

A **Standard** describes a state: one class of object as its
population, plus named rules, each a predicate over one member's
state. It describes that state twice. Its own text is the prose form,
what a writer reads to know what to make; the checkers its card's
Audit cell locates, deterministic or a model returning a value, are
the checkable form, what says whether one member is in the state
([Standard-Card](/doc-types/standard-card/definition.md)). A reviewer
or a lint cites a rule to reject work; the rejection is about the
state of one object at one moment, never about the process that
produced it. A Standard has no notion of moving toward the state, only
of being in or out of it; driving toward it is
[Loop](/doc-types/loop/definition.md)'s.

The family is the documents typed `Standard` under the card
directories: `standards/prose/conventions.md` binds an authored
document, `standards/build/skeleton.md` binds a repo's tracked tree. A
Standard does one thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its population and its rules. A rule's body may carry the reason that
keeps the rule from looking wrong; procedure and a writer's heuristics
are other documents' things.

## Where a Standard lives

A document typed `Standard` lives under `standards/`; nothing outside that tree
claims the label. okf-lint's `knowledge-organization.type-location` checks it.

The card binds the other way: a Define cell points only at Standards, so
every file a card defines itself by carries the label and sits in the tree.
