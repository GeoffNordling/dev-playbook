---
type: Standard-Ruleset
title: Indexes
description: The index.md file — typeless, an introduction naming what the directory holds, a listing of every concept document with its description, alphabetical unless declared otherwise, authored not generated
population: "an index.md"
---

# Indexes

The `index.md` of a directory, the navigational listing that lets an
agent see what the directory holds, and read each document's one-line
`description`, without opening every file. A repo's agent-navigated
documentation is one
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog)
bundle per the [OKF SPEC](/standards/references/okf-spec.md), the whole
repository: an agent triages a document by its frontmatter and navigates
between documents by the per-directory `index.md`, loading a body only
when the document is relevant. okf-lint is the authority
([Knowledge Organization](/standards/knowledge-organization/card.md)).

## Typeless

An `index.md` carries no OKF `type`; it is a listing, not a concept
document.

## The introduction

The prose between the H1 and the first listed entry is present and opens
with a single sentence naming what the directory holds, in that
directory's own vocabulary.

Restating the path is not an introduction: "the files in `standards/`"
tells a reader nothing the H1 did not. The live indexes name the thing:
*the catalog*; *the documentation type system*; *Build governs how a
repository is laid out, built, and checked*, the form a card directory
fixes
([The directory's introduction](/standards/standard/cards.md#the-directorys-introduction)).
Where the sole
entry's `description` already says what the directory holds, the
sentence says what it is for instead. After that sentence comes only
what a reader needs before the listing makes sense: a start-here
pointer, where the governing concept is defined, or a structural fact
the listing hides, such as half the directory's material living
elsewhere. The `Ordering:` marker goes last, on its own line
([Ordering](#ordering)). okf-lint checks only that the introduction is
present (`knowledge-organization.index-intro`); what it says is a
reviewer's judgment.

## The listing

An `index.md` lists, for its own directory, the directory's `README.md`
when present, then each concept document as a markdown link carrying
the document's frontmatter `description` verbatim, then each child
directory's own `index.md`.

A subdirectory holding concept documents carries an `index.md` of its
own and is listed as a child, never recursed into
([An index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)).

## Ordering

Within each group of an index, the concept documents after `README.md`
and the child-directory links, entries are alphabetical by link title,
case-insensitive, with `README.md` first; an index deviates only when an
intro line beginning `Ordering:` declares the meaningful order.

`Ordering: in Decision Record number order` and
`Ordering: by level of abstraction` are declarations. The marker is
structured: the detector checks only that an intro line, one before the
first listed entry, begins `Ordering:`. An undeclared deviation from
alphabetical is a defect: a reader cannot tell unstated meaning from
randomness.

## Authored, not generated

An `index.md` is authored; no committed generator produces it.

## The root index

The `index.md` at the repository root.

### OKF version declared

The root index declares the bundle's OKF version in frontmatter, per the
[OKF SPEC](/standards/references/okf-spec.md) Versioning section:

```yaml
---
okf_version: "0.1"
---
```

`okf_version` is dev-playbook's whole root frontmatter. A consumer repo
carries one key more, the `okf_types` mapping declaring the document
types it holds that no other repo shares
([Local declaration](/standards/knowledge-organization/type-registry.md#local-declaration)).
