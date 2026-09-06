---
type: General-Sheet
title: Doc-Type System
description: This repo's doc-type instantiation — the registry rulings, the roster of built doc-types, and the import surface for consumer repos
---

# Doc-Type System

This repo's instantiation of
[Doc-Type](/doc-types/doc-type.md): which
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

Every kind in both registries has a row, and no kind is excluded: a
type with few files and little at stake is carried as a thin doc-type,
never as an exclusion, since an exclusion is a second kind of row a
reader must learn. A row reading *pending* is not yet ruled; the pass
rules on Decision-Record first, where the shape is obvious, and on the
rows with one or two files last.

| Kind | Family | Ruling |
|---|---|---|
| Candidate-List | candidate lists | Pending |
| Decision-Record | decision records | Pending — the first run of the doc-type build loop ([#474](https://github.com/GeoffNordling/dev-playbook/issues/474)) |
| General-Sheet | — | Pending; its replacement is an open question ([Candidates](/CANDIDATES.md)) |
| Guide | guides | Important; no doc-type built yet |
| Instrument-Spec | instruments | Pending; the instruments are to be remade first ([Candidates](/CANDIDATES.md)) |
| Log | logs | Pending; the user's to rule |
| README | readmes | Pending |
| Recipe-Description | recipes | Pending |
| Reference | references | Pending |
| Standard | standards | The [Standard](/doc-types/standard/definition.md) doc-type |
| Standard-Card | cards | The [Standard-Card](/doc-types/standard-card/definition.md) doc-type |
| Survey | surveys | Pending; the user's to rule |
| Vocabulary | — | Separate — the vocabulary API ([System Legibility](/docs/system-legibility.md)), not a doc-type |
| Skill | runbooks | The [Runbook](/doc-types/runbook/contract-shape.md) doc-type |
| Agent definition | runbooks | The [Runbook](/doc-types/runbook/contract-shape.md) doc-type |
| `CLAUDE.md` | context files | Pending |
| `rules/*.md` | context files | Pending |
| `settings.json`, `settings.local.json` | configuration | Pending |
| `hooks/` | hooks | Pending |
| `.claude/workflows/*.js` | workflows | Pending |

## The roster

Three doc-types: Standard-Card sparse, Runbook and Standard deep.

**Standard-Card** — a card is the catalog record for one standard,
named by the question the standard governs
([definition](/doc-types/standard-card/definition.md)). It carries
type-level grain: one contract serves every card. Its shape is the
four cells, and `scripts/cardgen` collapses every card to rows of
`card, cell, pointer`.
Its fixed composition rule keeps the machinery sparse: headings suffice,
and its determinism lives in the audit linters and enforcement gates its
cards point at.

```
Standard-Card
  operations:   define audit enforce adopt
  composition:  one of each
    │
    └──► shape: the struct
           │
           ├─ the harness card — its four sections filled
           ├─ the build card — its four sections filled
           └─ … one per card in the catalog
```

**Standard** — a Standard is the kind a card's Define cell points at:
one class of object as its population, plus named rules over one
member's state ([definition](/doc-types/standard/definition.md)). It
carries instance-level grain: every Standard owns a distinct rule set.
Its shape is one population and its rules, and `scripts/rulegen`
collapses every Standard to two tables, `card, standard, population`
and `card, standard, rule, when`.

**Runbook** — a runbook is an invocable command: a skill or an
agent definition
([definition](/doc-types/runbook/definition.md)).
It carries instance-level grain: every runbook owns a distinct
chain. Its shape is the Reference chain, and `scripts/chaingen`
draws every runbook's chain. Its free composition rule demands deep
machinery: a grammar, a parser, a drift check.

```
Runbook
  operations:   read write do … — the full set in
                [contract-shape.md]
  composition:  any number, coarsely ordered
    │
    └──► shape: the chain — the Reference chain
           │
           ├─ /intake's chain    one contract
           ├─ /commit's chain    another
           └─ … one per runbook
```

A card is to Standard-Card what `/intake` is to Runbook: one instance,
one filled shape, one contract. The detail files under a card sit below
its contract the way a runbook's prose body sits below its chain.

Instances never live in the doc-type tree — they stay with their
populations, and a contract rides inside its instance file.

## The bundle

A built doc-type is one directory under `doc-types/`, and every
directory holds the same files, each one layer. `definition.md` says
what the kind is and names its family. `contract-shape.md` declares
the shape, in prose and in one screen of pseudocode, a class with
typed fields and rules over its own state, and the view: the CLOA
object every instance collapses to.
`encoding.md` is the layer below the shape: how the family's instances
are written so deterministic code generates the view, the primitive
map of [Doc-Type](/doc-types/doc-type.md#layers-and-the-primitive-map)
written down. A generator under `scripts/` writes the view to one
file in the directory and fails on drift with `--check`.
`residual-ledger.md` records what the shape cannot express, one entry
per instance that has one. Each file holds its own layer and the
directory's `index.md` is the map between them.

## Shape and obligation

A doc-type declares what a contract shape *is*; it never binds
anyone to use it. The binding rule — every instance in the family
must carry its contract — is a Standard card's job: Runbook's
obligation rides
[runbook-conventions](/standards/harness/runbook-conventions.md),
audited by the chain drift check. The shape is never itself a
Standard, so Standard-Card and Runbook remain peers in this roster.

## The import surface

A consumer repo writes its own doc-type-system file: an import
declaration — Runbook and Standard-Card, from dev-playbook — plus its
local rulings, and a doc-type of its own only when it declares one.
It never copies the kind definition or a shape. This is the
workspace's general pattern: dev-playbook declares a system once,
every consumer repo inherits it, and a repo declares only what is
local to it.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
