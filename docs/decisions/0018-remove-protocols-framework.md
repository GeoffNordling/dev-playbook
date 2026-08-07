---
type: Decision-Record
title: Remove the Align-Map-Execute Protocol Framework
description: Remove the protocols/ tree, the Align, Map, Execute formulation and its companion skill, the improve-protocol meta-skill, and the Protocol document type — an attended-session construct the autonomous factory never used
date: 2026-08-06
---

# Remove the Align-Map-Execute Protocol Framework

## Context

A **protocol** was this playbook's name for an augmented skill built from two
halves. The **formulation** (`formulation.md`, carrying the `Protocol` document
type) was a pseudo-mathematical algorithm — deliberately pre-rigorous, its
objects too loose to support proofs — whose purpose was to let the reader step
back from a particular codebase and reason about the *workflow* instead: name
the objects, define their relationships, question the constraints. The
**skill** was a faithful plain-language translation of that algorithm, living
in its own dotfiles bundle, on the untested prior that pointing an executing
agent at the notation would divert its attention from the task. Protocols were
written to be *frontier-invariant*: they related abstract quantities — scope,
capability, step size — so that advancing model capability moved the operating
parameters rather than obsoleting the algorithm.

One protocol existed. **Align, Map, Execute** addressed the attended session in
which a task's scope exceeds what the user can hold in mind: the agent can
search that scope, but the user cannot evaluate raw results. It compressed the
task into a stream of user-sized decision points across staged phases — align
on intent, build a low-dimensional map, then execute — and persisted its whole
state in a `PROTOCOL_STATE.md` in the project repo so a fresh agent could
resume cold. Its primitives distinguished latent intent from the user-provided
objective, scope, facets, and references, and from the constructed alignment
and map; its operational quantities were the two context budgets, agent
capability, the quality threshold, the step size that bounds unobserved drift,
and an intent calibration log that turned each act of user direction into a
sample of intent. The map was a matrix: facets as columns, regions discovered
by surveying the scope as rows, each cell a *size estimate* rather than a
description. A third piece, the `improve-protocol` meta-skill, closed the loop
— it primed a session to feed observed agent behavior back into the pair, under
the rule that the formulation is authoritative and a divergence means the
instruction is wrong.

The framework was exercised and revised. Its README kept field notes: **V0**
concluded that the protocol prescribes little a competent user would not do
intuitively, and that its contribution is instead naming the objects so a
session becomes *improvable* — structure reduces variance. **V1** recorded that
the first execution produced a useless map because "organized according to the
alignment" was too free an instruction, and fixed it by promoting facets to a
separate primitive and defining the map as a matrix, which made the phase
handoff mechanical.

Two things date it. Its premise is an *attended* session — the scarce resource
is the user sitting there evaluating output, and every mechanism in it exists
to spend that attention well. The software factory inverted that premise:
nodes run unattended and the user meets the work at defined checkpoints, so the
per-step compression the protocol is built around has no place to attach. And
in practice nothing invoked it — no factory skill, standard, or workflow
referenced the protocol; its only inbound references at removal were the root
index row, the document-type registry row, and a test fixture that happened to
use its skill file as a classification example.

## Decision

Remove the whole framework: the `protocols/` tree, the companion skill bundle,
the `improve-protocol` meta-skill, and the `Protocol` document type. The
concept keeps its value as a way of thinking — this record exists so it can be
rebuilt rather than rediscovered — but it earns its place back by being needed,
not by being retained.

## Recovery

Everything removed was last alive on `main` at commit
`207a1bf64f4ce3a0df191e479c65609e87d91ec4`, the branch point of
`worktree-simplify`; the removal commit on that branch is
`Delete the protocols framework`. Recover any file with
`git show 207a1bf:<path>`. The exact paths:

- `protocols/index.md`
- `protocols/README.md` — the definition of a protocol, the
  frontier-invariance rule, and the V0/V1 field notes
- `protocols/align-map-execute/formulation.md` — the algorithm: primitives,
  artifact constraints, and the four stages
- `dotfiles/dot-claude/skills/protocol-align-map-execute/SKILL.md` — the
  plain-language translation an agent executed
- `dotfiles/dot-claude/skills/protocol-align-map-execute/references/protocol-state-document.md`
  — the `PROTOCOL_STATE.md` format
- `.claude/skills/improve-protocol/SKILL.md` — the meta-skill

Read the README first: it defines what the other files are for. The formulation
and the skill are a matched pair and only make sense together.

## Consequences

- `Protocol` is no longer a document type. An OKF document declaring it fails
  the type registry, so a reinstatement adds the row back before it adds the
  formulation.
- `PROTOCOL_STATE.md` has no producer. Any such file left in a project repo is
  now orphaned state that nothing reads or updates.
- Reinstating the framework means re-deciding it against the factory as it then
  stands, not restoring three files. The recovered text is a starting draft
  whose central premise — an attended session — has to be re-argued first.
