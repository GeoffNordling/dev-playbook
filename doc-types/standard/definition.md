---
type: General-Sheet
title: Standard
description: What a Standard is — one object class as its population, plus named rules over that class's state — and where it lives
---

# Standard

A **Standard** is the kind a card's Define cell points at
([Standard-Card](/doc-types/standard-card/definition.md)): one object
class as its population, plus named rules, each a predicate over that
class's state. A reviewer or a lint cites a Standard to reject work; the
rejection is about the state of one object at one moment, never about
the process that produced it. The documents typed `Standard` under the
card directories are the family. Its loop has not run: this file holds
what is settled, and the contract shape, the encoding, the generator,
and the residual ledger arrive with the loop.

## Where a Standard lives

A document typed `Standard` lives under `standards/`; nothing outside that tree
claims the label. okf-lint's `knowledge-organization.type-location` checks it.

The card binds the other way: a Define cell points only at Standards, so
every file a card defines itself by carries the label and sits in the tree.
