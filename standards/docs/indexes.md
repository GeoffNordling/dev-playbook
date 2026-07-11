---
type: Standard
title: Indexes
description: The index.md listing — per-directory content rules, child-index delegation, authored not generated
---

# Indexes

An `index.md` is a navigational listing that lets an agent see what a
directory contains — and read each document's one-line `description` —
without opening every file. `index.md` is **typeless**: it carries no OKF
`type` and is not itself a concept document.

## Content

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
and the child-directory links — the default order is **alphabetical by
link title**, case-insensitive. `README.md` always comes first.

An index may use a different, meaningful order **only when its intro prose
declares what that order is** — for example "listed in reading order",
"in ADR number order", or "ordered by level of abstraction". An undeclared
deviation from alphabetical is a defect: a reader cannot distinguish
unstated meaning from entropy.

## Authored, not generated

`index.md` files are **authored**, not produced by a committed generator. A
staleness checker (a pre-commit hook, alongside `ref-audit` and the
type-lint) fails the commit when an index omits a concept document in its
directory, lists one that no longer exists, or gives a description that no
longer matches the child's frontmatter. The check keeps hand-authored
indexes honest without a generator owning the file.
