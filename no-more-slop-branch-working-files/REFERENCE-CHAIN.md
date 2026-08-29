---
type: General-Sheet
title: Reference Chain
description: The Reference chain, declared — a runbook's behavior and call signature as nodes and edges
---

# Reference Chain

The **Reference chain** is one CLOA abstraction: the construction
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
rules for the runbook family. This file declares the object itself — its
nodes and its edges. The mechanics that construct a
chain from runbook prose — the primitive map, the grammar, the
rendering — sit one layer down in
[Encoding](/no-more-slop-branch-working-files/ENCODING.md). Same
working-file conventions as the branch plan sets out.

## The chain

A Reference chain is abstractions and the actions that connect them:
**nodes** joined by labeled **edges**, rooted at one runbook.

The chain's origin: a runbook is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
contract. The Reference chain is that contract written down: the
signature (args in, reports out) plus the effects, in the coarse order
they fire. Not full fidelity — the chain is a collapse of the runbook's
program, and the fine-grained sequencing it drops stays below the CLOA.

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub, a
file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | reads                  | —           | Its own noun and verbs, in [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs) |
| Agent    | does                   | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | does                   | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | does                   | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under its
node.

## Edges

An edge is an action. The six labels:

| Label | The action | Detail |
| ----- | ---------- | ------ |
| does | run a runbook or a script | — |
| reads | consult | — |
| overrides … with … | substitute a previous clause | — |
| writes | change state | target is one of four buckets — `git(commit, push)` |
| args | take the caller's input | by name — `friction` |
| reports | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type.

How each edge is written in runbook prose is ruled in
[Encoding](/no-more-slop-branch-working-files/ENCODING.md#the-primitive-map),
and how it draws in
[Encoding](/no-more-slop-branch-working-files/ENCODING.md#the-code).

Any edge may carry a **condition** — what must hold for it to fire. A
conditional edge draws dashed; an unconditional edge draws solid. The
condition never changes the edge's type.

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Acronyms

None.
