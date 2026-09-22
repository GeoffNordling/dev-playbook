---
type: Standard
title: The Standards Tree
description: A repo's standards/ tree — one directory per Standard, the statement each directory's index opens with, the catalog that lists the directories, and no shadowing of an upstream directory
population: "a repo's standards/ tree: the directories under it and the standards/index.md that lists them"
---

# The Standards Tree

A repo's `standards/` tree: one directory per Standard, and the catalog,
`standards/index.md`, that lists the directories. A Standard is a file
typed `Standard`, one population and its rules, at
`standards/<name>/<topic>.md`; the form of that file is
[Standard Conventions](/standards/doc-type/standard-conventions.md).

> **Why.** One directory, one standard puts the rules of a standard
> and the index that names them in one documentation set
> ([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)),
> so a reader who finds one file finds the rest. The names are
> reserved against a consumer because a consumer's
> `standards/<name>/` on a name dev-playbook publishes would silently
> override the workspace-scoped standard of that name.

## Directory layout

Every immediate subdirectory of `standards/` is a Standard directory: it
holds at least one file typed `Standard`, and every other `.md` file
under it, `index.md` aside, is typed `Standard`; the only flat `.md`
files under `standards/` are `README.md` and `index.md`.

`standard.directory-layout` · deterministic

## The statement

Every Standard directory's `index.md` opens with one sentence,
`<Name> governs <what> — <the things>`: the Standard's name, the
question it governs, and the things its rules cover; the catalog row
repeats that sentence.

`standard.the-statement` · deterministic

## The catalog

A repo carrying a `standards/` tree has a `standards/index.md` listing
`README.md` first and then every directory, in dev-playbook the
meta-standard's `standard/` next, the rest alphabetical by name, each
row carrying its directory index's opening sentence verbatim less the
period; standards-lint reports the order and a row's wording, and
okf-lint the membership
([The listing](/standards/knowledge-organization/indexes.md#the-listing)).

`standard.the-catalog` · deterministic

## No shadowing

A repo-scoped Standard directory's name is one no directory dev-playbook
publishes under `standards/` carries; standards-lint reports the
collision at the consumer's commit gate.

`standard.no-shadowing` · deterministic
