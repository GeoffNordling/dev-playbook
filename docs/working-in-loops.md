---
type: General-Sheet
title: Working in Loops
description: The doctrine — agents work in loops, and the user works on the loops
---

# Working in Loops

How work gets done in the workspace: agents work in loops, and the user
works on the loops.

## The goal

Linear work — one session, the user and one agent, one task at a time,
powering through — is unsustainable. It built this repository, and the
backlog grew faster than the sessions drained it. The user has less free time and the models are stronger every month; a way of working
that spends the scarce resource one result at a time does not survive
that.

The user's time goes into loops, contracts, and detectors. A loop runs
without the user. A detector catches its class of slop before it bubbles up.

## Why linear work fails

A shape is defined and agents are dispatched. The output comes back in
the right shape and full of slop: comments through the prose, claims the
user cannot tell from inventions. The user fixes it by hand, turn by
turn. The fix is consumed once, and the next dispatch makes the same
slop. The shape was a contract and the agents obeyed it; nothing
verified what the shape did not say.

## What a loop stands on

Improvement needs verification. Verification needs measurement.
Measurement needs expression: a property written as a programmable
operation over the object's state. Each layer stands on the one below.

## Loops

A **loop** is a named, registered procedure: it dispatches agents over a
population against a contract, verifies the output, and stops at an exit
condition. It runs without the user; the user looks at the end.

A loop is described in markdown, so Loop is a doc-type; its shape is
found the way every doc-type's is, by running the loop on the family
([Doc-Type](/doc-types/doc-type.md)). The registry of loops is its
generated view — one place lists every loop.

## The user's position

The user reads a run's outputs and looks below them often, as a
scientist samples and a manager checks in. Looking below is
what earns the claim of understanding. At the end of a run the user
reads the diff.

When the user does not like the result, the user changes the loop — a
contract, a detector, the runbook — and runs it again. The user does not
fix the output by hand.

A linear session is for work that does not repeat: a foundational
document, a decision. Work that repeats gets a loop.

Whether work repeats depends on the level one thinks at. This specific document
is written once, but many documents are written every week. Ask the
question one level up, then one level again, until the
repetition shows.

## The meta-loop

A loop improves by keeping a residual ledger: what the user's review
catches and the detectors missed becomes a row, with the detector that
now catches it.