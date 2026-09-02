---
type: General-Sheet
title: Standard Residual Ledger
description: Standard's residual record — what one population and its rules cannot express, one entry per Standard that has one
---

# Standard Residual Ledger

Standard's residual record: what
[one population and its rules](/doc-types/standard/contract-shape.md)
cannot express. That is all an entry is — a record.

## Standards

Per Standard ported to the encoding: what the rewrite could not
express, recognized and written down at the moment of porting. Entries
name populations, rules, and conditions in the vocabulary
[encoding.md](/doc-types/standard/encoding.md) declares.

An entry is a couple of sentences, hard limit: name each specific thing
the file could not express and why the shape cannot say it, nothing
else. A Standard with nothing to record has no entry.

### build/skeleton

Could not express `tests/` as a rule under the union of two layers,
Python package or Python scripts, since a rule binds under one
condition; it sits under its own condition, Python source, whose test
restates the union. Could not name the base layer: a rule under no
condition shows `—`, and the view carries no name for the set every
rule binds.

### build/canonical

Could not express the compare strength, byte-identical, blocks
verbatim, or values parsed, as data on the member; it lives only in
each rule's predicate. Could not express the `pyproject.toml` fork on
`src/` as two conditioned rules without splitting one artifact's compare
in two; the fork is two clauses of one predicate.

### build/python

Could not express the shebang rule's antecedent, an executable file, as
a condition, since the condition Scripts already tests presence under
`scripts/` and a rule takes one condition; the antecedent sits inside
the predicate.

### standard/gates

Could not express a population of three fixed members: the phrase names
the class, and the three are named only in the Three rungs predicate.
Could not express the red-CI rule over a gate's state: its object is a
pull request, so it binds a member outside the population.

### distribution/channel

Could not express one class of object: the population spans four kinds
of state, a manifest, a local block, a pin, and the roster, joined only
by the repo that holds them. Could not express the roster rule over an
object in a tree: its member is one line of workspace-lint's source.
