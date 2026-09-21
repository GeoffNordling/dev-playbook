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
doc-type, the three built and any built later; a rule over the
instances of one doc-type is that doc-type's own Standard's. The
reasoning behind these rules is
[Doc-Type Explanation](/standards/doc-type/explanation.md).

## Registered

The doc-type is the ruling of at least one row of the registry rulings
table in [Doc-Type System](/doc-types/doc-type-system.md#registry-rulings),
and its directory is a row of [doc-types/index.md](/doc-types/index.md).

`doc-type.registered` · deterministic

## A verb set

`definition.md` states the doc-type's verbs, a non-empty set of single
words, and the `operations` of the class in `contract-shape.md` is the
same set.

`doc-type.a-verb-set` · stochastic

## One base

`contract-shape.md` holds one class that extends `DocType`, declaring
`operations` and `frontmatter`; every other class in its block is
nested inside that one, extends nothing, and declares no operations.

`doc-type.one-base` · stochastic

## A composition rule

`contract-shape.md` states what an instance may point at, which
doc-types and which Targets, and how many of each.

`doc-type.a-composition-rule` · stochastic

## An encoding

`encoding.md` maps each markdown construct an instance uses to one part
of the class in `contract-shape.md`.

`doc-type.an-encoding` · stochastic

## Held to a Standard

A Standard exists whose population is the instances of the doc-type, so
that every file of the type is a member of it.

`doc-type.held-to-a-standard` · stochastic

## One sentence

`definition.md` opens with one sentence that says what one instance is
and what the doc-type does.

`doc-type.one-sentence` · stochastic
