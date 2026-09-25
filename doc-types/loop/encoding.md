---
type: General-Sheet
title: Acts, Verifications, and Yields Encoding
description: The layer below the shape — how a Loop's file writes its graph, its acts, its verifications, and its yields so a check can read them, and where the file sits
---

# Acts, Verifications, and Yields Encoding

The layer below
[the shape](/doc-types/loop/contract-shape.md): the form a Loop's file
takes so a check reads every act, verification, yield, and condition
deterministically, and where the file sits. The graph is the source of
truth; the prose around it carries only what a Mermaid label cannot,
the pointers and the conditions in full. Loop has no generated view: the graph GitHub renders is the view. The rules that the
graph and prose agree, and the checks that decide them, are in
[Loop Conventions](/standards/doc-type/loop-conventions.md).

## The graph

One fenced `mermaid` block, a `flowchart`. Every act, every verification, and every yield is a node, and so is
every receiver a yield hands control to: the user, the principal, or
another loop.
Every edge label is a condition, written short; the entry under the
verb heading carries it in full. Node ids are free-form and unique
within the file; which verb a node is comes from the heading its entry
sits under, not from its id or its shape.

The edges follow the shape: a step leads to the next step; a yield
also leads out to its receiver, and only a yield does; a receiver leads
back to the step where the loop resumes.

## The verb sections

Three H2s after the graph, headed `Acts`, `Verifications`, and
`Yields`, in that order. Each is one list with one entry per node of
that verb, and every node of that verb has one entry. An entry opens
with the node id in backticks, then an em dash, then the part of the
shape the label cannot carry:

- **An act** links the runbook it points at, a skill or an agent
  definition, then states its condition: `fires when …`, or `fires
  every iteration`.
- **A verification** links each Standard it measures against, one or
  more files typed `Standard` at `standards/<name>/<topic>.md`, then
  states its condition the same way. What the verification runs is the
  verifier of each of those Standards' rules, a check or a judge, never a gate
  ([Checks](/standards/standard/checks.md)).
- **A yield** names its receiver, the user, the principal, or a
  linked Loop, then
  states its condition: `yields when …`.

## The paragraph

One paragraph between the H1 and the graph: what state the loop drives,
and toward what, named by the standards its verifications point at.
Nothing else sits before the graph.

## Where a Loop lives

A Loop is `loops/<loop>.md`, typed `Loop`. The label's rule and its
check are in
[definition.md](/doc-types/loop/definition.md#where-a-loop-lives).
