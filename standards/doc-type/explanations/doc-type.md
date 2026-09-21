---
type: Explanation
title: Doc-Type Explanation
description: The Reasons for the Doc-Type Standard — why its member is the directory, why its rules are general, why six are read by a judge, and the decision behind each of the seven
---

# Doc-Type Explanation

## The member is the directory

The population is `doc-types/<name>/`, not the files of that type. A
rule over instances, that every runbook edge lands or that every Loop
has a Mermaid graph, is already some Standard's: Runbook Conventions
binds a runbook, Loop Conventions a document typed Loop, the
Meta-Standard a `standards/` tree. A second Standard over the same files
would return a second finding for one fault, naming the doc-type where
the fault is one file. So this Standard asks one thing of the instances,
that one Standard covers them, and leaves the rest to it.

explains `doc-type.held-to-a-standard`

## General by construction

The rules describe the set every doc-type is in, the ones not yet
written included, so a loop that proposes a new doc-type checks its
candidate against this file alone. A predicate true of the built
doc-types but not of a doc-type in general is not here: the verb sets
are stated in each doc-type's `definition.md` and not repeated as rules,
and no rule names a location, since the pseudocode carries none.

explains `doc-type.registered`, `doc-type.a-verb-set`, `doc-type.one-base`, `doc-type.a-composition-rule`, `doc-type.an-encoding`, `doc-type.held-to-a-standard`, `doc-type.one-sentence`

## Pseudocode is read, not parsed

Six of the seven rules read the pseudocode in `contract-shape.md` or
prose in `definition.md`; the fenced blocks are pseudocode, not Python,
and are never parsed as Python, so each such rule is stochastic, a
judge's prompt. Registered is deterministic because the rulings table
and the index are both tables a script reads.

explains `doc-type.registered`, `doc-type.a-verb-set`, `doc-type.one-base`, `doc-type.a-composition-rule`, `doc-type.an-encoding`, `doc-type.held-to-a-standard`, `doc-type.one-sentence`

## Registered

A doc-type nobody can find from the registry rulings or the doc-types
index is not in the system. The rulings table, not the type registry, is
the anchor, because a runbook carries no frontmatter `type`: `Skill` and
`Agent definition` are rulings onto Runbook.

explains `doc-type.registered`

## A verb set

The verbs are the doc-type's API. Two doc-types may share a verb; the
Standard says so by having no rule against it.

explains `doc-type.a-verb-set`

## One base

One class per doc-type keeps the blocks a module a reader holds in mind;
a part is a class nested in its DocType, so that a Rule or an Edge is
never mistaken for a doc-type.

explains `doc-type.one-base`

## A composition rule

What an instance may point at is what a reader, and a later extractor,
checks a pointer against.

explains `doc-type.a-composition-rule`

## An encoding

Without a map from markdown to the class, an instance is prose and the
contract shape is decoration.

explains `doc-type.an-encoding`

## Held to a Standard

The shape never binds; a Standard does. A doc-type whose instances no
Standard covers has a contract nobody is held to.

explains `doc-type.held-to-a-standard`

## One sentence

The sentence is the test a reader applies to a file before the encoding
is consulted: is this one of these.

explains `doc-type.one-sentence`
