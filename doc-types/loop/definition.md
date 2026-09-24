---
type: General-Sheet
title: Loop
description: What a loop is — a document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards — its four verbs, the family it serves, and where it lives
---

# Loop

A **loop** drives a state toward a target state by iteratively taking
prescribed actions and validating against prescribed standards. A
runbook is one move, a run of a standard's verifiers is one
measurement, a loop is moves and measurements iterated toward a target.

## The verbs

Four. Three are steps, iterated, and the fourth is what the steps do
to a workstream:

- **act** — a pointer at a runbook.
- **verify** — a pointer at one or more standards, whose verifiers are
  run.
- **yield** — a programmed exit to another loop, the user, or a stint's
  principal, resumed where it left.
- **drive** — what a loop does to a
  [workstream](/doc-types/workstream/definition.md). The loop names no
  workstream: a stint binds one loop to one workstream, and the
  workstream records it.

The target is not a field of the loop: it is written in the standards
the verifications measure against. An act reads a standard to know
what the target looks like; a verification runs the same standard's
verifiers, checks and judges, to measure the distance, and the target
state is reached when every verification returns no findings.

A loop yields where its author put the yield, never, once at the end,
every K rounds, every turn, and the doc-type does not say when. A loop
is out of standard until its last step, and many never get there, so
the standards it verifies against are run by the loop, never at a gate
([Standard](/doc-types/standard/definition.md)).

## The family

The documents typed `Loop` under `loops/`, one file per loop. A Loop
instance is the specification of a procedure that brings a system
closer to its target state; the workflow script, skill, or person that
runs it is the loop's driver, not the loop. A loop does one thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its acts, its verifications, and its yields, drawn as one graph. One
loop drives many workstreams.

## Where a loop lives

A document typed `Loop` lives under `loops/`, or as a draft in a working
documentation set under `working-docs/`; nothing else claims the label. A consumer repo keeps its own `loops/` for its own
loops, the way it keeps its own `standards/`.
