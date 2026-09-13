---
type: Standard-Ruleset
title: Loop Conventions
description: The form a document typed Loop takes — one paragraph, one Mermaid graph, and the Acts, Checks, and Yields sections that agree with it
population: "a document typed Loop"
---

# Loop Conventions

A document typed `Loop`, under `loops/`
([Document Types](/standards/knowledge-organization/document-types.md#typed-loop)).
The [Loop doc-type](/doc-types/loop/index.md) declares what a loop is and
the encoding its file takes,
[Acts, Checks, and Yields Encoding](/doc-types/loop/encoding.md); a
doc-type binds nobody, so this Standard is what binds the file to that
encoding. Every rule here is checked by `scripts/loop-lint`, and a rule
names the `knowledge-organization.*` id that checks it. The detector stops
at a file's first disagreement, since each rule reads the cut the one
before it made.

## One graph

The body is an H1, one paragraph, and one fenced `mermaid` block
holding a `flowchart`, in that order, with nothing else before the
fence (`knowledge-organization.loop-graph`).

The graph is the source of truth; the paragraph says what state the
loop drives and toward what. A second paragraph, a heading, or a
second graph before the verb sections fails the rule, as does a graph
the detector cannot read: a statement that is neither a node, an edge,
nor a Mermaid directive, or an `&` fan-out.

## Three verb sections

After the graph come three H2s, `Acts`, `Checks`, `Yields`, in that
order and no others, each holding one list whose every line is an
entry, the node id in backticks, an em dash, then the entry's text, each
id once (`knowledge-organization.loop-sections`).

An indented line continues the entry above it.

## Nodes and entries agree

Every entry names a node of the graph, and every node of the graph has
an entry or is a receiver, a node under no heading that some yield
leads to (`knowledge-organization.loop-nodes`).

## Edges follow the shape

An act leads to an act or a check; a check leads to a check or a yield;
a yield leads back to an act or out to a receiver; a receiver leads back
to an act (`knowledge-organization.loop-edges`).

This is the shape [Acts, Checks, and Yields](/doc-types/loop/contract-shape.md#the-graph)
draws: moves, then measurements, then the programmed exits, and control
coming back to the top.

## Entries point and condition

An act's entry links the runbook it runs; a check's entry links the
Audit cell of a card, `standards/<card>/card.md#audit`; a yield's entry
names the user or links a document typed `Loop`; and every entry states
its condition, `fires when …` or `fires every iteration` for an act or
a check, `yields when …` for a yield
(`knowledge-organization.loop-entries`).

A link is root-absolute or relative to the Loop's file, and it resolves
to a file in the repo. A check links the card's Audit cell and never the
Standard's own file: the cell composed is the audit, never the gate
([Standard](/doc-types/standard/encoding.md#cells)).
