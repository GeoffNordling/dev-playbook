---
type: General-Sheet
title: Card Cells Encoding
description: The layer below the card — how a cell's bullets encode pointers for cardgen, where a card lives, how it is named, and the catalog that lists it
---

# Card Cells Encoding

The layer below the
[cells](/doc-types/standard-card/contract-shape.md): the form a cell's
bullets take so `scripts/cardgen` reads every pointer deterministically,
where a card's file sits, what it is named, and the catalog that lists
every card.

## Cells

A cell is a bullet list, one pointer per bullet, or the single bullet
`none`. cardgen slices; it never interprets. The cut points are the
bullet marker, the first spaced em dash (` — `), the first markdown link
before that dash, and, in Enforce, the bold gate name.

- **The lead.** A bullet's text up to its first ` — ` is the lead.
  Everything after the dash is annotation: carried in the card, never
  read by the generator.
- **Define, Audit, Adopt.** The pointer is the target of the first link
  in the lead. A lead with no link is the pointer verbatim — the form for
  a third-party detector cited by its pin (`ruff`, `mypy`, `shellcheck`,
  `shfmt`), whose home is a pin, not a file in this repository.
- **Enforce.** The pointer is the gate the bullet names in bold —
  `**commit gate**`, `**push gate**`, or `**CI gate**` — exactly one per
  bullet, wherever it sits in the bullet. The three names are fixed by
  [Gates](/standards/standard/gates.md#three-rungs).
- **none.** A cell with nothing to point at holds the one bullet `none`,
  optionally followed by a colon and the reason. It renders as one `none`
  row.
- **Prose.** A paragraph in a cell that is not a bullet is opaque: cardgen
  carries nothing from it. A remark that is not a pointer — a chosen gap,
  what sits outside every gate — goes there, never in a bullet.

A bullet that breaks the form — a Define bullet with no link, an Enforce
bullet naming no gate or two, a `none` beside other bullets — fails the
generator: a card that cannot be sliced cannot be viewed.

## Where a card lives

A card is `standards/<name>.md`, flat, and every flat file there except
`README.md` and `index.md` is a card; the tree's rule is flat = card,
directory = content. standards-lint's `standard.card-layout` checks it.
Where a document typed `Standard` lives is the Standard doc-type's rule,
in [definition.md](/doc-types/standard/definition.md#where-a-standard-lives).

## Naming

A filename under `standards/`, card or contract document alike, is
kebab-case and names its topic as a noun: a plain
noun (`conventions.md`, `records.md`, `distribution.md`), a noun compound
(`cache-gate.md`, `context-content.md`), or a gerund compound
(`issue-authoring.md`) — never a bare verb
(`skill-write.md`). When a directory has an established family prefix, a
new sibling on the same subject keeps it.

## The catalog

Each repo that carries cards has its own catalog at `standards/index.md`; in
dev-playbook that is [standards/index.md](/standards/index.md). okf-lint's
index rule forces a catalog to list every card with a matching description.
