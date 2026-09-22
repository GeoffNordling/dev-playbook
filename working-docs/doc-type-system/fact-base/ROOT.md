---
type: General-Sheet
title: Fact Base Strand
description: The root of the fact base strand — the one deterministic object under every view, its standing over the viewer, its principle and terms, the worklist from hand simulations through extractors, declared data, and a stamped findings artifact, and what is done
---

# Fact Base Strand

The strand that holds the compiled object: one deterministic object of
nodes and edges extracted from a checkout, every view a selection from
it. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
The theory is
[Fact Base](/working-docs/doc-type-system/fact-base/fact-base.md),
with its prior art in
[Precedent](/working-docs/doc-type-system/fact-base/precedent.md);
the first simulation by hand is
[Ralph Fact Base](/working-docs/doc-type-system/fact-base/fact-base-ralph.md),
with its rows in `fact-base-ralph.json`; and
[Deterministic Separation](/working-docs/doc-type-system/fact-base/deterministic-separation.md)
is one planned view. Each encoding the doc-type system writes defines
an extractor here
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md));
every kind the viewer draws is a selection from here
([CLOA Viewer](/working-docs/doc-type-system/viewer/ROOT.md)).

## Goal

The fact base proven by simulation before any of it is coded, then
extracted by code: one refresh writes one fact base per checkout, and
the viewer's next kinds are selections from it.

## Standing

Where the viewer pages, or anything elsewhere in the repo, disagree
with [Fact Base](/working-docs/doc-type-system/fact-base/fact-base.md),
that page has priority. It defines no word: the words the strand
shares are the set's, and its own are below.

## Principles

- **The fact base holds declarations and state, never findings.**
  Findings are a separate stamped artifact. Deterministic ones are
  recomputable from the fact base; stochastic ones are cached with
  commit, judge, and time. This is the seam Terms draws between a set
  and a distribution.

## Terms

Fact base, node, edge, extractor, derivation, view, and residual are
defined in the set's
[Terms](/working-docs/doc-type-system/ROOT.md#terms). The
strand's own:

- **Receipt** — the extractor and the line that yielded a row. Every
  row carries one, so every fact can be checked against its file and
  every missing fact shows where a declaration would have to be. A
  derived row's receipt names the derivation and the rows it derived
  from.
- **Primitive** — one named element of a vocabulary: `reads`,
  `bucket:git`, `contains`.
- **Vocabulary** — the closed set of primitives one doc-type owns
  ([the chain](/doc-types/runbook/contract-shape.md#edges)).
- **Schema** — the fact base's set of node types and relation types:
  the union of every vocabulary plus the bedrock relations. The fact
  base has a schema and no vocabulary of its own.

## Planned

In order; each produces what the next needs.

- **Simulations by hand.** Enumerate the use cases, the questions a
  person asks of the system, and hand-write a fact base per subsystem
  like the Ralph one, in the viewer's envelope, every row with a
  receipt. The use cases recorded for the runbook population in the
  first design session: what is there, split Agent and Skill; where the
  user enters, the runbooks no other runbook does, and their complement
  the leaves; who does whom, the `does` edges and their connected
  clusters; what each can touch, the writes buckets and the never bans;
  what the fleet runs on, model, effort, and tools per Agent; and how
  heavy each is, counted from the object and from the file. One subject
  was named, the software factory, whose agents are singletons in the
  `does` graph because the factory's own graph lives in
  `software-factory.md`, which issue-overwatch reads as a bare imported
  node; the factory is isolated under `working-docs/software-factory/`
  since 2026-09-20, so that subject waits on its fate. Each use case names a subsystem; each simulation firms the
  seven views, adds extractors, and writes residuals; and one
  simulation is a consumer-repo subsystem, the first data point for
  residual ownership across repos
  ([Open questions](/working-docs/doc-type-system/fact-base/fact-base.md#open-questions)).
  No code is written until the simulations cover the expected use
  cases.
- **The simulation as a loop.** The second simulation is already
  repeatable work, and the third is a loop, not a session: an agent
  re-expresses the subsystem in the current primitives, writes the fact
  base and the residuals, and proposes primitives; the user accepts or
  rejects and justifies neither. The same loop later writes extractors
  and derivations. The user designs from scratch only at a beginning,
  the way
  [Fact Base](/working-docs/doc-type-system/fact-base/fact-base.md)
  was designed.
- **Extractors.** `chaingen` and `rulegen`, deleted by the doc-type
  plan's steps 7 and 6 and kept in git history at commits `b266ce4` and
  `9be0089`, are the models for the `chain` and `standard` extractors
  in the package, alongside the bedrock extractors, and a `loop` extractor
  reads a Loop document's Mermaid block
  ([Planned](/working-docs/doc-type-system/loop/ROOT.md#planned));
  one refresh writes one fact base per checkout; the shims go. The `card` extractor and `cardgen` are
  struck: the doc-type system retires Standard-Card, Retire the card in
  [Planned](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned).
- **Docs follow the moves.** The `doc-types/` indexes and pages that
  name the text files and the shims, and `scripts/index.md`.
- **Verifier table and boundary config as declared data.** The rule id
  to verifier map, step 2 of the doc-type system's refactor, and the
  rule id to boundary map, step 3, are declared data in a fixed shape
  with an extractor, wherever they live, so a solver can read them.
  The fact base extracts declared files and bedrock only, so a map
  that is not declared data is not in it.
  Where they are declared is open.
- **Findings as a stamped artifact.** The artifact Principles
  names: its shape, its stamp of commit, judge, and time, and how
  a deterministic finding is recomputed from the fact base.
- **The per-predicate tail query.**
  [Deterministic Separation](/working-docs/doc-type-system/fact-base/deterministic-separation.md)
  as a view: for each rule id, which stochastic nodes lie between its
  last verifier and the end. Whether it is a view in the registry's
  sense or a query beside the fact base is open.

## Open

The fact base's parked questions are in
[Open questions](/working-docs/doc-type-system/fact-base/fact-base.md#open-questions).

## Completed

- **Fact base.** The concept and one hand simulation, 2026-09-10;
  reconciled with the viewer on 2026-09-14.

## Acronyms

None.
