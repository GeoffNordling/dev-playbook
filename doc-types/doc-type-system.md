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
| Log | logs | Pending; the user's to rule |
| Loop | loops | The [Loop](/doc-types/loop/definition.md) doc-type |
| README | readmes | Pending |
| Recipe-Description | recipes | Pending |
| Reference | references | Pending |
| Standard-Card | standards | The [Standard](/doc-types/standard/definition.md) doc-type |
| Standard-Ruleset | standards | The [Standard](/doc-types/standard/definition.md) doc-type |
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

**Standard** — a Standard is a normative target that is defined,
audited, enforced, and adopted
([definition](/doc-types/standard/definition.md)). It is written across
two file kinds: the card, `Standard-Card`, the record of its four verbs,
one cell each; and its rulesets, `Standard-Ruleset`, one population and
its rules, what the Define cell points at. Its shape is the four cells
and the ruleset beneath Define. `scripts/cardgen` collapses every card
to rows of `card, cell, pointer`; `scripts/rulegen` collapses every
ruleset to two tables, `card, standard, population` and
`card, standard, rule, when`. The card's fixed composition keeps its
machinery sparse: headings suffice, and its determinism lives in the
detectors and gates its cells point at.

```
Standard
  operations:   define audit enforce adopt
  composition:  one cell each, any number of pointers; under Define,
                one population and any number of rules per ruleset
    │
    └──► shape: the card, four cells; the rulesets it defines by
           │
           ├─ the harness Standard — its card and rulesets
           ├─ the build Standard — its card and rulesets
           └─ … one per directory under standards/
```

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

**Loop** — a loop drives a state toward a target state by iteratively
taking prescribed actions and validating against prescribed standards
([definition](/doc-types/loop/definition.md)). It carries
instance-level grain: every loop owns its own acts, checks, and yields.
Its shape is acts, checks, and yields, iterated, and its view is the
Mermaid graph in each instance; it has no generator and no generated
file. It composes the other two peers by pointer: an act points at a
runbook, a check at a standard's audit.

```
Loop
  operations:   act check yield
  composition:  any number of acts and checks, in iteration
                order; a set of yield conditions
    │
    └──► shape: the graph — acts, checks, yields, and receivers
           │
           └─ … one per loop; none written yet
```

A directory under `standards/` is to Standard what `/intake` is to
Runbook: one instance, one filled shape, one contract. The rulesets
under a card sit below its contract the way a runbook's prose body sits
below its chain.

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
file in the directory and fails on drift with `--check`; a doc-type
whose view is a graph inside each instance has none.
`residual-ledger.md` records what the shape cannot express, one entry
per instance that has one. Each file holds its own layer and the
directory's `index.md` is the map between them.

## Shape and obligation

A doc-type declares what a contract shape *is*; it never binds
anyone to use it. The binding rule — every instance in the family
must carry its contract — is a Standard card's job: Runbook's
obligation rides
[runbook-conventions](/standards/harness/runbook-conventions.md),
audited by the chain drift check; Loop's rides
[loop-conventions](/standards/knowledge-organization/loop-conventions.md),
audited by `scripts/loop-lint` at the commit gate; Standard's rides the
Meta-Standard, [standards/standard/](/standards/standard/card.md),
audited by `scripts/standards-lint`. The shape is never itself a
Standard, so Standard, Runbook, and Loop remain peers in this roster.

## The import surface

A consumer repo writes its own doc-type-system file: an import
declaration — Runbook, Standard, and Loop, from dev-playbook — plus its
local rulings, and a doc-type of its own only when it declares one.
It never copies the kind definition or a shape. This is the
workspace's general pattern: dev-playbook declares a system once,
every consumer repo inherits it, and a repo declares only what is
local to it.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
