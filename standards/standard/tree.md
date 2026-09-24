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

## Every subdirectory a Standard directory

Every `.md` file under a directory in `standards/`, at any depth
and except a file named `index.md`, has `type: Standard`, and each
directory directly in `standards/` has at least one such file. The
only `.md` files directly in `standards/` are `README.md` and
`index.md`.

`standard.every-subdirectory-a-standard-directory` · deterministic

## Directory index opens with the governing sentence

The first sentence after the H1 of each `standards/<name>/index.md`
has the form `<Name> governs <what> — <the things>`: the
Standard's name, the word `governs`, the question it governs, an
em dash, and the things its rules cover.

`standard.directory-index-opens-with-the-governing-sentence` · deterministic

## The catalog lists every directory

`standards/index.md` lists `README.md` first, then the `index.md`
of every directory directly in `standards/`, and nothing else. The
directories are in alphabetical order by name, except that in
dev-playbook `standard/` comes first. Each directory's entry has,
after its link, the first sentence of that directory's `index.md`
without its final period.

`standard.the-catalog-lists-every-directory` · deterministic

## No shadowing

In a repo other than dev-playbook, no directory directly in
`standards/` has the name of a directory directly in `standards/`
of the dev-playbook version the repo pins.

`standard.no-shadowing` · deterministic
