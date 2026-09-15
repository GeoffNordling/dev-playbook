---
type: Standard-Ruleset
title: Card Catalog
description: A repo's card catalog, the card directories under standards/ and the index that lists them — the directory layout, the question sentence, the directory's introduction, what Define and Audit cite, no shadowing of an upstream card, and the catalog's order
population: "a repo's card catalog: the standards/<name>/ card directories and the standards/index.md that lists them"
---

# Card Catalog

A repo's card catalog: the `standards/<name>/` card directories and the
`standards/index.md` that lists them. A card is the catalog record for
one standard, named by the question it governs, and points at the files
that define, audit, enforce, and adopt it. What a card is, its four
cells, and the view `scripts/cardgen` collapses it to are the
Standard doc-type
([Standard](/doc-types/standard/definition.md),
[Cells and Rulesets](/doc-types/standard/contract-shape.md),
[Cells and Rulesets Encoding](/doc-types/standard/encoding.md)). The rules
below bind the catalog's state; standards-lint reports six of them, and
the pre-commit suite stations it at the commit gate
([Meta-Standard](/standards/standard/card.md#enforce)).

## Directory layout

Every immediate subdirectory of `standards/` except `references/` is a
card directory: it holds `card.md`, typed `Standard-Card`, with Define,
Audit, Enforce, and Adopt as its H2 sections, in that order, each once,
and the only flat files under `standards/` are `README.md` and
`index.md`; standards-lint reports a departure (`standard.card-layout`).

The tree's rule is one directory, one standard: the card and the
Standards it defines itself by sit together, one documentation set
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)),
with the Standards at `standards/<name>/<standard>.md`
([Where a Standard lives](/doc-types/standard/definition.md#where-a-standard-lives)).
A filename on either level is a kebab-case noun, `card.md` and `index.md`
the two fixed role names
([Naming](/doc-types/standard/encoding.md#naming)). `references/`
holds vendored mirrors and no card.

## The question sentence

The sentence after a card's H1 opens `Governs how`, names the governed
territory in one breath, and is repeated verbatim less the period by the
frontmatter `description`; standards-lint reports a pair that has come
apart (`standard.card-question`).

The catalog row and the card then state one remit. A card is named by
the question its standard governs, so the name holds when the answer is
swapped
([Named by the question](/doc-types/standard/definition.md#named-by-the-question)).

## The directory's introduction

A card directory's `index.md` opens with the card's title and its
question sentence, names in a sentence of its own any member the Define
cell does not point at, and lists the card first; standards-lint reports
an index that does not open with its card (`standard.card-directory`).

The introduction is the set's concern
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)).
The card is a summary of its Standards, not a rival to them, so
[distinct concerns](/standards/knowledge-organization/documentation-sets/documentation-sets.md#distinct-concerns)
is judged among the Standards and never against the card.

## Define points only at rulesets

Every Define pointer targets a document typed `Standard-Ruleset`, and a Define
bullet is the link alone, with no ` — ` annotation; standards-lint
reports an annotated bullet (`standard.card-layout`).

A Guide is linked from a Standard's prose or from the Adopt cell; a tool
from the Audit, Enforce, or Adopt cell; and a doc-type file from a
Standard's prose or from a card's lead paragraph. A Standard's one-line
summary lives once, in the directory's index listing, which carries its
`description` verbatim
([one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home));
cardgen reads only the link
([Cells](/doc-types/standard/encoding.md#cells)). No lint checks the
target's type. The field is `define: list[Pointer[Ruleset]]` in
[Cells and Rulesets](/doc-types/standard/contract-shape.md#the-card).

## Audit cites a lint

An Audit bullet cites a first-party lint by a `/scripts/` link; a
third-party detector by its bare name and pin; and a cell with no checker
holds the one bullet `none`.

A lint is a deterministic detector held to the `--list-rules` contract
([Detectors](/standards/standard/detectors.md#a-first-party-detector)).
standards-lint's rule matrix collects only the `/scripts/` links
(`standard.rule-matrix`), so a bare name sits outside it by construction.
A card audits `none` when no automatic check exists, so the gap stays
visible.

## No shadowing

A repo-scoped card directory's name is one no card directory
dev-playbook publishes carries; standards-lint reports the collision at
the consumer's commit gate (`standard.card-shadows-upstream`).

A consumer's `standards/<name>/card.md` on an upstream name would
silently override the workspace-scoped standard of that name. The two
scopes are [Scope](/doc-types/standard/definition.md#scope).

## The catalog

A repo carrying cards has a `standards/index.md` listing `README.md`
first and then every directory, in dev-playbook the Meta-Standard's
`standard/` next, the rest alphabetical by name, each card directory's
row carrying the card's `description` verbatim; standards-lint reports
the order and a row's description (`standard.catalog-order`), and
okf-lint the membership
([The listing](/standards/knowledge-organization/indexes.md#the-listing)).
