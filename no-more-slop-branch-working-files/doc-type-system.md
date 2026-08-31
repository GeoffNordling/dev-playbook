---
type: General-Sheet
title: Doc-Type System
description: This repo's doc-type instantiation — the registry rulings, the roster of built doc-types, and the import surface for consumer repos
---

# Doc-Type System

This repo's instantiation of
[Doc-Type](/no-more-slop-branch-working-files/doc-type.md): which
document kinds matter here, which doc-types are built, and what a
consumer repo imports.

## Registry rulings

The registry pass runs over the repo's two registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/harness/files.md) for harness
files. A registry kind is finer than a family: the registries name
every kind that may exist; a doc-type is built only for a family
ruled important.

| Kind | Family | Ruling |
|---|---|---|
| Skill | runbooks | The [Runbook](/no-more-slop-branch-working-files/runbook-contract-shape.md) doc-type |
| Agent definition | runbooks | The [Runbook](/no-more-slop-branch-working-files/runbook-contract-shape.md) doc-type |
| Standard | cards | The [Standard](/standards/standard.md) doc-type |
| Standard-Card | cards | The [Standard](/standards/standard.md) doc-type — its catalog surface |
| Guide | guides | Important; no doc-type built yet |
| Vocabulary | — | Separate — the vocabulary API ([System Legibility](/no-more-slop-branch-working-files/system-legibility.md)), not a doc-type |

Any registry kind absent from this table is ruled not important.

## The roster

Two doc-types are built, one sparse and one deep.

**Standard** — a standard states a rule the workspace holds itself
to, named by the question it governs
([definition](/standards/standard/format.md)). It carries type-level
grain: one contract serves every card. Its shape — the card — is
declared in [format.md](/standards/standard/format.md). Its fixed
composition rule keeps the machinery sparse: headings suffice, and
its determinism lives in the audit linters and enforcement gates its
cards point at.

```
Standard
  operations:   define audit enforce adopt
  composition:  one of each
    │
    └──► shape: the struct
           │
           ├─ the harness card — its four sections filled
           ├─ the build card — its four sections filled
           └─ … one per card in the catalog
```

**Runbook** — a runbook is an invocable command: a skill or an
agent definition
([definition](/no-more-slop-branch-working-files/runbook-definition.md)).
It carries instance-level grain: every runbook owns a distinct
chain. Its shape is declared in
[runbook-contract-shape.md](/no-more-slop-branch-working-files/runbook-contract-shape.md),
its encoding layer in
[runbook-encoding.md](/no-more-slop-branch-working-files/runbook-encoding.md),
its residuals in
[runbook-residual-ledger.md](/no-more-slop-branch-working-files/runbook-residual-ledger.md).
Its free composition rule demands deep machinery: a grammar, a
parser, a drift check.

```
Runbook
  operations:   read write do … — the full set in
                [runbook-contract-shape.md]
  composition:  any number, coarsely ordered
    │
    └──► shape: the chain — the Reference chain
           │
           ├─ /intake's chain    one contract
           ├─ /commit's chain    another
           └─ … one per runbook
```

A card is to Standard what `/intake` is to Runbook: one instance, one
filled shape, one contract. The detail files under a card sit below
its contract the way a runbook's prose body sits below its chain.

Instances never live in the doc-type tree — they stay with their
populations, and a contract rides inside its instance file.

## Shape and obligation

A doc-type declares what a contract shape *is*; it never binds
anyone to use it. The binding rule — every instance in the family
must carry its contract — is a Standard card's job: Runbook's
obligation rides
[runbook-conventions](/standards/harness/runbook-conventions.md),
audited by the chain drift check. The shape is never itself a
Standard, so Standard and Runbook remain peers in this roster.

## The import surface

A consumer repo writes its own doc-type-system file: an import
declaration — Runbook and Standard, from dev-playbook — plus its
local rulings, and a doc-type of its own only when it declares one.
It never copies the kind definition or a shape. This is the
workspace's general pattern: dev-playbook declares a system once,
every consumer repo inherits it, and a repo declares only what is
local to it.
