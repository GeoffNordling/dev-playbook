---
type: General-Sheet
title: Reference Chain
description: The Reference chain, declared — a runbook's behavior and call signature as node types, edges, and rules
---

# Reference Chain

The **Reference chain** is one CLOA abstraction: the construction
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
rules for the runbook family. This file declares the object itself — its
node types, its edges, and its rules. The mechanics that construct a
chain from runbook prose — the primitive map, the grammar, the
rendering — sit one layer down in
[Encoding](/no-more-slop-branch-working-files/ENCODING.md). Same
working-file conventions as the branch plan sets out.

## The chain

A Reference chain is abstractions and the actions that connect them:
**nodes** joined by labeled **edges**, rooted at one runbook,
governed by a few **rules**.

The chain's origin: a runbook is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
contract. The Reference chain is that contract written down: the
signature (args in, reports out) plus the effects, in the coarse order
they fire. Not full fidelity — the chain is a collapse of the runbook's
program, and the fine-grained sequencing it drops stays below the CLOA.

## Nodes

Every edge lands on an abstraction; a **node** is how the chain draws
one. Provenance
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub, a
file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus, and the edge ends at
its boundary.

| Type     | What chains do with it | Where its declaration lives |
| -------- | ---------------------- | --------------------------- |
| Standard | reads                  | Its own noun and verbs, in [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs) |
| Agent    | does                   | Its own Reference chain     |
| Skill    | does                   | Its own Reference chain     |
| Script   | does                   | The code itself             |

- **Agent and Skill** differ in context binding: an agent runs in a
  fresh context window on its own permission set — a subprocess; a
  skill runs in the calling context on the caller's permissions — an
  in-process call. The steps inside either are its own program,
  file-level detail below the CLOA, never an interface.
- **Script** is deterministic code run via the shell, never a direct
  LLM call (usage-report's bundled `report.sh`). A script's own reads
  and writes hang under its node. A sibling **Workflow** noun was
  dropped — no recorded chain does one — and returns if a runbook
  ever does a workflow.

## Edges

- **does** — run a behavior a declared abstraction defines: the
  runbook where the doc is the definition, the code where the target
  is a Script.
- **reads** — consulted, not run.
- **overrides … with …** — substitute a clause in a runbook that cannot be
  edited.
- **writes** — produce or mutate state outside the chain. Targets are
  typed `bucket(refinement)`: a fixed bucket — git, GitHub, local
  file, local cache, scratch — plus an optional refinement, as in
  `git(commit, push)`. The bucket list stays fixed and lintable; the
  refinement is a memory aid, never a new type. Drawn form in
  [Encoding](/no-more-slop-branch-working-files/ENCODING.md#chain-rendering).
- **args** — the value the caller hands in at invocation; dies with
  the call. Declared by name alone — every arg is a string, so a type
  distinguishes nothing. Details in
  [Encoding](/no-more-slop-branch-working-files/ENCODING.md#the-primitive-map).
- **reports** — hand a value back to the caller, user and agent
  alike; dies with the call. Typed as well as named — commit reports
  `outcome: str` — because a report's type varies, so it carries
  information; a small enum is preferred. Declaration format in
  [Encoding](/no-more-slop-branch-working-files/ENCODING.md#the-primitive-map).

Any edge may carry a **condition** — what must hold for it to fire. A
conditional edge draws dashed and carries its condition; an unconditional edge
draws solid, and its trailing text is mere annotation. A call inside an
`if` is still a call edge; the condition never changes the edge's type.
The drawn form is in
[Encoding](/no-more-slop-branch-working-files/ENCODING.md#chain-rendering).

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Rules

- **Declared nodes are typed** by kind (Standard, Agent, Skill,
  Script); an imported node carries only its name.
  A node may also carry its permission expression and model pin as node
  data, quoted verbatim in the harness's own syntax —
  `allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
  paraphrased into prose.
- **Edges live at the definition site.** An edge belongs to the document
  whose text contains the instruction — greppable, so the assignment is
  lintable. A root's effects are the union of edges reachable along its
  does-path — the same rule as code, where a write belongs to the frame
  whose source contains the statement.
- **Tree, then graph.** Each runbook declares its own tree; the union across
  roots is the repo graph, where in-degree, hubs, and orphans appear. The
  code parallel is import-linter: a declared dependency contract that
  fails when reality disagrees. A lint-design candidate to evaluate when
  the checker is built: the ontology-guardrails idea
  (`~/workspace/mission-control/ideas/ontology-guardrails.md`) — declared
  rules enforced by a solver.

Remembered, not primitives:

- **Zoom.** A runbook collapses its internal files (containment is derivable
  from paths — `design/references/` sits under `design/`); zoomed in, they
  appear as nodes inside the runbook boundary with ordinary edges.
- **Doc type.** A read target's frontmatter type (Guide, General-Sheet)
  is noted informally; a type earns a noun only when it demonstrates a
  verb interface, the way Standard did.

## Acronyms

None.
