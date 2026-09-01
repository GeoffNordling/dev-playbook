---
type: General-Sheet
title: Reference Chain
description: The Reference chain — Runbook's contract shape, declared as nodes and edges
---

# Reference Chain

The **Reference chain** is Runbook's contract shape
([Doc-Type](/doc-types/doc-type.md)): the
form every runbook's contract takes. This file declares the shape —
its nodes and its edges. How chain edges are written inside runbook
prose sits one layer down in
[encoding.md](/doc-types/runbook/encoding.md).

## The chain

A Reference chain is **nodes** joined by labeled **edges**, rooted
at one runbook
([definition.md](/doc-types/runbook/definition.md)).
It is the contract written down: the signature — args in, reports
out — plus the effects, in the coarse order they fire. The chain is
a collapse of the runbook's program: the fine-grained sequencing it
drops stays below the CLOA, in the instance's body.

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([System Legibility](/docs/system-legibility.md))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub,
a file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | read                   | —           | The Standard doc-type ([Doc-Type System](/doc-types/doc-type-system.md)) |
| Agent    | do                     | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | do                     | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | do                     | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under
its node.

## Edges

An edge is one of Runbook's operations, applied: a base verb
connecting the runbook to a node. A rendered chain inflects the verb
to the third person (`reads`, `writes`), and the encoding's span
keywords are its imperative form.

Edges live at the definition site: an edge belongs to the file whose
text declares it, and a chain is stitched by following do-edges into
each target's own declarations — no file describes another file's
behavior.

| Operation | The action | Detail |
| --------- | ---------- | ------ |
| read | consult | — |
| write | change state | target is one of four buckets — `git(commit, push)` |
| do | run a runbook or a script | — |
| override … with … | substitute a previous clause | — |
| never … | prohibit | wraps one write and flips it from action to ban |
| args | take the caller's input | by name — `friction` |
| report | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type. A read's target is a file, or one of two read
buckets when no on-disk target exists — GitHub for remote state, the
launch prompt for material the caller assigns at dispatch. A never
wraps one write; a git-bucket ban may also name `merge`, a verb that
exists only inside a prohibition.

This vocabulary is closed: the tables above are all of it. A new
operation, node type, or bucket is an edit here before its first
use; its written form is an edit to
[encoding.md](/doc-types/runbook/encoding.md).

How each edge is written in runbook prose is ruled in
[encoding.md](/doc-types/runbook/encoding.md#the-primitive-map),
and how it draws in
[encoding.md](/doc-types/runbook/encoding.md).

Any edge may carry a **condition** — what must hold for it to fire.
A conditional edge draws dashed; an unconditional edge draws solid.
The condition never changes the edge's operation.

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in
[residual-ledger.md](/doc-types/runbook/residual-ledger.md).

## Acronyms

- **CLOA** — Correct Level of Abstraction.
