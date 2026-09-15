---
type: General-Sheet
title: Doc-Type System
description: This repo's doc-type instantiation — the registry rulings, the three built doc-types, what each directory holds, and the Standard that binds each one
---

# Doc-Type System

This repo's instantiation of [Doc-Type](/doc-types/doc-type.md): which
document kinds matter here, which doc-types are built, and what binds
their instances. The target state the system is moving toward is the
working set's, not this file's
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md)).

## Registry rulings

The registry pass runs over the repo's two registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/harness/files.md) for harness
files — and rules each kind important to the type system or not. A
registry kind is finer than a family: the registries name every kind
that may exist; a doc-type is built only for a family ruled important.

Every kind in both registries has a row, and no kind is excluded: a
type with few files and little at stake is carried as a thin doc-type,
never as an exclusion, since an exclusion is a second kind of row a
reader must learn. A row reading *pending* is not yet ruled.

| Kind | Family | Ruling |
|---|---|---|
| Candidate-List | candidate lists | Pending |
| Decision-Record | decision records | Pending |
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
| Skill | runbooks | The [Runbook](/doc-types/runbook/definition.md) doc-type |
| Agent definition | runbooks | The [Runbook](/doc-types/runbook/definition.md) doc-type |
| `CLAUDE.md` | context files | Pending |
| `rules/*.md` | context files | Pending |
| `settings.json`, `settings.local.json` | configuration | Pending |
| `hooks/` | hooks | Pending |
| `.claude/workflows/*.js` | workflows | Pending; a runtime that runs loops, not the [Loop](/doc-types/loop/definition.md) family |

## The built doc-types

Three, each one directory under `doc-types/`:

- **Runbook** — an invocable command, a skill or an agent definition
  ([definition](/doc-types/runbook/definition.md)).
- **Standard** — a normative target a class of object is held to,
  written across a card and its rulesets
  ([definition](/doc-types/standard/definition.md)).
- **Loop** — a document that drives a state toward a target state,
  pointing at runbooks and standards
  ([definition](/doc-types/loop/definition.md)).

Instances never live in the doc-type tree. They stay with their
populations, under the harness roots, `standards/`, and `loops/`, and
a contract rides inside its instance file.

## The bundle

A built doc-type is one directory under `doc-types/`, and every
directory holds the same files. `definition.md` says what the kind is,
its verbs, and its family, and where an instance lives.
`contract-shape.md` declares the shape, the parts every instance is
read as, and the view every instance collapses to. `encoding.md` is
the layer below the shape: how the family's instances are written so
deterministic code reads the view out of them. `residual-ledger.md`
records what the shape cannot express, one entry per instance that has
one. The directory's `index.md` is the map between them.

Runbook's and Standard's views are text files in the directory,
`chains.txt`, `cards.txt`, and `standards.txt`, written by
`scripts/chaingen`, `scripts/cardgen`, and `scripts/rulegen`, each of
which fails on drift with `--check`. The three scripts and their files
are temporary proofs of concept, on purpose wired into no gate and no
card: the fact base replaces them
([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
Loop's view is the Mermaid graph inside each instance and has no file
here.

## Shape and obligation

A doc-type declares what a contract shape *is*; it never binds anyone
to use it. The binding rule — every instance in the family must carry
its contract — is a Standard's job: Runbook's obligation rides
[runbook-conventions](/standards/harness/runbook-conventions.md),
audited by the chain drift check; Loop's rides
[loop-conventions](/standards/knowledge-organization/loop-conventions.md),
audited by `scripts/loop-lint` at the commit gate; Standard's rides the
Meta-Standard, [standards/standard/](/standards/standard/card.md),
audited by `scripts/standards-lint`. The shape is never itself a
Standard, so Standard, Runbook, and Loop remain peers.
