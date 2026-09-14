---
type: General-Sheet
title: Specification
description: The doc-type system's target state as a specification — the predicates any doc-type satisfies, so a loop can propose a new one, with the three known doc-types as conditioned specifics
population: "a doc-type: its bundle under doc-types/<name>/ in dev-playbook, every file of that type in a governed repo, and the toolchain entries that read them"
---

# Specification

The target state as a set of predicates, in the words of
[Glossary](/worktree-loop-document-type-working-docs/glossary.md) and
the form of a Standard: a rule is an H2, its predicate is the first
paragraph, and an H2 with H3s is the condition of each of them. Where
[Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)
draws three doc-types that satisfy these, this defines the set every
doc-type is in, the ones not yet written included. Speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

The member is one doc-type, so a loop that proposes a fourth checks
its candidate against the ungated rules alone. The three known
doc-types are conditions: under each, what is true of that member only.
Two doc-types may share a verb; the spec says so by having no rule
against it. The objective (complexity, minimized by having the fewest
doc-types, the fewest unique verbs, and fewer shared verbs), is not here. The id and
kind sit on a trailer line after each predicate; their real encoding
is the implementation plan's call.

## Registered

The doc-type has a name, a row in the type registry, and a bundle
`doc-types/<name>/` listed by the doc-types index.

`doc-type-system.registered` · deterministic

## A verb set

The bundle's definition declares a non-empty set of verbs, each one
word, as the doc-type's operations, and every action the encoding
parses out of an instance is one of them.

`doc-type-system.verbs` · deterministic

## One base

The bundle's contract shape declares one class that extends `DocType`
with operations, a location rule, and frontmatter keys; every other
class in it is nested inside that one, extends nothing, and declares
no operations.

`doc-type-system.one-base` · deterministic

## One module

The contract shapes of every doc-type, concatenated, parse as one
Python module in which `DocType`, `Target`, and `Finding` are defined
once and every name used is defined once.

`doc-type-system.one-module` · deterministic

## A location rule

Every instance lives where the location rule says, and a file's
doc-type is decidable from its path and its frontmatter `type`.

`doc-type-system.location` · deterministic

## A composition rule

The bundle states which doc-types and which Targets an instance may
point at, and every pointer in every instance is of a stated kind and
lands on a thing that exists.

`doc-type-system.composition` · deterministic

## An encoding with a detector

The bundle states how an instance's prose becomes its parts, and a
detector on the commit boundary rejects an instance the encoding
cannot parse.

`doc-type-system.encoding` · deterministic

## A view

Every instance regenerates byte-identical into a view derived from its
parts, and the view is committed beside the bundle or the instance.

`doc-type-system.view` · deterministic

## Held to a Standard

Every instance is in the population of one Standard, the doc-type's
conventions, and that Standard's rules are the detector's.

`doc-type-system.held` · deterministic

## A residual ledger

The bundle carries a residual ledger, and every recorded residual
names the rule it could not encode.

`doc-type-system.ledger` · deterministic

## One sentence

The definition states in one sentence what one instance is and what
the doc-type does, and the sentence is true of every instance.

`doc-type-system.definition` · stochastic

## Is Runbook

The doc-type is Runbook.

`doc-type-system.runbook` · deterministic

### Six verbs

The operations are read, write, do, override, accept, report.

`doc-type-system.runbook.verbs` · deterministic

### Every edge lands

Every edge carries one of the six and lands on a Target; a ban is a
polarity on a write; accept and report carry no target and sit at the
root.

`doc-type-system.runbook.edges` · deterministic

## Is Standard

The doc-type is Standard.

`doc-type-system.standard` · deterministic

### One verb

The operations are hold.

`doc-type-system.standard.verbs` · deterministic

### Every rule identified

Every rule, a condition included, has an id of the form
`<standard>.<slug>`, unique in the repo, and a kind, deterministic or
stochastic.

`doc-type-system.standard.rule-ids` · deterministic

### Every predicate decidable

Every rule's first paragraph is true or false of one member at one
moment, with no comparison to another member and no taste; what
follows it says why, never how to fix.

`doc-type-system.standard.predicate-litmus` · stochastic

### Population names a class

The population is one phrase naming a class of Target and its
exclusions.

`doc-type-system.standard.population` · stochastic

### Enforcement stays out

No Standard names the boundary, gate, or script that runs it.

`doc-type-system.standard.no-enforce` · deterministic

### Every id one verifier

The verifier table maps every rule id to exactly one script or judge,
names no id that does not exist, and a judge's prompt is its rule's
predicate paragraph.

`doc-type-system.standard.verifiers` · deterministic

### Boundaries name ids

The commit hook, `make check`, CI, and a loop's check each read a list
of rule ids from config, and every id named is in the verifier table.

`doc-type-system.standard.boundaries` · deterministic

### Audit returns findings

`audit(standard, state)` routes each rule id to its verifier, skips a
rule whose condition fails, and returns findings, each one member and one
rule id.

`doc-type-system.standard.audit` · deterministic

## Is Loop

The doc-type is Loop.

`doc-type-system.loop` · deterministic

### Three verbs

The operations are act, check, yield.

`doc-type-system.loop.verbs` · deterministic

### Only points

Every step is an act naming a Runbook that exists, a check naming a
Standard that exists, or a yield naming a Loop that exists or the
user, and a Loop holds no rule and no edge.

`doc-type-system.loop.points` · deterministic

### Unreached

No Runbook edge and no Standard rule lands on a file under `loops/`.

`doc-type-system.loop.unreached` · deterministic

### Zero certifies

A check passes on zero findings and on nothing else; any threshold on
findings is a yield's condition.

`doc-type-system.loop.zero` · deterministic

## Acronyms

- **CI** — Continuous Integration.
