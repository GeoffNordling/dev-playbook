---
type: Workstream
title: Wall Workstream
description: The head file of the Wall child workstream — the deterministic wall, the typed boundary every exchange between the user and an agent crosses, out as typed reports and in as typed commands; its principles and what is to be considered
---

# Wall Workstream

The child workstream that holds the deterministic wall: the shared,
typed structure between the user and an agent. This workstream is
speculative. The wall has two directions. Out, the agent reports to the
user through it; in, the user instructs the agent through it. Both
directions cross the same declared types.

## Principles

### Out: typed reports

- **The deterministic wall.** The user gives an agent the goal in
  plain words, and the agent reports back only through a shared
  structure of declared types that the user understands. The wall
  makes the agent show, in the user's terms, what it does, so it
  cannot hide or blur its work. Telling an agent what to do is easy;
  getting back a structured answer the user can trust is the hard
  part, and the wall is the answer. The structure is not one format:
  reports of different kinds and explanatory tools are part of it.
- **Only deterministic code speaks through the wall.** The agent does
  not write what the user sees. To present an idea, it spends tokens
  only to call the CLOA structures through tooling, and deterministic
  code generates the presentation from them. What the user sees is
  therefore a strict subset of what the structural language can
  express: the doc-types, the CLOA, and the deterministic structure,
  a language the user understands and has approved in advance.
- **A shared language builds and changes the wall.** The user and the
  agent build the wall together, and every change to it is made in
  that one language.
- **The agent owns its side of the wall.** It works freely behind the
  wall, and it proposes changes to the wall's design only as explicit
  changes to the wall's rules. The user must understand a proposal
  before approving it. An approval is an expensive, important gate,
  and an approved change is the new way the two communicate.
- **The wall is frontier-invariant.** The guess: a more capable agent
  adapts to the user's language from its own side, so the wall holds
  however capable the agent on the other side becomes.

### In: typed commands

- **Typed commands, not "do the thing".** Every instruction to an
  agent is vibe coding. "Do the thing" is untyped vibe coding. "Run
  this named, typed Runbook on these objects" is typed vibe coding:
  the instruction stays conversational, but it lands on declared
  structure. Vibe coding and saying what a system does in each state
  are one problem, the problem of telling an AI to do things, and a
  typed command solves both. Vibe coding that builds deterministic
  structure is the winning formula.
- **Typing makes the system visible.** A command with typed inputs
  and outputs is a thing a view can draw, so the typing that tames
  vibe coding is also what lets the user see what the system does.

## Planned

To consider, not to carry out: nothing here is thought through yet.

- **Consider public contracts across idea space.** The ontology could
  isolate one part of the system, the wall could freeze that part's
  external contract, and an agent could then improve its internals
  freely, as a public API lets a library change inside.
