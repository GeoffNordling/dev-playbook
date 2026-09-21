---
type: Standard
title: The Standards Tree
description: A repo's standards/ tree — one directory per Standard, the population every Standard names, the shape of a rule, the catalog that lists the directories, and no shadowing of an upstream directory
population: "a repo's standards/ tree: the directories under it and the standards/index.md that lists them"
---

# The Standards Tree

A repo's `standards/` tree: one directory per Standard, and the catalog,
`standards/index.md`, that lists the directories. A Standard is a file
typed `Standard`, one population and its rules, at
`standards/<name>/<topic>.md`. The reasoning behind these rules is
[Standard Explanation](/standards/standard/explanation.md#the-tree).

## Directory layout

Every immediate subdirectory of `standards/` is a Standard directory: it
holds at least one file typed `Standard`, and every other `.md` file
under it, `index.md` aside, is typed `Standard` or `Explanation`; the
only flat files under `standards/` are `README.md` and `index.md`;
standards-lint reports a departure.

`standard.directory-layout` · deterministic

## The population

A file typed `Standard` names the population its rules bind in its
frontmatter: a `population` key holding one phrase; standards-lint
reports a Standard without one.

`standard.the-population` · deterministic

## The rule shape

Each rule of a Standard is a level-two heading, a first paragraph that
is the predicate every member of the population is held to, at most one
block or table stating the target state the predicate compares against,
and last a trailer line, `` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``, where `<name>` is the directory and
`<slug>` the heading's GitHub slug; nothing follows the trailer before
the next heading. A level-three heading sits only under a level-two
heading that is a condition, and is then a rule bound under that
condition.

`standard.the-rule-shape` · deterministic

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
