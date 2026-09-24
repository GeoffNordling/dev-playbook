---
type: Standard
title: Loop Conventions
description: The form a document typed Loop takes — one paragraph, one Mermaid graph, and the Acts, Verifications, and Yields sections that agree with it
population: "a document typed Loop, outside a working documentation set"
---

# Loop Conventions

A document typed `Loop`, under `loops/` and outside a working
documentation set
([Document Types](/standards/knowledge-organization/document-types.md#loop-lives-under-loops)).
The [Loop doc-type](/doc-types/loop/index.md) declares what a loop is and
the encoding its file takes,
[Acts, Verifications, and Yields Encoding](/doc-types/loop/encoding.md); a
doc-type binds nobody, so this Standard is what binds the file to that
encoding.

> **Why.** The graph is the source of truth; the paragraph before it
> says what state the loop drives and toward what.

## One paragraph, then one graph

A file typed `Loop` has, after its front matter, one H1, then one
paragraph, then one fenced `mermaid` block, and nothing else before
the fence. The first line in the block is `flowchart` or `graph`.
Every other line is a Mermaid directive, a node, or an edge between
nodes, and no line uses `&`.

`doc-type.one-paragraph-then-one-graph` · deterministic

## The paragraph names state and target

In a document typed `Loop`, the paragraph before the graph names the
state the loop drives and the target state it drives that state toward.

`doc-type.the-paragraph-names-state-and-target` · stochastic

## Acts, Verifications, and Yields, in that order

After the graph there are exactly three H2s, `Acts`,
`Verifications`, and `Yields`, in that order, and nothing between the
graph and `## Acts`. Under each H2 there is one list. Each line of the
list is an entry, `` - `<node id>` — <text> ``, or an indented line
that continues the entry above it. No node id has two entries.

`doc-type.acts-verifications-and-yields-in-that-order` · deterministic

## Nodes and entries agree

In a file typed `Loop`, the node id of every entry is a node of the
graph. Every node of the graph has an entry, or has no entry and is
the target of an edge from a yield. A node of the second kind is a
receiver.

`doc-type.nodes-and-entries-agree` · deterministic

## Edges lead to steps

In a document typed `Loop`, every edge of the graph leads to a step, a
node whose entry is an act, a verification, or a yield, except an edge out of a
yield, which leads to a step or to a receiver, a node with no entry.

`doc-type.edges-lead-to-steps` · deterministic

## Every entry states its condition

Every entry of a file typed `Loop` contains `fires when` or
`fires every iteration` if it is an act or a verification, and
`yields when` if it is a yield. An act's entry has at least one
link. A verification's entry has a link to a file typed `Standard`. A
yield's entry has a link or the words `the user` or `the principal`,
and each of its links goes to a file typed `Loop`. Every link in an entry is
root-absolute or relative to the file, and goes to a file that
exists in the repo.

`doc-type.every-entry-states-its-condition` · deterministic

## An act links a runbook

An act's entry has a link to a runbook: a file
`<skills root>/<name>/SKILL.md` or `<agents root>/<name>.md`, where
the roots are those that
[Every runbook at a fixed path](/standards/harness/files.md#every-runbook-at-a-fixed-path)
names.

`doc-type.an-act-links-a-runbook` · deterministic
