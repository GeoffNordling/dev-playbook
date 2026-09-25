---
type: Standard
title: Standard Conventions
description: The form a file typed Standard takes — one population in its frontmatter, each rule a heading, a predicate, and a trailer, the why blocks that argue them, and every predicate decidable of one member
population: "a file typed Standard"
---

# Standard Conventions

A file typed `Standard`, under `standards/` or, as a
[draft Standard](/CONTEXT.md#governance), in a workstream
([OKF Frontmatter](/standards/knowledge-organization/okf-frontmatter.md#standard-lives-under-standards)):
one population and its rules. The
[Standard doc-type](/doc-types/standard/index.md) declares what a
Standard is and the encoding its file takes,
[Population and Rules Encoding](/doc-types/standard/encoding.md); a
doc-type binds nobody, so this Standard is what binds the file to that
encoding. The tree the file sits in is
[The Standards Tree](/standards/standard/tree.md).

> **Why.** A check claims a rule by its trailer's id
> ([Checks](/standards/standard/checks.md)),
> so a rule without one is a rule no check can name. A
> verifier, and a reader, must know the class before the first rule,
> which is what the one frontmatter phrase gives them. And no
> verifier, check or judge, returns one value for a predicate that
> compares two members or asks for taste.

## The frontmatter names the population

A file typed `Standard` has a `population` key in its frontmatter,
and its value is a string that is not empty.

`doc-type.the-frontmatter-names-the-population` · deterministic

> **Why.** A check reports a Standard without a population. What
> a check reports is not part of the predicate, so the clause lives
> here.


## A rule: heading, predicate, trailer

In a file typed `Standard`, a rule is an H2 or H3 whose section
ends with a trailer line,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``. `<name>` is the first
directory under `standards/` in the file's path, or, for a draft
Standard, the name of its workstream's directory, and `<slug>` is
the GitHub slug of the heading. Between the heading and the
trailer there is one paragraph, then any number of paragraphs,
fenced blocks, blockquotes, lists, or tables. After the trailer,
before the next heading, there is nothing, or one blockquote that
starts `> **Why.**`. An H3 is only under an H2 that has no trailer.

`doc-type.a-rule-heading-predicate-trailer` · deterministic

> **Why.** The first paragraph is the predicate every member is held
> to; the block or table is the target state it compares against. An H2
> without a trailer is a condition: it names which members the rules
> under it bind. It is one shape whether it has one child or eleven,
> and its definition is never repeated in the children.


## The file's why ends the opening prose

In a file typed `Standard`, the text between the H1 and the first
H2 has at most one blockquote that starts `> **Why.**`. If it has
one, that blockquote is the last block before the first H2.

`doc-type.the-files-why-ends-the-opening-prose` · deterministic


## Every predicate decidable of one member

Each rule's predicate is true or false of one member of the population
at one moment, with no comparison to another member and no taste.

`doc-type.every-predicate-decidable-of-one-member` · stochastic

## A why states no predicate

No sentence of a why block, a rule's or the file's own, holds a member
of the population to a state; the block argues for the rule or the file
it sits with.

`doc-type.a-why-states-no-predicate` · stochastic
