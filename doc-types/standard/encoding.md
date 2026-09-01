---
type: General-Sheet
title: Standard Card Encoding
description: The layer below the card — where a standard lives, how it is named, and the catalog that lists it
---

# Standard Card Encoding

The layer below the
[card](/doc-types/standard/contract-shape.md): where a standard's
files sit, what they are named, and the catalog that lists every card.

## Where a standard lives

A document typed `Standard` lives under `standards/`; nothing outside that tree
claims the label. okf-lint's `knowledge-organization.type-location` checks it.

This binds the type label, not membership — a card's define cell still points
wherever the contract is, and prose that governs without being a conformance
target takes another type.

## Naming

A standard's filename is kebab-case and names its topic as a noun: a plain
noun (`conventions.md`, `records.md`, `distribution.md`), a noun compound
(`cache-gate.md`, `context-content.md`), or a gerund compound
(`issue-authoring.md`) — never a bare verb
(`skill-write.md`). When a directory has an established family prefix, a
new sibling on the same subject keeps it.

## The catalog

Each repo that carries cards has its own catalog at `standards/index.md`; in
dev-playbook that is [standards/index.md](/standards/index.md). okf-lint's
index rule forces a catalog to list every card with a matching description.
