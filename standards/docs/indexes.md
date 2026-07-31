---
type: Standard
title: Indexes
description: The index.md file — its required introduction, per-directory listing rules, child-index delegation, authored not generated
---

# Indexes

An `index.md` is a navigational listing that lets an agent see what a
directory contains — and read each document's one-line `description` —
without opening every file. `index.md` is **typeless**: it carries no OKF
`type` and is not itself a concept document.

## Content

An `index.md` opens with an **introduction**, then **lists** what its
directory holds.

### The introduction

The introduction is the prose between the H1 and the first listed entry. It
is **required**, and it opens with a single sentence: a noun phrase naming
what the directory holds, in that directory's own vocabulary.

Restating the path is not an introduction — "the files in `standards/`"
tells a reader nothing the H1 did not. Name the thing, as the live indexes
do: *the catalog*; *the layered repo standard, one concern per document*;
*purpose-built artifact formats and their tooling*. Where the sole entry's
`description` already says what the directory holds, say what it is **for**
instead.

After that sentence, add only what a reader needs before the listing makes
sense: a start-here pointer, where the governing concept is defined, or a
structural fact the listing hides — such as half the directory's material
living elsewhere. The `Ordering:` marker goes last, on its own line
([Ordering](#ordering)).

No deterministic detector checks this.

### The listing

An `index.md` lists, for its own directory:

- the directory's `README.md` (if present), then
- each concept document, as a markdown link carrying the document's
  frontmatter `description`.

For child directories, it links the child's own `index.md` rather than
reaching into it. A subdirectory is recursed into inline **only when it has
no `index.md` of its own** — otherwise the listing delegates to that child
index.

The repository root `index.md` additionally declares the bundle's OKF
version in frontmatter (its only frontmatter key), per the
[OKF SPEC](/standards/references/okf-spec.md) Versioning section:

```yaml
---
okf_version: "0.1"
---
```

## Ordering

Within each group of an index — the concept documents after `README.md`,
and the child-directory links — entries are **alphabetical by link title**,
case-insensitive. `README.md` always comes first.

An index may deviate from alphabetical **only when an intro line beginning
`Ordering:` declares the meaningful order** — for example
`Ordering: in Decision Record number order` or `Ordering: by level of abstraction`. The
marker is structured, not prose: the detector checks only that an intro line
(one before the first listed entry) begins `Ordering:`, and never parses what
the declaration says. An undeclared deviation from alphabetical is a defect —
a reader cannot distinguish unstated meaning from entropy.

## Authored, not generated

`index.md` files are **authored**, not produced by a committed generator. A
staleness checker (a pre-commit hook, alongside `ref-lint` and the
type-lint) fails the commit when an index omits a concept document in its
directory, lists one that no longer exists, or gives a description that no
longer matches the child's frontmatter. The check keeps hand-authored
indexes honest without a generator owning the file.
