---
type: General-Sheet
title: Doc-Type System
description: This repo's doc-type instantiation — the registry rulings, the five built doc-types, what each directory holds, and the Standard that binds each one
---

# Doc-Type System

This repo's instantiation of [Doc-Type](/doc-types/doc-type.md): which
document kinds matter here, which doc-types are built, and what binds
their instances. The whole system is drawn in
[Reference Model](/doc-types/reference-model.md).

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
| Guide | guides | The [Guide](/doc-types/guide/definition.md) doc-type |
| Log | logs | Pending; the user's to rule |
| Loop | loops | The [Loop](/doc-types/loop/definition.md) doc-type |
| Mirror | mirrors | Pending |
| README | readmes | Pending |
| Recipe-Description | recipes | Pending |
| Standard | standards | The [Standard](/doc-types/standard/definition.md) doc-type |
| Survey | surveys | Pending; the user's to rule |
| Workstream | workstreams | The [Workstream](/doc-types/workstream/definition.md) doc-type |
| Vocabulary | — | Separate — the vocabulary API ([System Legibility](/docs/system-legibility.md)), not a doc-type |
| Skill | runbooks | The [Runbook](/doc-types/runbook/definition.md) doc-type |
| Agent definition | runbooks | The [Runbook](/doc-types/runbook/definition.md) doc-type |
| `CLAUDE.md` | context files | Pending |
| `rules/*.md` | context files | Pending |
| `settings.json`, `settings.local.json` | configuration | Pending |
| `hooks/` | hooks | Pending |
| `.claude/workflows/*.js` | workflows | Pending; a runtime that runs loops, not the [Loop](/doc-types/loop/definition.md) family |

## The built doc-types

Five, each one directory under `doc-types/`:

- **Runbook** — an invocable command, a skill or an agent definition
  ([definition](/doc-types/runbook/definition.md)).
- **Standard** — a normative target a class of object is held to,
  one population and its rules, each carrying its own why
  ([definition](/doc-types/standard/definition.md)).
- **Guide** — instructs one kind of work
  ([definition](/doc-types/guide/definition.md)).
- **Loop** — a document that drives a workstream toward a target
  state, pointing at runbooks and standards
  ([definition](/doc-types/loop/definition.md)).
- **Workstream** — one line of work, its ideas, target state, and
  context, driven by a loop
  ([definition](/doc-types/workstream/definition.md)).

Instances never live in the doc-type tree. They stay with their
populations, under the harness roots, `standards/`, `guides/`,
`loops/`, and `workstreams/`, and a contract rides inside its instance file.

## The bundle

A built doc-type is one directory under `doc-types/`, and every
directory holds the same files. `definition.md` says what the kind is,
its verbs, and its family, and where an instance lives.
`contract-shape.md` declares the shape, the parts every instance is
read as. `encoding.md` is the layer below the shape: how the family's
instances are written so deterministic code reads the parts out of
them. `residual-ledger.md`
records what the shape cannot express, one entry per instance that has
one. The directory's `index.md` is the map between them.

No view is generated today. The three prototype generators,
`chaingen`, `cardgen`, and `rulegen`, and the text files they wrote are
deleted and kept in git history, the last of them at commit `b266ce4`;
the fact base's extractors are the planned successors
([Planned](/workstreams/system/see/fact-base/WORKSTREAM.md#planned)).
Loop's view is the Mermaid graph inside each instance.

## Shape and obligation

A doc-type declares what a contract shape *is*; it never binds anyone
to use it. The binding rule — every instance in the family must carry
its contract — is a Standard's job, and the five sit together under
[standards/doc-type/](/standards/doc-type/index.md): Runbook's
obligation rides
[Runbook Conventions](/standards/doc-type/runbook-conventions.md),
checked by `playbook check`; Loop's rides
[Loop Conventions](/standards/doc-type/loop-conventions.md), checked
by `playbook check`; Standard's rides
[Standard Conventions](/standards/doc-type/standard-conventions.md),
checked by `playbook check`; Guide's rides
[Guide Conventions](/standards/doc-type/guide-conventions.md);
Workstream's rides
[Workstream Conventions](/standards/doc-type/workstream-conventions.md),
checked by `playbook check`. The shape is never itself a Standard, so the five remain peers.
