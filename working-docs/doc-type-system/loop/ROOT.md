---
type: General-Sheet
title: Loop
description: The root of the Loop strand — the third doc-type as a peer of Runbook and Standard, its terms, principles, and prior art, the two planned items, and what is built
---

# Loop

The strand that builds the **Loop** doc-type, a third directory under
`doc-types/` beside [runbook/](/doc-types/runbook/index.md) and
[standard/](/doc-types/standard/index.md). Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
Loop is one of the doc-type system's four doc-types
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md)):
the rules every doc-type is held to are the Standard
[Doc-Type](/standards/doc-type/doc-type.md), and a Loop's instances
are held to
[Loop Conventions](/standards/doc-type/loop-conventions.md).
Loop is a leaf: no strand's plan waits on it except by use. The
doc-type system's first instance and the fact base's simulation loop
are both loops.

## Goal

A Loop doc-type that is a full peer of Runbook and Standard under
[Doc-Type](/doc-types/doc-type.md): operations, a composition rule, a
shape, an encoding, and a residual ledger, in one directory, with its row
in the registry table and its entry in the roster of
[Doc-Type System](/doc-types/doc-type-system.md).

## Terms

- **Loop** — per
  [Terms](/working-docs/doc-type-system/ROOT.md#terms); the
  shape carries its parts.
- **Yield** — the third operation: a loop's programmed exit to
  something outside it, another loop or the user. An instance writes
  "yields when …"; the when is the instance's.
- **Target state**, **finding**, **predicate**, **objective** — per
  [Terms](/working-docs/doc-type-system/ROOT.md#terms).
  [Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md#the-three-written-forms)
  holds the three written forms, goal, predicate, and objective.

## Principles

- **Simple and composable.** The definition carries no policy. Yield is
  where a loop is programmed to yield; the user decides when a loop is
  worth writing.
- **Predicates, not fixes.** An idea about the doc-type system is
  written as a goal, a predicate, or an objective, never carried out as
  an instruction.
  [Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md)
  holds the forms.
- **A Loop document for every loop.** Shape is orthogonal to
  stochasticity
  ([Principles](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles)),
  so a fully deterministic loop, even one a workflow runs, still gets
  a Loop document. For a loop the substrate is the code that runs it,
  and the drift check binds the document to that code.

## Prior art

Act and verify are industry-standard under other names: control loops
and Kubernetes reconciliation (desired state, observed state, a
controller closing the gap; desired state written as a spec, which
agrees with having no target operation), evaluator-optimizer and
generator-critic patterns, PDCA, OODA, red-green-refactor. Yield is
where the field has no consensus (interrupt, checkpoint, a person in
the loop); the generator sense, hand control out and resume at the
same point, is the most precise word available. One difference on
purpose: industry loops are code; a Loop instance is a document that
points at runbooks and standards, and the runtime is whatever runs it.
From memory, not a fresh search.

## Planned

- **Retire `loop_lint` and move its five checks into the check
  package.** The check rewrite moved every other check into the package, by the user's ruling
  that the loop family waits for this workstream, and deleted the
  script `scripts/loop-lint`. What it left: the module
  `src/dev_playbook/loop_lint.py`, its tests, and the legacy step by
  which `playbook check` calls that module; five deterministic rules of
  [Loop Conventions](/standards/doc-type/loop-conventions.md) registered
  in `src/dev_playbook/checks/doc_type.py` by `tool_check` with
  `hook="loop-lint"`, so `playbook checks` lists them and the meta-test
  passes; the sixth, `an-act-links-a-runbook`, already a function
  there. This workstream owns the rest, after the rewrite merges to
  main: one function per rule in `checks/doc_type.py` reading the
  model, one test per rule id, the five `tool_check` lines and the
  docstring's last sentence removed, then the module, tests, and
  legacy step deleted. The unit of work is one family as the
  rewrite did every other: the four things above in one commit, with
  `make check` and `uv run playbook check .` clean after it. Fold in
  the three rules below when the Standard is revised in the
  same turn, or leave them for their own.

- **Three rules for Loop Conventions.** Drafted in the retired
  specification, deleted with it at step 8 of the doc-type system:
  every step points at a Runbook, a Standard, a Loop, or the user that
  exists; no Runbook edge and no Standard rule lands on a file under
  `loops/`; a verification passes on zero findings and on nothing else, any
  threshold being a yield's condition. Each becomes a rule of
  [Loop Conventions](/standards/doc-type/loop-conventions.md)
  or is dropped, when that Standard is next revised.

- **The objective part.** Infinitely many states satisfy a
  specification, so a loop that proposes doc-types needs a scalar to
  descend, lexicographic, residuals, then doc-types, then verbs, then
  shared verbs, with a stop on stagnation. Whether Loop gains a part
  for it, and what the part is, is decided when the doc-type system's
  first instance is written
  ([Planned](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned)).
  Then Loop is used as it stands by that instance and by the fact
  base's simulation loop
  ([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
- **The Mermaid block as encoding.** A loop extractor reads it, and
  the view is drawn from rows, so the contract shape's "no generated
  file"
  ([Acts, Verifications, and Yields](/doc-types/loop/contract-shape.md))
  gives way; the clause is rewritten when the fact base's `loop`
  extractor lands
  ([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).

## Completed

- **One-sentence definition.** Settled; it opens
  [Loop](/doc-types/loop/definition.md).
- **Family.** Files typed `Loop` under `loops/`, mirroring Standard.
  Recorded in [Loop](/doc-types/loop/definition.md).
- **Shape, directory, encoding, residual ledger.** Written to
  `doc-types/loop/`: [Acts, Verifications, and Yields](/doc-types/loop/contract-shape.md),
  its [encoding](/doc-types/loop/encoding.md), and the
  [ledger](/doc-types/loop/residual-ledger.md), seeded empty.
- **Operations and composition rule.** Three verbs, act, verify, yield;
  the verifications carry the target. Recorded in [Loop](/doc-types/loop/definition.md).
- **Location rule and registry.** The `typed-loop` check
  binds `Loop` to `loops/`; the `Loop` row and the Typed Loop rule are
  in `document-types.md`; the registry ruling and the roster entry are
  in `doc-type-system.md`; `loops/` exists with an empty index.
- **Obligation.** `src/dev_playbook/loop_lint.py` holds the checks of
  [Loop Conventions](/standards/doc-type/loop-conventions.md),
  the Standard that binds a `Loop` file to the encoding; a step of the
  `playbook check` run, so a bad Loop file cannot be committed. Tests
  in `tests/dev_playbook/test_loop_lint.py`.

## Acronyms

- **PDCA** — Plan-Do-Check-Act.
- **OODA** — Observe-Orient-Decide-Act.
