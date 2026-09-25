---
type: Standard
title: Doc-Type
description: What any doc-type satisfies — a ruling, a verb set, a composition rule, an encoding, a Standard over its instances, and a one-sentence definition
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
> prompt; a rule that reads a table a script parses, as Registered
> does, is deterministic.

## Registered

The table under `## Registry rulings` in
`doc-types/doc-type-system.md` has a row whose Ruling cell links to
a file in `doc-types/<name>/`.

`doc-type.registered` · deterministic

> **Why.** A doc-type nobody can find from the registry rulings or the
> doc-types index is not in the system. The rulings table, not the
> type registry, is the anchor, because a runbook carries no
> frontmatter `type`: `Skill` and `Agent definition` are rulings onto
> Runbook.

## Verbs are the operations

`definition.md` states the doc-type's verbs, a set of single words,
possibly empty, and the `operations` of the class in
`contract-shape.md` is the same set.

`doc-type.verbs-are-the-operations` · stochastic

> **Why.** The verbs are the doc-type's API. Two doc-types may share a
> verb; the Standard says so by having no rule against it.

## What an instance may point at

`contract-shape.md` states what an instance may point at, which
doc-types and which Targets, and how many of each.

`doc-type.what-an-instance-may-point-at` · stochastic

> **Why.** What an instance may point at is what a reader, and a later
> extractor, checks a pointer against.

## Each construct maps to one class part

`encoding.md` maps each markdown construct an instance uses to one part
of the class in `contract-shape.md`.

`doc-type.each-construct-maps-to-one-class-part` · stochastic

> **Why.** Without a map from markdown to the class, an instance is
> prose and the contract shape is decoration.

## Held to a Standard

A Standard exists whose population is the instances of the doc-type, so
that every file of the type is a member of it.

`doc-type.held-to-a-standard` · stochastic

> **Why.** The shape never binds; a Standard does. A doc-type whose
> instances no Standard covers has a contract nobody is held to.

## One sentence says what an instance is

`definition.md` opens with one sentence that says what one instance is.

`doc-type.one-sentence-says-what-an-instance-is` · stochastic

> **Why.** The sentence is the test a reader applies to a file before
> the encoding is consulted: is this one of these.
