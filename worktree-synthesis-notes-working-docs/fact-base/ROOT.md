---
type: General-Sheet
title: Fact Base Strand
description: The root of the fact base strand — the one deterministic object under every view, its standing over the viewer, the rulings filed here, the worklist from hand simulations through extractors, declared data, and a stamped findings artifact, and what is done
---

# Fact Base Strand

The strand that holds the compiled object: one deterministic object of
nodes and edges extracted from a checkout, every view a selection from
it. Speculative, per
[Synthesis Working Root](/worktree-synthesis-notes-working-docs/ROOT.md).
The theory is
[Fact Base](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md);
the first simulation by hand is
[Ralph Fact Base](/worktree-synthesis-notes-working-docs/fact-base/fact-base-ralph.md),
with its rows in `fact-base-ralph.json`; and
[Deterministic Separation](/worktree-synthesis-notes-working-docs/fact-base/deterministic-separation.md)
is one planned view. Each encoding the doc-type system writes defines
an extractor here
([Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md));
every kind the viewer draws is a selection from here
([CLOA Viewer](/worktree-synthesis-notes-working-docs/viewer/ROOT.md)).

## Goal

The fact base proven by simulation before any of it is coded, then
extracted by code: one refresh writes one fact base per checkout, and
the viewer's next kinds are selections from it.

## Standing

Where the viewer pages, or anything elsewhere in the repo, disagree
with [Fact Base](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md),
that page has priority. Its claim to rule vocabulary on its own is
withdrawn: words are settled by the doc-type system's vocabulary pass,
one meaning per word across all four strands
([Planned](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#planned)).

## Terms

The fact base's terms are in
[Terms](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#terms).

## Decided

- **The fact base holds declarations and state, never findings.**
  Findings are a separate stamped artifact. Deterministic ones are
  recomputable from the fact base; stochastic ones are cached with
  commit, judge, and time. This is the seam the glossary draws between
  a set and a distribution.
- **"Rule" splits.** The fact base's rows-to-rows function with no
  judgment is a derivation. Its rows-to-violations function is a
  verifier keyed by rule id. Standard keeps "rule". The rename runs in
  the vocabulary pass.

## Planned

In order; each produces what the next needs.

- **Simulations by hand.** Enumerate the use cases and hand-write a
  fact base per subsystem, in the viewer's envelope, every row with a
  receipt, per the first of the fact base's
  [Next steps](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#next-steps).
  No code is written until the simulations cover the expected use
  cases.
- **The simulation as a loop.** The third simulation is a loop, not a
  session, per the second of the fact base's
  [Next steps](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#next-steps).
- **Extractors.** [chaingen](/scripts/chaingen) and
  [rulegen](/scripts/rulegen), the scripts that write the text files
  today, move into the package as the `chain` and `standard`
  extractors, the scripts and their text files deleted with the move
  and their logic kept, alongside the bedrock extractors, and a `loop` extractor
  reads a Loop document's Mermaid block
  ([Decided](/worktree-synthesis-notes-working-docs/loop/ROOT.md#decided));
  one refresh writes one fact base per checkout; `chains.txt`, its
  siblings, and the shims go. The `card` extractor and `cardgen` are
  struck: the doc-type system retires Standard-Card, step 4 of
  [Planned](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#planned).
- **Docs follow the moves.** The `doc-types/` indexes and pages that
  name the text files and the shims, and `scripts/index.md`.
- **Verifier table and boundary config as declared data.** The rule id
  to verifier map, step 2 of the doc-type system's refactor, and the
  rule id to boundary map, step 3, are declared data in a fixed shape
  with an extractor, wherever they live, so a solver can read them.
  The fact base extracts declared files and bedrock only, so a map
  that is not declared data is not in it.
  Where they are declared is open.
- **Findings as a stamped artifact.** The artifact the first Decided
  item names: its shape, its stamp of commit, judge, and time, and how
  a deterministic finding is recomputed from the fact base.
- **The per-predicate tail query.**
  [Deterministic Separation](/worktree-synthesis-notes-working-docs/fact-base/deterministic-separation.md)
  as a view: for each rule id, which stochastic nodes lie between its
  last verifier and the end. Whether it is a view in the registry's
  sense or a query beside the fact base is open.

## Open

The fact base's parked questions are in
[Open questions](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#open-questions).

## Completed

- **Fact base.** The concept and one hand simulation, 2026-09-10;
  reconciled with the viewer on 2026-09-14.

## Acronyms

None.
