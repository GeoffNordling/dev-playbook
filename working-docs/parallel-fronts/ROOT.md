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

- **Experiment three.** Designed at the problem-table level, to be
  confirmed with the user and then run. Parts 1 to 3 use the stand-in agent
  and cost no tokens; part 4 uses real Claude briefly.
  1. *Booby-trap fix.* Build the approved fix into `front-clone`, and add a
     permanent test that plants a trap at every point and asserts none
     fires on `close`.
  2. *Option B.* Write our own container plug-in and run the stand-in
     through it. It must report the repository at
     `~/workspace/mission-control`, dev-playbook at
     `~/workspace/dev-playbook`, the repository name `mission-control`, and
     the skill and rule links resolving; experiment two's safety checks run
     again.
  3. *Option A.* Sandcastle's own podman plug-in, with dev-playbook at a
     fixed place of its own and the name read from the copy's clone note,
     the standards change made on this branch only. Same four reports, same
     safety checks.
  4. *Real Claude.* A tiny task on each option that passed: the agent has
     its skills and rules, its hook events reach the measurement database,
     and the billing check passes before launch.

  The output is, per option, whether it worked and what it costs: for B the
  plug-in's size, for A the standards that change. The user then chooses.
- **Two windows, one container.** Open dev-playbook twice for one front —
  read-only as the config source, read-write as the work checkout — and
  confirm an edit in one does not appear in the other and the front still
  loads its skills. This is the case where a front is assigned to change
  dev-playbook itself, which the prototype specified and never ran. It may
  fold into experiment three, part 2 or 3.
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
