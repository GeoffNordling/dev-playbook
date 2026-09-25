---
type: General-Sheet
title: Deterministic Separation
description: Deterministic separation of a stochastic chain, one predicate at a time — a verifier as a containment boundary, a predicate's tail as the stochastic steps after its last check, and the tail as a query over the fact base
---

# Deterministic Separation

The record of one topic from a synthesis session on 2026-09-14: whether
parts of the system can be provably separated under determinism, so
that the worst case of stacked stochasticity is bounded. Speculative,
per [Fact Base Workstream](/workstreams/system/see/fact-base/WORKSTREAM.md).
The answer is well-formed once stated per
[predicate](/CONTEXT.md#specification)
rather than per system, and the provable part is a query over the fact
base, which is why this page sits in this child workstream as a planned view.

## Terms

Predicate, rule, verifier, check, judge, fact base, and view are the
repo's words ([CONTEXT.md](/CONTEXT.md)); a deterministic rule is one a
check decides, and a stochastic rule one a judge decides.

## One predicate at a time

Take one predicate P over the final state. Each stochastic step has
some probability of breaking P, and along a chain those compound: the
chance P survives is a product, and the tail grows with chain length.
A deterministic verifier of P at step k is a containment boundary:
everything downstream runs conditional on P holding, so P's violation
probability at the end depends only on the stochastic steps after k.
Predicates nobody verifies compound across the whole chain. The
system's worst case is one number per predicate: the compounded error
of the stochastic steps after that predicate's last deterministic
check. Stochastic rules are the ones whose tails still run the length
of the chain.

## Miniature

Runbook A, a model, writes `data.json`. Script S reads it, transforms
it to `out.json`, and fails loud on malformed input. Runbook B, a
model, reads `out.json` and writes a report.

- "out.json is well-formed": S verifies it, A is contained, B does not
  write the file. Effectively deterministic.
- "the report cites every record in out.json": nobody verifies it. A
  can drop a record and S passes it through; B can miss one. Tail
  length two, compounding.

A script that diffs the report's citations against `out.json` after B
drops the second predicate's tail to zero.

## The tail as a query

The provable part is a graph question: for each rule id, which
stochastic nodes lie between its last verifier and the end. That is a
query over the fact base, and it is deterministic. The probabilities
stay estimates; the structure that bounds them is proven. This and
"the target is a ruleset of predicates" are one question: every rule
given a script verifier shortens its own tail to the segment after its
gate. Whether the query is a view over the fact base in the registry's
sense or a query beside it is the open part, carried in the child
workstream's [Planned](/workstreams/system/see/fact-base/WORKSTREAM.md#planned).
