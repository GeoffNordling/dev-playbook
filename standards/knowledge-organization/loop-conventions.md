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
encoding.

## One graph

A document typed `Loop` holds one H1, then one paragraph, then one
fenced `mermaid` block, in that order and with nothing else before the
fence. The block is a flowchart, opening `flowchart` or `graph`, whose
statements are Mermaid directives, nodes, and edges between nodes, with
no `&` fan-out.

`knowledge-organization.one-graph` · deterministic

## What the paragraph says

In a document typed `Loop`, the paragraph before the graph names the
state the loop drives and the target state it drives that state toward.

`knowledge-organization.what-the-paragraph-says` · stochastic

## Three verb sections

After the graph, a document typed `Loop` holds three H2s, `Acts`,
`Checks`, and `Yields`, in that order and no others, with nothing
between the graph and the first of them. Each H2 holds one list whose
every line is an entry, the node id in backticks, an em dash, then the
entry's text, or is a line indented under an entry, which continues it;
and no node id carries two entries.

`knowledge-organization.three-verb-sections` · deterministic

## Nodes and entries agree

Every entry of a document typed `Loop` names a node of its graph, and
every node of the graph carries an entry or is a receiver, a node with
no entry that an edge out of a yield leads to.

`knowledge-organization.nodes-and-entries-agree` · deterministic

## Edges follow the shape

In a document typed `Loop`, every edge of the graph leads to a step, a
node whose entry is an act, a check, or a yield, except an edge out of a
yield, which leads to a step or to a receiver, a node with no entry.

`knowledge-organization.edges-follow-the-shape` · deterministic

## Entries point and condition

Every entry of a document typed `Loop` states its condition, `fires
when …` or `fires every iteration` for an act or a check and `yields
when …` for a yield. An act's entry holds at least one link; a check's
entry links a document typed `Standard-Card` at its `audit` fragment; a
yield's entry holds a link or the words `the user`, and every link it
holds names a document typed `Loop`. Every link in an entry is
root-absolute or relative to the document, and it resolves to a file in
the repo.

`knowledge-organization.entries-point-and-condition` · deterministic

## An act links a runbook

The link an act's entry holds names a runbook, a skill bundle's
`SKILL.md` or an agent definition
([Runbook Conventions](/standards/harness/runbook-conventions.md#location)).

`knowledge-organization.an-act-links-a-runbook` · deterministic
