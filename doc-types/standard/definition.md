---
type: General-Sheet
title: Standard
description: What a Standard is — one class of object as its population, plus named rules over one member's state — the family it serves, and where it lives
---

# Standard

A **Standard** is the kind a card's Define cell points at
([Standard-Card](/doc-types/standard-card/definition.md)): one class of
object as its population, plus named rules, each a predicate over one
member's state. A reviewer or a lint cites a rule to reject work; the
rejection is about the state of one object at one moment, never about
the process that produced it.

The family is the documents typed `Standard` under the card
directories: `standards/prose/conventions.md` binds an authored
document, `standards/build/skeleton.md` binds a repo's tracked tree. A
Standard does one thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its population and its rules. Rationale, procedure, and a writer's
heuristics are other documents' things.

## Where a Standard lives

A document typed `Standard` lives under `standards/`; nothing outside that tree
claims the label. okf-lint's `knowledge-organization.type-location` checks it.

The card binds the other way: a Define cell points only at Standards, so
every file a card defines itself by carries the label and sits in the tree.
