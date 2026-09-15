---
type: General-Sheet
title: Standard Specification
description: What the Standard doc-type satisfies beyond Doc-Type Specification — one verb, every rule identified and decidable, a population naming a class, one verifier per id, boundaries that name ids, and an audit that returns findings
population: "the Standard doc-type: its directory doc-types/standard/ in dev-playbook, every Standard in a governed repo, and the toolchain entries that read them"
---

# Standard Specification

What the Standard doc-type satisfies beyond
[Doc-Type Specification](/worktree-synthesis-notes-working-docs/doc-type-system/specification/doc-type.md),
which every doc-type satisfies. Speculative, per
[Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md).

## One verb

The operations are hold.

`doc-type-system.standard.verbs` · deterministic

## Every rule identified

Every rule, a condition included, has an id of the form
`<standard>.<slug>`, unique in the repo, and a kind, deterministic or
stochastic.

`doc-type-system.standard.rule-ids` · deterministic

## Every predicate decidable

Every rule's first paragraph is true or false of one member at one
moment, with no comparison to another member and no taste; what
follows it says why, never how to fix.

`doc-type-system.standard.predicate-litmus` · stochastic

## Population names a class

The population is one phrase naming a class of
[Target](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md#the-language)
and its exclusions.

`doc-type-system.standard.population` · stochastic

## Every id one verifier

The verifier table maps every rule id to exactly one script or judge,
names no id that does not exist, and a judge's prompt is its rule's
predicate paragraph.

`doc-type-system.standard.verifiers` · deterministic

## Boundaries name ids

The commit hook, `make check`, CI, and a loop's check each read a list
of rule ids from config, and every id named is in the verifier table.

`doc-type-system.standard.boundaries` · deterministic

## Audit returns findings

`audit(standard, state)` routes each rule id to its verifier, skips a
rule whose condition fails, and returns findings, each one member and one
rule id.

`doc-type-system.standard.audit` · deterministic

## Acronyms

- **CI** — Continuous Integration.
