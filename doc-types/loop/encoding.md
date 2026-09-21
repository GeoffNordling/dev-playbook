---
type: General-Sheet
title: Acts, Checks, and Yields Encoding
description: The layer below the shape — how a Loop's file writes its graph, its acts, its checks, and its yields so a lint can read them, and where the file sits
---

# Acts, Checks, and Yields Encoding

The layer below
[the shape](/doc-types/loop/contract-shape.md): the form a Loop's file
takes so a lint reads every act, check, yield, and condition
deterministically, and where the file sits. The graph is the source of
truth; the prose around it carries only what a Mermaid label cannot,
the pointers and the conditions in full. Loop has no generated view: the graph GitHub renders is the view. What checks that
graph and prose agree is a lint, and the Standard that stations it is
[Loop Conventions](/standards/doc-type/loop-conventions.md).

## The graph

One fenced `mermaid` block, a `flowchart`. Every act, every check, and every yield is a node, and so is
every receiver a yield hands control to, the user or another loop.
Every edge label is a condition, written short; the entry under the
verb heading carries it in full. Node ids are free-form and unique
within the file; which verb a node is comes from the heading its entry
sits under, not from its id or its shape.

The edges follow the shape: a step leads to the next step; a yield
also leads out to its receiver, and only a yield does; a receiver leads
back to the step where the loop resumes.

## The verb sections

Three H2s after the graph, headed `Acts`, `Checks`, and `Yields`, in
that order. Each is one list with one entry per node of that verb, and
every node of that verb has one entry. An entry opens with the node id
in backticks, then an em dash, then the part of the shape the label
cannot carry:

- **An act** links the runbook it points at, a skill or an agent
  definition, then states its condition: `fires when …`, or `fires
  every iteration`.
- **A check** links the Standard it measures against, a file typed
  `Standard` at `standards/<name>/<topic>.md`, then states its
  condition the same way. What the check runs is the verifier of each
  of that Standard's rules, never a gate
  ([The verifier table](/standards/standard/detectors.md#the-verifier-table)).
- **A yield** names its receiver, the user or a linked Loop, then
  states its condition: `yields when …`.

## The paragraph

One paragraph between the H1 and the graph: what state the loop drives,
and toward what, named by the standards its checks point at. Nothing
else sits before the graph.

## Where a Loop lives

A Loop is `loops/<loop>.md`, typed `Loop`. The label's rule and its
lint are in
[definition.md](/doc-types/loop/definition.md#where-a-loop-lives).
