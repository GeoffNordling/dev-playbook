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

> **Why.** The verifier table reads a rule by its trailer
> ([The verifier table](/standards/standard/detectors.md#the-verifier-table)),
> so a rule without one is a rule no row of that table can name. A
> verifier, and a reader, must know the class before the first rule,
> which is what the one frontmatter phrase gives them. And no
> verifier, script or judge, returns one value for a predicate that
> compares two members or asks for taste.

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
`<slug>` the heading's GitHub slug; after the trailer, before the next
heading, is at most one block opening `> **Why.**`. A level-three
heading sits only under a level-two heading that carries no trailer,
which scopes it.

`doc-type.the-rule-shape` · deterministic


## Decidable predicates

Each rule's predicate is true or false of one member of the population
at one moment, with no comparison to another member and no taste.

`doc-type.decidable-predicates` · stochastic
