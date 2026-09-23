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
- Every run needs a container, so every run happens on the Fedora machine.
  The WSL machine this set was begun on has no container runtime and is
  not a target.
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
  All five are solved and proven in test. **Hook logging**'s fix is not
  yet on main.

- **What the landing PR carries.** For the user to rule before any PR
  opens: only the two changes part 4 ran on, or all of this branch's work
  (the hardened `front-clone`, its trap test, and this working set) with
  them, and whether anything of the `sandbox-probe` branch comes along.
- **Why a dev-playbook front needs two copies.** The user questions whether
  a front assigned to change dev-playbook needs a read-only config copy
  beside its work copy at all. The prototype's reason is recorded in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-two-windows-that-matter):
  the config copy answers "what does published main say", so it must not
  show the front its own uncommitted edits. Parked until part 4 worked;
  now due to be revisited together.

## Planned

- **Land the sandbox changes on main.** Part 4 ran on two dev-playbook
  changes that exist only in a throwaway config copy
  ([What part 4 settled](/working-docs/parallel-fronts/sandbox.md#what-part-4-settled)):
  `measure-event` sending rows to the host from a sandbox, and the Stop and
  SessionEnd hooks set to wait. The PR's scope is open above.
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
- **Experiment three, part 1: the booby-trap fix.** `front-clone close`
  never runs git in a copy, and a permanent test plants a trigger at every
  point git offers and asserts none fires.
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-booby-trap-fix)
  records how.
- **Experiment three, part 2: option B.** A 20-line wrapper around
  Sandcastle's podman plug-in closes the **Workspace collision** with no
  fork and no standards change, proven with the stand-in on a
  mission-control front and a dev-playbook front. The user then chose one
  layout for every front, work copy at `~/assignment/<repo>`.
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#what-experiment-three-settled)
  records the run.
- **Experiment three, part 4: real Claude end to end.** Real Claude, on the
  subscription, did a tiny task in a front through Sandcastle and the
  option B plug-in. Billing, config, and the commit's return passed at once;
  hook logging passed once the two end-of-session hooks were set to wait.
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#what-part-4-settled)
  records the run. The rig is throwaway, in the session scratchpad under
  `exp3/` (`part4.mjs` and `receiver.py` beside parts 1 and 2's files).

## Acronyms

None.
