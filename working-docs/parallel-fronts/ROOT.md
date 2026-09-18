---
type: General-Sheet
title: Parallel Fronts Working Root
description: The root of the parallel-fronts set — the shape being prototyped, the words it uses, the open questions, and the worklist
---

# Parallel Fronts Working Root

This set is speculative: every member writes a guess as a guess, and every
member inherits that voice. The work is to find out whether one project can
be split into a few lines of work that agents advance in parallel, each on
its own branch, merged back at a point where the user takes stock. Nothing
here is settled.

## Goal

A project advances on two to four fronts at once. Each front runs its own
agent against its own plan on its own branch, all of them starting from one
commit. At the end of a lap the branches come back together, and the user
reads what landed before the next lap starts. The work runs over many laps,
and no single lap is expected to produce a result fit for `main`.

The point is delegation with the user still in charge: the agents hold the
inner loop, the user holds every seam between laps.

## Constraints

- The user aligns at every checkpoint. No lap reaches `main` unattended.
- A lap starts from one commit and ends at one commit, so the fronts always
  have a shared base to diverge from and return to.
- A front's scope is set before the lap starts, not discovered during it.
- Between two and four fronts. Below two the shape has no purpose; above
  four the user cannot hold the merge in their head.
- Every front reads dev-playbook at published state, whichever repository
  it is assigned to change, and a front may be assigned to change a
  dev-playbook branch at the same time. Both facts hold together, and
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md) is where the
  arrangement that serves them is worked out.

## Terms

The words of the set, one meaning each.

- **Front** — one line of work that advances on its own branch from the
  lap's base commit, with its own scope and its own plan.
- **Lap** — one cycle of the shape: fan out to the fronts, let each
  iterate, merge them back, stop. The work is a sequence of laps.
- **Checkpoint** — the end of a lap, where the driver stops and the user
  takes stock before deciding what the next lap contains.
- **Driver** — the deterministic program that schedules a lap: which
  fronts run, from what base, with which prompt, and when the lap ends. It
  makes no judgment about the code the fronts produce.
- **Integrator** — the agent that merges the fronts' branches at the end of
  a lap and reconciles what they conflict over. Unlike the driver, it
  judges.

The word *orchestrator* covers the driver and the integrator both, which is
why the set uses the two narrower names instead. The distinction is the one
that matters most here: the driver is a schedule and is reproducible, the
integrator is a judgment and is not.

## Open

- **Whether a front converges.** A front given a budget of iterations may
  finish its useful work early and then invent more. The guess is that a
  front needs a way to declare itself done that the driver can read, and
  that the budget is a ceiling rather than a target. Untested.
- **Who integrates.** The integrator may be an agent, or it may be the
  user with an agent assisting. The guess is that the first few laps are
  integrated by hand, because that is where the shape's real failure modes
  show.
- **How a front's plan is revised.** A lap ends with three or four
  divergent views of the project. Which of them updates the other fronts'
  plans, and whether that is the user's act or the integrator's, is
  unsettled.
- **What drives the laps.** [Sandcastle](/working-docs/parallel-fronts/sandcastle.md)
  is one candidate. Whether it earns its weight against a smaller script is
  the question that member exists to inform.
- **Whether the fence holds.** The arrangement in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md) is read from
  Sandcastle's source and has not been run. That member carries its own
  Open bucket, and every item in it is a guess awaiting a test.

## Planned

- **Experiment one: the clone round-trip.** Find out where a front's
  commits land when Sandcastle runs against a throwaway clone, and whether
  the host can move them into the real repository afterwards. Runs on a
  scratch repository with one front and no container, so a failure points
  at the git model rather than at the fence.
- **One lap by hand.** Run the shape once with two fronts and no driver
  program at all, to find where it hurts before any of it is automated.
- **Decide the driver.** Choose between Sandcastle and a smaller script,
  against what the hand-run lap shows.

## Completed

- **Survey Sandcastle.** What the tool offers this shape is recorded in
  [Sandcastle](/working-docs/parallel-fronts/sandcastle.md).
- **State the sandbox requirement.** What a front's container must reach,
  and where Sandcastle collides with it, is recorded in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md).
- **Assert this device holds no metered credential.** `billing-lint` reads
  four surfaces and refuses rather than reports, and the
  [Billing](/standards/billing/card.md) card stations it at the commit
  gate. The same assertion immediately before a container launches waits on
  the driver, since there is nothing yet to carry it.

## Acronyms

None.
