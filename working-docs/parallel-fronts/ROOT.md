---
type: General-Sheet
title: Parallel Fronts Working Root
description: The root of the parallel-fronts set — the shape being built, how the agent works with the user on it, the words it uses, the open questions, and the worklist
---

# Parallel Fronts Working Root

This set is speculative: every member writes a guess as a guess, and every
member inherits that voice. The work is to find out whether one project can
be split into a few lines of work that agents advance in parallel, each on
its own branch, merged back at a point where the user takes stock. One
part is settled: the
[Sandcastle pipeline](/working-docs/parallel-fronts/pipeline.md), which
runs a single front safely, is built and proven. How fronts run together,
and what that gives the user, is still speculation.

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
- Sandcastle, if chosen, is never forked or patched
  ([The Sandbox](/working-docs/parallel-fronts/sandbox.md#constraints)).
- Every run happens on the Fedora machine
  ([The Sandbox](/working-docs/parallel-fronts/sandbox.md#constraints)).
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
- **Integrator** — the role that merges the fronts' branches at the end of
  a lap and reconciles what they conflict over. Unlike the driver, it
  judges.
- **Sandcastle pipeline** — the working arrangement that runs one front:
  throwaway copies go into a sealed container, one agent works there
  through Sandcastle and our plug-in, and only its commit comes back.
  [The Sandcastle Pipeline](/working-docs/parallel-fronts/pipeline.md)
  describes it.

Checkpoint and integrator are working names. What each is, and who fills
it, waits for the discussion of them in Planned.

The word *orchestrator* covers the driver and the integrator both, which is
why the set uses the two narrower names instead. The distinction is the one
that matters most here: the driver is a schedule and is reproducible, the
integrator is a judgment and is not.

## Open

None. Every question the set has met is carried by an item in Planned,
and is answered there.

## Planned

Sessions with the user come first, each at a high level, the agent
guiding.

- **Discuss: what this gives the user, and how they run it.** When this branch lands
  on main, what does the user gain, and does it change any way work is done
  on main today? Rule what the landing PR carries: only the two changes
  part 4 ran on, or all of this branch's work (the hardened `front-clone`,
  its trap test, and this working set) with them, whether anything of
  the `sandbox-probe` branch comes along, and where the pipeline's pieces
  that now live only in the session scratchpad are kept
  ([Where each piece lives](/working-docs/parallel-fronts/pipeline.md#where-each-piece-lives)). Then step back further: so far
  the work proved Sandcastle's sandbox can be made safe, but sandboxing is
  not the library's point. It coordinates agents across branches and
  worktrees. Define the question first, what value parallel fronts should
  deliver and how the user wants to run them, before choosing any tool to
  run them with. [Sandcastle](/working-docs/parallel-fronts/sandcastle.md)
  records what one candidate offers. The answer also settles what the
  pipeline does not yet do
  ([The Sandcastle Pipeline](/working-docs/parallel-fronts/pipeline.md#what-it-does-not-yet-do)):
  running fronts together, where real copies live, and what removes a
  stranded container.
- **Discuss: the checkpoint and the integrator.** What happens at the end
  of a lap: who merges the fronts' branches (the user, an agent, or both),
  and who revises a front's plan when the fronts disagree. Also settle the
  name "checkpoint", which the repo's shared glossary already uses for the
  Ralph loop.
- **Discuss: overlap with active branches.** Does the landing PR touch any
  file that another active, unmerged branch is also changing?
- **Land the sandbox changes on main.** Part 4 ran on two dev-playbook
  changes that exist only in a throwaway config copy
  ([What part 4 settled](/working-docs/parallel-fronts/sandbox.md#what-part-4-settled)):
  `measure-event` sending rows to the host from a sandbox, and the Stop and
  SessionEnd hooks set to wait. All five problems in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-five-problems)
  are solved in test; this is the last step to make them solved for real.
- **One lap by hand.** Run the shape once with two fronts and no driver
  program at all, to find where it hurts before any of it is automated.
  The lap tests what the checkpoint discussion decided, and answers
  whether a front converges or finishes its useful work and then invents
  more. The guess: a front needs a way to declare itself done, and its
  budget is a ceiling, not a target.

## Completed

- **Survey Sandcastle.** What the tool offers this shape is recorded in
  [Sandcastle](/working-docs/parallel-fronts/sandcastle.md).
- **State the sandbox requirement.** What a front's container must reach,
  and where Sandcastle collides with it, is recorded in
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md).
- **Assert this device holds no metered credential.** `billing-lint`
  asserts it at the commit gate, stationed by the
  [Billing](/standards/billing/card.md) card, and
  [The Sandbox](/working-docs/parallel-fronts/sandbox.md#constraints)
  records what it reads and the assertion still waiting on the driver.
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
- **Walk the user through the Sandcastle pipeline.** The user saw the
  copies, the plug-in, the round trip, and the hook logging, and named the
  arrangement. A front assigned to change dev-playbook keeps both copies:
  the read-only config copy answers "what does published main say", so the
  front's own unfinished edits never change the rules it runs under
  ([The Sandbox](/working-docs/parallel-fronts/sandbox.md#the-two-windows-that-matter)).

## Acronyms

None.
