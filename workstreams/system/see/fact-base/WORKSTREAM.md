---
type: Workstream
title: Fact Base Workstream
description: The head file of the fact base child workstream — one deterministic object of nodes and edges per checkout, with the ontology inside it, its standing over the viewer, its principles and terms, the worklist from hand simulations through extractors and the ontology's solver, and what is done
---

# Fact Base Workstream

The child workstream that holds the compiled object: one deterministic
object of nodes and edges extracted from a checkout, every view a
selection from it, and the ontology that says what in it may point at
what. Speculative, per
[See Workstream](/workstreams/system/see/WORKSTREAM.md). Its files:

- [Fact Base](/workstreams/system/see/fact-base/fact-base.md) — the
  theory.
- [Ontology Solvers](/workstreams/system/see/fact-base/ontology-solvers.md)
  — the ontology in industry terms, and the solver that checks it.
- [Precedent](/workstreams/system/see/fact-base/precedent.md) — the
  prior art.
- [Ralph Fact Base](/workstreams/system/see/fact-base/fact-base-ralph.md)
  — the first simulation by hand, with its rows in
  `fact-base-ralph.json`.
- [Deterministic Separation](/workstreams/system/see/fact-base/deterministic-separation.md)
  — one planned view.

Each encoding a doc-type defines is an extractor here
([Doc-Type System](/doc-types/doc-type-system.md)); every view the
viewer draws is a selection from here
([CLOA Viewer](/workstreams/system/see/viewer/WORKSTREAM.md)).

## Goal

One fact base per checkout, extracted by code from the declared
doc-types, with the ontology checking what may point at what. The fact
base is proven by simulation before any of it is coded, then extracted
by code, and the viewer's next views are selections from it.

### Standing

Where the viewer pages, or anything elsewhere in the repo, disagree
with [Fact Base](/workstreams/system/see/fact-base/fact-base.md),
that page has priority.

## Done when

One refresh writes the fact base of a checkout, and the solver runs
over it.

## Principles

- **The fact base records what is declared, not what happens.** A
  fact says what a file declares or what a parser found. A `reads`
  edge from a runbook says the runbook tells an agent to read a file,
  not that the agent will
  ([The record is not the behavior](/workstreams/system/see/fact-base/fact-base.md#the-record-is-not-the-behavior)).
- **The ontology is part of the fact base, and there is one solver.**
  The fact base is the ABox; the doc-types are the TBox, and the
  doc-type system is what makes an ontology to solve at all
  ([Ontology Solvers](/workstreams/system/see/fact-base/ontology-solvers.md)).
  One engine checks the document ontology, declared once in
  dev-playbook, and a consumer repo's domain ontology, over one fact
  base per checkout.

## Terms

The terms the See children share are in
[See Workstream](/workstreams/system/see/WORKSTREAM.md#terms), and the
terms the main part of the repo also uses are in
[CONTEXT.md](/CONTEXT.md). The terms of this child workstream:

- **ABox** — the facts of a knowledge base, each a triple of subject,
  predicate, and object. The fact base is an ABox.
- **TBox** — the schema of a knowledge base: classes, properties with
  a domain and a range, and a class hierarchy. The doc-types are a
  TBox.

## Planned

In order; each produces what the next needs.

- **Simulations by hand.** Stochastic agents simulate the fact base
  and its views before any of it is built, to test that it has real
  value first
  ([Story-Forge Simulation](/workstreams/system/see/story-forge/WORKSTREAM.md)).
- **Extractors.** `chaingen` and `rulegen`, deleted and kept in git
  history at commits `b266ce4` and `9be0089`, are the models for the
  `chain` and `standard` extractors in the package, alongside the
  bedrock extractors, and a `loop` extractor reads a Loop document's
  Mermaid block. One refresh writes one fact base per checkout. The
  `doc-types/` pages that name the deleted prototypes then point at the
  extractors.
- **Verifier table and boundary config as declared data.** The rule id
  to verifier map and the rule id to boundary map are declared data in
  a fixed shape with an extractor, wherever they live, so the solver
  can read them. The fact base extracts declared files and bedrock
  only, so a map that is not declared data is not in it. Where they are
  declared is open.
- **The ontology and its solver.** The doc-types declared as the TBox
  in a form the solver reads, a Standard's rules as shapes, and one
  solver run over the fact base, its violations findings with
  receipts
  ([Ontology Solvers](/workstreams/system/see/fact-base/ontology-solvers.md)).
- **The per-predicate tail query.**
  [Deterministic Separation](/workstreams/system/see/fact-base/deterministic-separation.md)
  as a view: for each rule id, which stochastic nodes lie between its
  last verifier and the end. Whether it is a view in the registry's
  sense or a query beside the fact base is open.

## Open

The fact base's parked questions are in
[Open questions](/workstreams/system/see/fact-base/fact-base.md#open-questions).

## Completed

- **Fact base.** The concept and one hand simulation, 2026-09-10;
  reconciled with the viewer on 2026-09-14.

## Acronyms

- **EM** — Expectation-Maximization.
- **MIP** — Mixed-Integer Programming.
- **OWL** — Web Ontology Language.
- **RDFS** — Resource Description Framework Schema.
- **SHACL** — Shapes Constraint Language.
