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
- Sandcastle, if chosen, is used as published and never forked or
  patched. A mismatch is closed by a plug-in Sandcastle accepts, or by
  changing the workspace standards.
- Past decisions do not bind this set. A decision record that stands in the
  way is revised rather than worked around.

## Working with the user

The user holds the requirements and the approvals; the agent holds the
technical detail. Report at the level of the problem table in
[The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-five-problems):
plain language, each problem and solution by its name, a concrete picture
where one helps, such as a directory tree with enough rows to show what the
files are. Leave out commands, flags, and mechanism unless the user asks.
Describe a test plan and get approval before running it, and discuss results
before acting on them.

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
- **Whether the fence holds.** Five named problems stand between Sandcastle
  and a safe front, tracked in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-five-problems).
  Two are solved and proven; three are not.

## Planned

Every run below needs a container, so every run happens on the Fedora
machine. The WSL machine this set was begun on has no container runtime and
is not a target, which
[The Sandbox](/working-docs/parallel-fronts/sandbox.md) records as settled.

- **Experiment three.** Approved by the user, in progress. Parts 1 and 2
  use the stand-in agent and cost no tokens; part 4 uses real Claude
  briefly.
  1. *Booby-trap fix.* Done: see
     [The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-booby-trap-fix).
  2. *Option B.* Our own container plug-in, a thin wrapper around
     Sandcastle's podman plug-in, run with the stand-in. Six checks: the
     name reads `mission-control`; dev-playbook sits at
     `~/workspace/dev-playbook` and the eight links resolve; the real
     repository and unpushed work are untouched; the commit comes back at
     the same SHA; the planted traps do not fire; and **two windows, one
     container** — a front assigned to change dev-playbook gets a
     read-only copy to read from and a copy to edit, and an edit to one
     does not appear in the other. The last is the check most likely to
     break option B, since both copies want `~/workspace/dev-playbook`.
  3. *Option A.* Only if option B fails. The user ruled it the fallback:
     code also runs outside Sandcastle, so a standards change would cascade
     into workflows beyond this set.
  4. *Real Claude.* An end-to-end proof on the option that passed: a tiny
     real task, with the billing check passing before launch, the skills
     and rules loaded, and hook events reaching the measurement database.
- **Sandcastle's other branch modes.** `branch` and `merge-to-head` run more
  git on the host than `head` mode, and may trip the booby trap themselves.
- **One lap by hand.** Run the shape once with two fronts and no driver
  program at all, to find where it hurts before any of it is automated.
- **Decide the driver.** Choose between Sandcastle and a smaller script,
  against what the runs above show.

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
- **Experiment one: the clone round-trip.** A front's commits are made in a
  throwaway clone and reach the real repository at the same SHA, or the lap
  stops. [`front-clone`](/scripts/front-clone) is the plumbing, and
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md) records the four
  things the run settled. It used no container and no driver, so what it
  settled is git's behavior alone.
- **Experiment two: Sandcastle against a copy.** Sandcastle, pointed at a
  `front-clone` copy with a misbehaving stand-in agent, left the real
  repository and the user's unpushed work untouched, and the commit came
  back. It proved the throwaway copy solves **Shared history** and
  **Relabel**, and exposed the **Workspace collision** and the **Booby
  trap**. [The Sandbox](/working-docs/parallel-fronts/sandbox.md#what-the-sandcastle-run-settled)
  records the details.

## Acronyms

None.
