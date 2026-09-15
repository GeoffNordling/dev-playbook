---
type: General-Sheet
title: Loop
description: The root of the Loop strand — the third doc-type as a peer of Runbook and Standard, its principles and terms, the two planned items, and what is built
---

# Loop

The strand that builds the **Loop** doc-type, a third directory under
`doc-types/` beside [runbook/](/doc-types/runbook/index.md) and
[standard/](/doc-types/standard/index.md). Speculative, per
[Synthesis Working Root](/worktree-synthesis-notes-working-docs/ROOT.md).
Loop is one of the doc-type system's three doc-types
([Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md)):
its predicates are
[Loop Specification](/worktree-synthesis-notes-working-docs/doc-type-system/specification/loop.md),
and where it stands among its peers is
[Three Peers](/worktree-synthesis-notes-working-docs/doc-type-system/three-peers.md).
Loop is a leaf: no strand's plan waits on it except by use. The
doc-type system's first instance and the fact base's simulation loop
are both loops.

## Goal

A Loop doc-type that is a full peer of Runbook and Standard under
[Doc-Type](/doc-types/doc-type.md): operations, a composition rule, a
shape, an encoding, and a residual ledger, in one directory, with its row
in the registry table and its entry in the roster of
[Doc-Type System](/doc-types/doc-type-system.md).

## Principles

- **Simple and composable.** The definition carries no policy. Yield is
  where a loop is programmed to yield; the doc-type does not rule when a
  loop is worth writing. The user decides that.
- **Predicates, not fixes.** An idea about the doc-type system is
  written as a goal, a predicate, or an objective, never carried out as
  an instruction.
  [Specifying a Loop](/worktree-synthesis-notes-working-docs/loop/specifying-a-loop.md)
  holds the forms.
- **Every loop gets a Loop document.** Shape is orthogonal to
  stochasticity, general over doc-types
  ([Principles](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#principles)):
  a fully deterministic loop, even one a workflow runs, still gets a
  Loop document, because the document is the legible form. Three
  Peers states it as the instance's sentence, a Loop instance is a
  document and code that runs it is its substrate, with the drift
  check that binds the two
  ([Three Peers](/worktree-synthesis-notes-working-docs/doc-type-system/three-peers.md#loop-today)).

## Terms

- **Loop** — the one sentence of [Loop](/doc-types/loop/definition.md);
  the shape carries its parts.
- **Yield** — the third operation: a loop's programmed exit to
  something outside it, another loop or the user. An instance writes
  "yields when …"; the when is the instance's.
- **Target state**, **finding**, **predicate** — per
  [Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms).
  [Specifying a Loop](/worktree-synthesis-notes-working-docs/loop/specifying-a-loop.md#the-three-written-forms)
  holds the three written forms, goal, predicate, and objective.

## Planned

- **The objective part.** Infinitely many states satisfy a
  specification, so a loop that proposes doc-types needs a scalar to
  descend, lexicographic, residuals, then doc-types, then verbs, then
  shared verbs, with a stop on stagnation. Whether Loop gains a part
  for it, and what the part is, is decided when the doc-type system's
  first instance is written
  ([Planned](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#planned)).
  Then Loop is used as it stands by that instance and by the fact
  base's simulation loop
  ([Planned](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#planned)).
- **The Mermaid block is encoding.** A loop extractor reads it, and
  the view is drawn from rows, so the contract shape's "no generated
  table and no generator"
  ([Acts, Checks, and Yields](/doc-types/loop/contract-shape.md))
  gives way; the clause is rewritten when the fact base's `loop`
  extractor lands
  ([Planned](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#planned)).

## Completed

- **One-sentence definition.** Settled; it opens
  [Loop](/doc-types/loop/definition.md).
- **Family.** Files typed `Loop` under `loops/`, mirroring Standard.
  Recorded in Three Peers.
- **Shape, directory, encoding, residual ledger.** Written to
  `doc-types/loop/`: [Acts, Checks, and Yields](/doc-types/loop/contract-shape.md),
  its [encoding](/doc-types/loop/encoding.md), and the
  [ledger](/doc-types/loop/residual-ledger.md), seeded empty.
- **Operations and composition rule.** Three verbs, act, check, yield;
  the checks carry the target. Recorded in Three Peers.
- **Location rule and registry.** okf-lint's `type-location` check
  binds `Loop` to `loops/`; the `Loop` row and the Typed Loop rule are
  in `document-types.md`; the registry ruling and the roster entry are
  in `doc-type-system.md`; `loops/` exists with an empty index.
- **Obligation.** `scripts/loop-lint` is the detector behind
  [Loop Conventions](/standards/knowledge-organization/loop-conventions.md),
  the Standard that binds a `Loop` file to the encoding; enrolled in the
  `playbook-lint` roster, so a bad Loop file cannot be committed. Logic in
  `src/dev_playbook/loop_lint.py`, tests beside it.

## Acronyms

None.
