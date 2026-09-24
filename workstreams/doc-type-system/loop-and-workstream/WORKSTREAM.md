---
type: Workstream
title: Loop and Workstream
description: The head file of the Loop and Workstream child workstream — the two doc-types designed together, a loop that drives and the workstream it drives, their terms, what is settled and open, and the worklist
---

# Loop and Workstream

The child workstream that designs two doc-types together: **Loop**, built once
under [doc-types/loop/](/doc-types/loop/index.md) and now read as an
old draft, and **Workstream**, new. Speculative, per
[Synthesis Workstream](/workstreams/doc-type-system/WORKSTREAM.md). The
workflow that uses them, stints, drivers, and the principal, is
[the delegation workstream](/workstreams/delegation/WORKSTREAM.md), whose terms
this child workstream uses. Greenfield: any rule the old Loop bundle or
[Reference Model](/workstreams/doc-type-system/doc-type-system/reference-model.md)
states may be rewritten.

## Goal

Workstream and Loop, each a full peer under
[Doc-Type](/doc-types/doc-type.md), entered together in
[Reference Model](/workstreams/doc-type-system/doc-type-system/reference-model.md)
and approved by the user there before any first instance is written.

## Terms

- **Loop** — per
  [Terms](/workstreams/doc-type-system/WORKSTREAM.md#terms); the shape
  carries its parts.
- **Yield** — a loop's programmed exit to a receiver: another loop, the
  principal, or the user. An instance writes "yields when …".
- **Workstream**, **principal**, **driver**, **stint** — per
  [the delegation terms](/workstreams/delegation/WORKSTREAM.md#terms).
- **Target state**, **finding**, **predicate**, **objective** — per
  [Terms](/workstreams/doc-type-system/WORKSTREAM.md#terms).
  [Specifying a Loop](/workstreams/doc-type-system/loop-and-workstream/specifying-a-loop.md#the-three-written-forms)
  holds the three written forms, goal, predicate, and objective.

## Principles

- **Simple and composable.** The definition carries no policy. Yield is
  where a loop is programmed to yield; the user decides when a loop is
  worth writing.
- **Predicates, not fixes.** An idea about the doc-type system is
  written as a goal, a predicate, or an objective, never carried out as
  an instruction.
- **A Loop document for every loop**, one a script runs included.

## Settled

Decided with the user on 2026-09-24.

- **A loop drives a workstream: `Loop ─drive─▶ Workstream`.** The
  workstream is the state the loop drives. Workstream is passive, as
  Standard is held to and Runbook is invoked, and adds no verb.
- **The heading menu lives inside Workstream, every heading optional.**
  The menu is the one in
  [the delegation Settled](/workstreams/delegation/WORKSTREAM.md#settled);
  a heading outside it is a finding.
- **Loop's steps stay three kinds, act, verification, and yield.** An
  act points at a Runbook, a verification at a Standard, and a yield at
  a receiver.
- **The principal is a yield receiver**, beside another loop and the
  user. A checkpoint yields to the principal, which changes the plan;
  the end of a stint yields to the user.
- **The reference model comes first.** Workstream and Loop enter
  [Reference Model](/workstreams/doc-type-system/doc-type-system/reference-model.md)
  together, and the user approves both there before any instance is
  written.

## Open

- **Is Done when a Spec written for one run?** That is, the target of a
  stint, verified to zero findings like a Standard, or only the
  condition of the finish yield.
- **Does a stint's review verify against a Standard?** Accepted
  tentatively: the reviewer is a verification against a stochastic
  Standard, "a segment does what its plan said".

## Planned

- **Re-read the old Loop items.** Four items carried from the old Loop
  child workstream, each kept, rewritten, or dropped against the new model:
  - Retire `loop_lint` and move its five checks into the check
    package: `src/dev_playbook/loop_lint.py`, its tests, and the
    legacy step `playbook check` calls, replaced by one function per
    rule in `checks/doc_type.py`.
  - Three rules drafted for Loop Conventions: every step points at a
    file that exists; no Runbook edge or Standard rule lands under
    `loops/`; a verification passes on zero findings only.
  - The objective part: a scalar a proposing loop descends.
  - The Mermaid block as encoding, read by the fact base's `loop`
    extractor
    ([Planned](/workstreams/doc-type-system/fact-base/WORKSTREAM.md#planned)).
- **Decide the deferred risks.** Two, not to be solved before the first
  instances:
  - A verification that runs deterministic rules collides with the
    gates. A stochastic rule is easy for an agent to run; a
    deterministic one already runs in the repo's pre-commit hooks, so a
    loop's verification running it too is a second path to the same
    check.
  - A driver can drift from its Loop document, and no check binds them.
- **Re-read Specifying a Loop.**
  [Specifying a Loop](/workstreams/doc-type-system/loop-and-workstream/specifying-a-loop.md)
  kept, rewritten, or dropped against the new model.

## Completed

- **Write Workstream Conventions.** Done 2026-09-24:
  [Workstream Conventions](/standards/doc-type/workstream-conventions.md),
  four rules, the three deterministic ones checked in
  `checks/doc_type.py`, and the menu's names shipped in `sources.py`
  and pinned to its table by a test.
- **Write the Workstream bundle.** Done 2026-09-24:
  `doc-types/workstream/` in the four-file form, its row in
  [Doc-Type System](/doc-types/doc-type-system.md), and the `Workstream`
  type in
  [Document Types](/standards/knowledge-organization/document-types.md).
  A doc-type's verbs may now be empty, per
  [Doc-Type](/standards/doc-type/doc-type.md#verbs-are-the-operations).
- **Revise the Loop bundle.** Done 2026-09-24: `doc-types/loop/` and
  [Loop Conventions](/standards/doc-type/loop-conventions.md) brought
  to the approved model: the drive verb, a verification over one or
  more Standards, the principal as a receiver, which `loop_lint`
  accepts, and the steps as peers the graph orders.
- **Enter Workstream and Loop in the reference model.** Done
  2026-09-24: both classes, the drive edge, `Loop.acts`/`verifications`/`yields`
  in place of `steps`, a verification's `standards` list, `Workstream`
  with its `Heading` and `Stint` parts and derived `parent`/`children`
  properties, and "How they fit" rewritten. Approved by the user.
- **Build the Loop doc-type.** Its definition, shape, encoding, and
  ledger in `doc-types/loop/`, its registry row, the `typed-loop`
  location check, `loops/` with an empty index, and
  [Loop Conventions](/standards/doc-type/loop-conventions.md) checked
  by `loop_lint`. Now an old draft, per this child workstream's opening.
- **Join Workstream to the Loop child workstream.** Done 2026-09-24: the
  child workstream renamed from `loop/`, and the design of Workstream
  moved here from
  [the delegation workstream](/workstreams/delegation/WORKSTREAM.md#planned).
- **Move the head-file rules to Workstream Conventions.** Done
  2026-09-24: the bold-item rule moved to
  [Workstream Conventions](/standards/doc-type/workstream-conventions.md)
  as `a-worklist-item-opens-with-its-bold-name`. The rules that bind
  every file of a workstream stay in
  [Workstream Files](/standards/knowledge-organization/documentation-sets/workstream-files.md):
  a guess written as a guess, the Acronyms appendix, a shared term, a
  fact under a bucket, the worklist in the head file only, reach, and
  the directory layout. A Standard has one population, and those rules
  bind every file, not the head file alone. The rule that a leaf head
  file has exactly one Planned and one Completed is dropped, because
  every menu heading is optional.

## Acronyms

None.
