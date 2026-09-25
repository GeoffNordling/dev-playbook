---
type: Workstream
title: See Workstream
description: The head file of the See child workstream — deterministic code shows what a checkout does at the CLOA, through the fact base, its ontology, and the viewer, with story-forge as the proof by hand; the principles, terms, and acronyms its children share
---

# See Workstream

The child workstream that lets the user see a system without reading
it. Speculative, per
[System Workstream](/workstreams/system/WORKSTREAM.md). It holds three
child workstreams, and this head file holds only what crosses them.

## Goal

Deterministic code shows what a checkout does, at the CLOA. The object
underneath is a typed property graph compiled from declared documents,
in the lineage of Kythe and Glean
([Precedent](/workstreams/system/see/fact-base/precedent.md)). It is
not a knowledge graph in the usual sense, where a model extracts the
facts and the schema grows freely: here a parser yields every row with
a receipt, and every relation type belongs to a declared doc-type.

The doc-type system, built and closed under
[`doc-types/`](/doc-types/index.md), enables the rest: without
doc-types there is no ontology to solve and no fact to extract.

- **Fact base**: one fact base per checkout, extracted by code from
  the declared doc-types, with the ontology inside it checking what may
  point at what. Head file:
  [Fact Base Workstream](/workstreams/system/see/fact-base/WORKSTREAM.md).
- **Viewer**: the fact base on a browser screen, one registered view
  per panel, no model tokens. Head file:
  [CLOA Viewer](/workstreams/system/see/viewer/WORKSTREAM.md).
- **Story-forge**: the fact base and its views simulated by hand with
  agents on a real repo, before any of it is coded, to prove they are
  worth building. Head file:
  [Story-Forge Simulation](/workstreams/system/see/story-forge/WORKSTREAM.md).

The fact base runs next. The viewer's next views wait on it, since each
is a selection from it. Story-forge runs now, ahead of the code, and
takes its method from the fact base.

## Done when

The viewer draws the fact base's views of a real repo.

## Principles

- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what
  [the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
  calls the residual. The bedrock of determinism is a threshold on
  content, not a line between file kinds.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. A drift check binds the document to
  the code it describes; a loop has none yet
  ([Driver drift](/workstreams/system/drive/WORKSTREAM.md#planned)).
- **An extractor is the inverse of a declared encoding.** An agent
  that writes an extractor also writes the doc-type it read from, in
  the reference model's pseudocode, so its assumptions are inspected
  as a short class and not as the parsing code.
- **Permissions, rules, and views read one fact base.** The ontology
  grants which node types may point at which; a rule checks one fact,
  such as whether a link's target exists; a view draws the facts. A
  dangling edge violates a rule, never the ontology.
- **A view is code, registered by name.** Each view is a function with
  one stated question it answers; the code is the spec, and the
  question is the only prose it needs.

## Terms

Fact base, node, edge, extractor, encoding, view, primitive, and
residual are in [CONTEXT.md](/CONTEXT.md). The terms the children
share:

- **Receipt** — the extractor and the line that yielded a row. Every
  row carries one, so every fact can be checked against its file and
  every missing fact shows where a declaration would have to be. A
  derived row's receipt names the derivation and the rows it derived
  from.
- **Derivation** — a deterministic function from rows to rows. It
  reads the fact base and derives new rows from existing ones, with no
  judgment, and never touches a file.
- **Vocabulary** — the closed set of primitives one doc-type owns
  ([the chain](/doc-types/runbook/contract-shape.md#edges)).
- **Schema** — the fact base's set of node types and relation types:
  the union of every vocabulary plus the bedrock relations. The fact
  base has a schema and no vocabulary of its own.
- **Checkout** — one working copy of a repo, a main checkout or a
  worktree: the unit a fact base describes and the viewer shows.
- **Envelope** — the fixed top-level fields every view file and every
  hand-written fact base carries around its payload
  ([the envelope](/workstreams/system/see/viewer/contract.md#the-envelope)).

## Acronyms

- **API** — Application Programming Interface.
- **HTML** — Hypertext Markup Language.
- **JSON** — JavaScript Object Notation.
- **SVG** — Scalable Vector Graphics.
- **YAML** — YAML Ain't Markup Language.
