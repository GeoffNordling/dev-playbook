---
type: Standard
title: Card Catalog
description: A repo's card catalog, the flat cards under standards/ and their index; the question sentence, what Define and Audit cite, no shadowing of an upstream card, and the catalog's order
population: "a repo's card catalog: the flat standards/<name>.md cards and the standards/index.md that lists them"
---

# Card Catalog

A repo's card catalog: the flat `standards/<name>.md` cards and the
`standards/index.md` that lists them. A card is the catalog record for
one standard, named by the question it governs, and points at the files
that define, audit, enforce, and adopt it. What a card is, its four
cells, and the view `scripts/cardgen` collapses it to are the
Standard-Card doc-type
([Standard-Card](/doc-types/standard-card/definition.md),
[Card Cells](/doc-types/standard-card/contract-shape.md),
[Card Cells Encoding](/doc-types/standard-card/encoding.md)). The rules
below bind the catalog's state; standards-lint reports four of them, and
the pre-commit suite stations it at the commit gate
([Meta-Standard](/standards/standard.md#enforce)).

## Flat layout

Every flat file under `standards/` except `README.md` and `index.md` is
a card: typed `Standard-Card`, with Define, Audit, Enforce, and Adopt as
its H2 sections, in that order, each once; standards-lint reports a
departure (`standard.card-layout`).

The tree's rule is flat = card, directory = content: a card's Standards
live under `standards/<name>/`
([Where a Standard lives](/doc-types/standard/definition.md#where-a-standard-lives)),
and a filename on either level is a kebab-case noun
([Naming](/doc-types/standard-card/encoding.md#naming)).

## The question sentence

The sentence after a card's H1 opens `Governs how`, names the governed
territory in one breath, and is repeated verbatim less the period by the
frontmatter `description`; standards-lint reports a pair that has come
apart (`standard.card-question`).

The catalog row and the card then state one remit. A card is named by
the question its standard governs, so the name holds when the answer is
swapped
([Named by the question](/doc-types/standard-card/definition.md#named-by-the-question)).

## Define points only at Standards

Every Define pointer targets a document typed `Standard`. A Guide is
linked from a Standard's prose or from the Adopt cell; a tool from the
Audit, Enforce, or Adopt cell; and a doc-type file from a Standard's
prose or from a card's lead paragraph.

No lint checks the target's type: cardgen slices the first link of a
bullet and reads nothing of the file it names
([Cells](/doc-types/standard-card/encoding.md#cells)). The field is
`define: list[Pointer[Standard]]` in
[Card Cells](/doc-types/standard-card/contract-shape.md#the-card).

## Audit cites a lint or an audit

An Audit bullet cites a lint by a `/scripts/` link or an audit by a
judgment link, `/judgments/*.yaml` or a `/standards/semantic-validation/`
document; a third-party detector is its bare name and pin; and a cell
with no checker holds the one bullet `none`.

A lint is a deterministic detector held to the `--list-rules` contract
([Detectors](/standards/standard/detectors.md#a-first-party-detector));
an audit is an LLM judge and carries no script contract. standards-lint's
rule matrix collects only the `/scripts/` links (`standard.rule-matrix`),
so a judgment link and a bare name sit outside it by construction. A card
audits `none` when no automatic check exists, so the gap stays visible.

## No shadowing

A repo-scoped card's stem is one no card dev-playbook publishes carries;
standards-lint reports the collision at the consumer's commit gate
(`standard.card-shadows-upstream`).

A consumer's `standards/<name>.md` on an upstream stem would silently
override the workspace-scoped standard of that name. The two scopes are
[Scope](/doc-types/standard-card/definition.md#scope).

## The catalog

A repo carrying cards has a `standards/index.md` listing every card,
ordered `README.md` first, in dev-playbook the Meta-Standard card next,
then the cards alphabetical by title, then the contract documents no
child index lists alphabetical by title, then the directories;
standards-lint reports the order (`standard.catalog-order`), and okf-lint
the membership and each row's description
([The listing](/standards/knowledge-organization/indexes.md#the-listing)).
