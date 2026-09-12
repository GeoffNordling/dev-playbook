---
type: General-Sheet
title: Loop
description: What a loop is — a document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards — the family it serves, and where it lives
---

# Loop

A **loop** drives a state toward a target state by iteratively taking
prescribed actions and validating against prescribed standards. It is
three verbs, iterated: *act*, a pointer at a runbook; *check*, a
pointer at a standard's audit; *yield*, a programmed exit to another
loop or to the user, resumed where it left. A runbook is one move, an
audit is one measurement, a loop is moves and measurements iterated
toward a target. The target is not a field of the loop: it is written
in the standards the checks measure against. An act reads a standard's
definition to know what the target looks like; a check runs the same
standard's audit to measure the distance, and the target state is
reached when every check returns no findings.

A loop yields where its author put the yield, never, once at the end,
every K rounds, every turn, and the doc-type does not say when. A loop
is out of standard until its last step, and many never get there, so
the standards it checks against are audited, not gated
([Standard-Card](/doc-types/standard-card/definition.md)).

The family is the documents typed `Loop` under `loops/`, one file per
loop. A Loop instance is the specification of a procedure that brings a
system closer to its target state; the workflow script, skill, or
person that runs it is the substrate, not the loop. A loop does one
thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its acts, its checks, and its yields, drawn as one graph.

## Where a loop lives

A document typed `Loop` lives under `loops/`; nothing outside that tree
claims the label. A consumer repo keeps its own `loops/` for its own
loops, the way it keeps its own `standards/`.
