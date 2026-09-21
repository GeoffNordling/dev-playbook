---
type: Standard
title: Standard Conventions
description: The form a file typed Standard takes — one population in its frontmatter, each rule a heading, a predicate, and a trailer, and every predicate decidable of one member
population: "a file typed Standard"
---

# Standard Conventions

A file typed `Standard`, under `standards/`
([Document Types](/standards/knowledge-organization/document-types.md#typed-standard)):
one population and its rules. The
[Standard doc-type](/doc-types/standard/index.md) declares what a
Standard is and the encoding its file takes,
[Population and Rules Encoding](/doc-types/standard/encoding.md); a
doc-type binds nobody, so this Standard is what binds the file to that
encoding. The tree the file sits in is
[The Standards Tree](/standards/standard/tree.md).

The reasoning behind the rules is
[Doc-Type Explanation](/standards/doc-type/explanation.md#a-standards-file).

## The population

A file typed `Standard` names the population its rules bind in its
frontmatter: a `population` key holding one phrase; standards-lint
reports a Standard without one.

`doc-type.the-population` · deterministic


## The rule shape

Each rule of a Standard is a heading, a first paragraph, at most one
block or table stating the target state, and last a trailer line,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``, where `<name>` is the directory and
`<slug>` the heading's GitHub slug; nothing follows the trailer before
the next heading. A level-three heading sits only under a level-two
heading that carries no trailer, which scopes it.

`doc-type.the-rule-shape` · deterministic


## Decidable predicates

Each rule's predicate is true or false of one member of the population
at one moment, with no comparison to another member and no taste.

`doc-type.decidable-predicates` · stochastic
