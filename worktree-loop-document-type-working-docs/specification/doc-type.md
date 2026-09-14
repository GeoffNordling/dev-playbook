---
type: General-Sheet
title: Doc-Type Specification
description: The doc-type system's target state as a specification — the predicates any doc-type satisfies, so a loop can propose a new one; the files beside it hold each known doc-type's own
population: "a doc-type: its directory doc-types/<name>/ in dev-playbook, every file of that type in a governed repo, and the toolchain entries that read them"
---

# Doc-Type Specification

The target state as a set of predicates, in the words of
[Glossary](/worktree-loop-document-type-working-docs/glossary.md) and
the form of a Standard: a rule is an H2, its predicate is the first
paragraph, and an H2 with H3s is the condition of each of them. This
file holds what any doc-type satisfies; each file beside it, one per
doc-type, holds what that doc-type alone satisfies, its population the
narrower class. Where
[Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)
draws three doc-types that satisfy these, this defines the set every
doc-type is in, the ones not yet written included. Speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

The member is one doc-type, so a loop that proposes a fourth checks
its candidate against this file alone. Two doc-types may share a verb; the spec says so by having no rule
against it. The objective (complexity, minimized by having the fewest
doc-types, the fewest unique verbs, and fewer shared verbs), is not here. The id and
kind sit on a trailer line after each predicate; their real encoding
is the implementation plan's call.

## Registered

The doc-type has a name, a row in the type registry, and a directory
`doc-types/<name>/` listed by the doc-types index.

`doc-type-system.registered` · deterministic

## A verb set

`definition.md` declares a non-empty set of verbs, each one
word, as the doc-type's operations, and every action the encoding
parses out of an instance is one of them.

`doc-type-system.verbs` · deterministic

## One base

`contract-shape.md` declares one class that extends `DocType`
with operations, a location rule, and frontmatter keys; every other
class in it is nested inside that one, extends nothing, and declares
no operations.

`doc-type-system.one-base` · deterministic

## One module

Every doc-type's `contract-shape.md` pseudocode, concatenated, parse as one
Python module in which `DocType`, `Target`, and `Finding` are defined
once and every name used is defined once.

`doc-type-system.one-module` · deterministic

## A location rule

Every instance lives where the location rule says, and a file's
doc-type is decidable from its path and its frontmatter `type`.

`doc-type-system.location` · deterministic

## A composition rule

`contract-shape.md` states which doc-types and which Targets an instance may
point at, and every pointer in every instance is of a stated kind and
lands on a thing that exists.

`doc-type-system.composition` · deterministic

## Parses

`encoding.md` maps each markdown construct an instance may
use, a heading, a first paragraph, a keyword span, a fenced graph, to
one part of the contract-shape class, and every instance parses under
it into one object of that class.

`doc-type-system.encoding` · deterministic

## Held to a Standard

Every instance is in the population of one Standard, the doc-type's
conventions.

`doc-type-system.held` · deterministic

## One sentence

`definition.md` states in one sentence what one instance is and what
the doc-type does, and the sentence is true of every instance.

`doc-type-system.definition` · stochastic

## Acronyms

None.
