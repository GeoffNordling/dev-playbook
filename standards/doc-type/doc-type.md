---
type: Standard
title: Doc-Type
description: What any doc-type satisfies — a ruling and an index row, a verb set, one base class, a composition rule, an encoding, a Standard over its instances, and a one-sentence definition
population: "a doc-type: an immediate subdirectory of doc-types/"
---

# Doc-Type

A doc-type is a directory `doc-types/<name>/`: the definition, contract
shape, and encoding of one kind of markdown file, the theory of which
is [Doc-Type](/doc-types/doc-type.md). These rules hold of every
doc-type, the built and any built later; a rule over the
instances of one doc-type is that doc-type's own Standard's.

> **Why.** The rules describe the set every doc-type is in, the ones
> not yet written included, so a loop that proposes a new doc-type
> checks its candidate against this file alone. A predicate true of
> the built doc-types but not of a doc-type in general is not here:
> the verb sets are stated in each doc-type's `definition.md` and not
> repeated as rules, and no rule names a location, since the
> pseudocode carries none. The population is `doc-types/<name>/`, not
> the files of that type: a rule over instances is already some
> Standard's, so this Standard asks one thing of the instances, that
> one Standard covers them, and leaves the rest to it. A rule that
> reads the pseudocode in `contract-shape.md` or the prose in
> `definition.md`, never parsed as Python, is stochastic, a judge's
> prompt; a rule that reads a table or a class header a script parses,
> as Registered and One base do, is deterministic.

## Registered

The doc-type is the ruling of at least one row of the registry rulings
table in [Doc-Type System](/doc-types/doc-type-system.md#registry-rulings),
and its directory is a row of [doc-types/index.md](/doc-types/index.md).

`doc-type.registered` · deterministic

> **Why.** A doc-type nobody can find from the registry rulings or the
> doc-types index is not in the system. The rulings table, not the
> type registry, is the anchor, because a runbook carries no
> frontmatter `type`: `Skill` and `Agent definition` are rulings onto
> Runbook.

## A verb set

`definition.md` states the doc-type's verbs, a non-empty set of single
words, and the `operations` of the class in `contract-shape.md` is the
same set.

`doc-type.a-verb-set` · stochastic

> **Why.** The verbs are the doc-type's API. Two doc-types may share a
> verb; the Standard says so by having no rule against it.

## One base

`contract-shape.md` holds one class that extends `DocType`, declaring
`operations` and `frontmatter`; every other class in its block is
nested inside that one, extends nothing, and declares no operations.

`doc-type.one-base` · deterministic

> **Why.** One class per doc-type keeps the blocks a module a reader
> holds in mind; a part is a class nested in its DocType, so that a
> Rule or an Edge is never mistaken for a doc-type.

## A composition rule

`contract-shape.md` states what an instance may point at, which
doc-types and which Targets, and how many of each.

`doc-type.a-composition-rule` · stochastic

> **Why.** What an instance may point at is what a reader, and a later
> extractor, checks a pointer against.

## An encoding

`encoding.md` maps each markdown construct an instance uses to one part
of the class in `contract-shape.md`.

`doc-type.an-encoding` · stochastic

> **Why.** Without a map from markdown to the class, an instance is
> prose and the contract shape is decoration.

## Held to a Standard

A Standard exists whose population is the instances of the doc-type, so
that every file of the type is a member of it.

`doc-type.held-to-a-standard` · stochastic

> **Why.** The shape never binds; a Standard does. A doc-type whose
> instances no Standard covers has a contract nobody is held to.

## One sentence

`definition.md` opens with one sentence that says what one instance is.

`doc-type.one-sentence` · stochastic

> **Why.** The sentence is the test a reader applies to a file before
> the encoding is consulted: is this one of these.
