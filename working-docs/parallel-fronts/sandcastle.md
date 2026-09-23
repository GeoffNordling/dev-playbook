---
type: Survey
title: Sandcastle
description: What Sandcastle offers the parallel-fronts shape — the driver primitives it supplies, what it leaves to the user, and what it does not cover
---

# Sandcastle

Sandcastle is one candidate for the driver
([Parallel Fronts Working Root](/working-docs/parallel-fronts/ROOT.md#terms)).
This member records what the tool supplies to the shape and what it leaves
undone, so the choice between it and a smaller script rests on something
written rather than on first impressions. The findings come from the
project's own documentation at <https://github.com/mattpocock/sandcastle>.

## What it is

A TypeScript library, not a command-line tool driven by hand. Its own
README describes a programmatic `run()` function "for use in scripts, CI
pipelines, or custom tooling", and each agent invocation is a function call
inside a program the user writes. The consequence for this set is that a
lap is ordinary code: a list of fronts, a fan-out, a wait, a merge step.
The driver is a file, and it is read and revised like any other file.

The library takes no position on the work itself. Its README states that
the user writes the prompt "and the engine executes it — no opinions about
workflow, task management, or context sources are imposed."

## What it gives the shape

Four of its primitives map onto terms this set already has.

**A branch per front.** A run is configured with a branch strategy, and
the named-branch strategy puts a front's commits on a branch the caller
chooses. The fronts of one lap are then a list of names the driver holds.

**A fan-out that the language already supplies.** Because a run is a
function call that returns a value, running the fronts at once is the
standard JavaScript idiom for "do these together and wait for all". No
feature of the library is involved, which is a point in its favor: the
concurrency is the language's and is therefore familiar and debuggable.

**A typed handoff between agents.** A run can be told to extract a
schema-validated payload from the agent's output. This is what lets one
agent's answer become the next step's input without the user reading it in
between. A planning agent that emits a list of fronts, and a driver that
fans out over that list, is the library's own worked example.

**A commit count per front.** A run returns the commits it produced, so
the driver can tell a front that did work from one that did not, and give
the integrator only the branches worth merging.

## What it leaves to the user

The library has no notion of a checkpoint. A driver program runs to
completion and exits; it cannot stop and ask the user a question. For this
set that is close to a feature rather than a gap, because the checkpoint is
the user's own session between two runs of the driver, and the exit is what
makes the seam visible. The guess is that this matches the shape well, and
it is the first thing a hand-run lap should test.

It also has no notion of a front's plan surviving a lap. Revising what a
front works on next is outside the library entirely.

## Its container

The library's headline concern is sandbox isolation: it runs each agent in
a container and merges the commits back out. This set does want every
front in a container, but not on the window layout Sandcastle chooses,
which opens the real repository to the front.
[The Sandbox](/working-docs/parallel-fronts/sandbox.md#where-sandcastle-collides)
records the collision and the guess at a resolution. The tool also offers
a no-sandbox provider that runs the agent directly on the host; this set
does not use it.

## What it fixes, and where it bends

Read from the published package, version 0.12.0, and partly confirmed by
experiment two
([The Sandbox](/working-docs/parallel-fronts/sandbox.md#what-the-sandcastle-run-settled)).

**Fixed.** The repository always lands at `/home/agent/workspace` inside
the container, and the podman plug-in always sets the agent's home to
`/home/agent`. No option changes either. This is the source of the
workspace collision.

**Bends.** The host repository is chosen per run (`cwd`), which is how a
run is pointed at a throwaway copy. Extra read-only or read-write mounts
are declared per plug-in. The agent is a plug-in too: any object that turns
a prompt into a shell command, which is how experiment two ran a stand-in
with no tokens. And the sandbox itself is a plug-in: the library exports
the builder its own podman and docker plug-ins are made from, so a plug-in
of ours is a supported extension rather than a fork.

**Branch modes.** `head` runs the agent directly in the repository it is
pointed at, and is the mode that fits a throwaway copy. `branch` and
`merge-to-head` add a worktree of their own, and run more git on the host.

## Acronyms

- **CI** — Continuous Integration.
