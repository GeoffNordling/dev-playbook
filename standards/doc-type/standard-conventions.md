---
type: Standard
title: Standard Conventions
description: The form a file typed Standard takes — one population in its frontmatter, each rule a heading, a predicate, and a trailer, the why blocks that argue them, and every predicate decidable of one member
population: "a file typed Standard"
---

# Standard Conventions

A file typed `Standard`, under `standards/`
([Document Types](/standards/knowledge-organization/document-types.md#standard-lives-under-standards)):
one population and its rules. The
[Standard doc-type](/doc-types/standard/index.md) declares what a
Standard is and the encoding its file takes,
[Population and Rules Encoding](/doc-types/standard/encoding.md); a
doc-type binds nobody, so this Standard is what binds the file to that
encoding. The tree the file sits in is
[The Standards Tree](/standards/standard/tree.md).

> **Why.** A detector claims a rule by its trailer's id
> ([Detectors](/standards/standard/detectors.md)),
> so a rule without one is a rule no detector can name. A
> verifier, and a reader, must know the class before the first rule,
> which is what the one frontmatter phrase gives them. And no
> verifier, script or judge, returns one value for a predicate that
> compares two members or asks for taste.

## The frontmatter names the population

A file typed `Standard` names the population its rules bind in its
frontmatter: a `population` key holding one phrase.

`doc-type.the-frontmatter-names-the-population` · deterministic

> **Why.** standards-lint reports a Standard without a population. What
> a detector reports is not part of the predicate, so the clause lives
> here.


## A rule: heading, predicate, trailer

Each rule of a Standard is a heading, a first paragraph, at most one
block or table stating the target state, and last a trailer line,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``, where `<name>` is the directory and
`<slug>` the heading's GitHub slug; after the trailer, before the next
heading, is at most one block opening `> **Why.**`. A level-three
heading sits only under a level-two heading that carries no trailer,
which scopes it.

`doc-type.a-rule-heading-predicate-trailer` · deterministic

> **Why.** The first paragraph is the predicate every member is held
> to; the block or table is the target state it compares against. An H2
> without a trailer is a condition: it names which members the rules
> under it bind. It is one shape whether it has one child or eleven,
> and its definition is never repeated in the children.


## The file's why ends the opening prose

The prose between a Standard's level-one heading and its first
level-two heading ends with at most one block opening `> **Why.**`:
the argument for the file as a whole, not for any one of its rules.

`doc-type.the-files-why-ends-the-opening-prose` · deterministic


## Every predicate decidable of one member

Each rule's predicate is true or false of one member of the population
at one moment, with no comparison to another member and no taste.

`doc-type.every-predicate-decidable-of-one-member` · stochastic

> **Why.** A predicate is decided from the bytes of the repo at one
> commit, by reading them or by a pure function of them such as a
> formatter. It is not a test over run-time behaviour, what a script
> exits or prints; not an instruction to an author; not a fact held
> outside the files, the day a decision was made, the latest upstream
> release, a GitHub setting, git history, another repo; and not a
> definition that scopes other rules. Behaviour and instruction go to a
> Guide, the why to the why block, a scoping definition to an H2 with
> no trailer. Kind is judged from the sentence, not the trailer: a
> sentence a script decides from the files with no judgment call is
> deterministic, a sentence with a judgment word is stochastic, and
> where a sentence mixes the two the mechanical part stays
> deterministic and the judgment moves to the why block.


## A why states no predicate

No sentence of a why block, a rule's or the file's own, holds a member
of the population to a state; the block argues for the rule or the file
it sits with.

`doc-type.a-why-states-no-predicate` · stochastic
