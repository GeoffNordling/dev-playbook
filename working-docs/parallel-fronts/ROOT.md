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
runs fronts safely and in parallel, is built and proven. How laps are run
with it, and what that gives the user, is still speculation.

## Goal

A project advances on two to four fronts at once. Each front runs its own
agent against its own plan on its own branch, all of them starting from one
commit. At the end of a lap the branches come back together, and the user
reads what landed before the next lap starts. The work runs over many laps,
and no single lap is expected to produce a result fit for `main`.

The point is delegation with the user still in charge: the agents hold the
inner loop, the user holds every seam between laps.

## Principles

- Bias for simplicity: take the simpler way until a more complex one
  proves its need.
- Past decisions do not bind this set. A decision record that stands in the
  way is revised rather than worked around.

## Constraints

- The user aligns at every checkpoint. No lap reaches `main` unattended.
- A lap starts from one commit and ends at one commit, so the fronts always
  have a shared base to diverge from and return to.
- A front's scope is set before the lap starts, not discovered during it.
- Between two and four fronts. Below two the shape has no purpose; above
  four the user cannot hold the merge in their head.
- Every front reads dev-playbook at published `main`, whichever repository
  it is assigned to change. A front assigned to change dev-playbook reads
  the standards as published while it writes their replacement; its own
  edits reach a later lap. Refreshing the config between laps, or letting
  such a front read its own branch as config, was declined.
- Every run happens on the Fedora machine, and nowhere else. The container,
  its image, and the `claude` binary inside it are Fedora. The WSL Ubuntu
  machine has no container runtime and is not a target: a result measured
  there does not count, and no effort goes to making the set portable.
- The subscription pays for every run, and this is asserted, not assumed.
  The billing checks of `playbook check` read four places for a metered credential: the live
  environment, the shell startup files, `~/.claude/settings.json`, and the
  repository's `.claude/settings.json`. It runs at the commit gate and again
  before every run.
- A container never mounts a real file, only copies made for the run and
  deleted after it. Podman's SELinux option permanently relabels whatever
  is mounted, even read-only, and a host program can then be refused its
  own file.
- No front reaches GitHub. The container holds no GitHub credential, so
  only local git works inside it, and whatever pushes a front's commits
  does so outside.
- The user's hooks keep logging every event to the measurement database
  from inside a container.
- Sandcastle is never forked or patched. It is used as published, through
  the plug-ins it accepts, since a fork would need maintaining for as long
  as the set uses it.

## Working with the user

The user holds the requirements and the approvals; the agent holds the
technical detail. Report at the level of the problem table in
[What it guarantees](/working-docs/parallel-fronts/pipeline.md#what-it-guarantees):
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
- **Sandcastle pipeline** — the working arrangement that runs fronts in
  parallel: for each front, throwaway copies go into a sealed container,
  one agent works there through Sandcastle and our plug-in, and only its
  commit comes back.
  [The Sandcastle Pipeline](/working-docs/parallel-fronts/pipeline.md)
  describes it.

Checkpoint and integrator are working names. What each is, and who fills
it, waits for the control-code design in Planned.

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

- **Wait: overlap with active branches.** Paused: a large refactor is
  in progress on `main`, and this set waits for it to finish. Then check
  what it changed, and whether the landing PR touches any file that
  another active, unmerged branch is also changing.
- **Design the invocation and the control code.** How the user starts a
  lap, the program around `run()` that decides what runs and when, and
  what happens at the lap's end: who merges the fronts' branches (the
  user, an agent, or both), and who revises a front's plan when the fronts
  disagree. This settles what the pipeline does not yet do
  ([The Sandcastle Pipeline](/working-docs/parallel-fronts/pipeline.md#what-it-does-not-yet-do)):
  what schedules a lap, and where real copies live. It also settles the
  names checkpoint and integrator; "checkpoint" is already used in the
  repo's shared glossary for the Ralph loop. Waits on the overlap
  discussion above.
- **Discuss: where the pipeline lives on main.** Where its document and
  the code in [`rig/`](/working-docs/parallel-fronts/rig/index.md) go once
  the work lands, and what the landing PR carries: only the two changes
  part 4 ran on, or all of this branch's work (the hardened `front-clone`,
  its trap test, and this working set) with them, and whether anything of
  the `sandbox-probe` branch comes along. Waits until the large refactor now running on `main`
  finishes, since that refactor may move the places they would go.
- **Land the sandbox changes on main.** Part 4 ran on two dev-playbook
  changes that exist only in a throwaway config copy
  ([Part 4](/working-docs/parallel-fronts/experiment-log.md#part-4-real-claude)):
  `measure-event` sending rows to the host from a sandbox, and the Stop and
  SessionEnd hooks set to wait. All five problems in
  [What it guarantees](/working-docs/parallel-fronts/pipeline.md#what-it-guarantees)
  are solved in test; this is the last step to make them solved for real.
- **One lap by hand.** Run the shape once with two fronts and no driver
  program at all, to find where it hurts before any of it is automated.
  The lap tests what the control-code design decided, and answers
  whether a front converges or finishes its useful work and then invents
  more. The guess: a front needs a way to declare itself done, and its
  budget is a ceiling, not a target.

## Completed

- **Survey Sandcastle.** What the tool offers this shape is recorded in
  [Sandcastle](/working-docs/parallel-fronts/sandcastle.md).
- **State the sandbox requirement.** What a front's container must reach,
  and where Sandcastle collides with it, is recorded in
  [The five problems](/working-docs/parallel-fronts/experiment-log.md#the-five-problems).
- **Assert this device holds no metered credential.** The billing
  checks assert it at the commit gate, under
  [Billing Credentials](/standards/billing/credentials.md); what they read is under
  [Constraints](#constraints).
- **Experiment one: the clone round-trip.** A front's commits are made in a
  throwaway clone and reach the real repository at the same SHA, or the lap
  stops. [`front-clone`](/scripts/front-clone) is the plumbing, and
  [the log](/working-docs/parallel-fronts/experiment-log.md#experiment-one-the-clone-round-trip)
  records what the run settled. It used no container and no driver, so what it
  settled is git's behavior alone.
- **Experiment two: Sandcastle against a copy.** Sandcastle, pointed at a
  `front-clone` copy with a misbehaving stand-in agent, left the real
  repository and the user's unpushed work untouched, and the commit came
  back. It proved the throwaway copy solves **Shared history** and
  **Relabel**, and exposed the **Workspace collision** and the **Booby
  trap**. [The log](/working-docs/parallel-fronts/experiment-log.md#experiment-two-sandcastle-against-a-copy)
  records the details.
- **Experiment three, part 1: the booby-trap fix.** `front-clone close`
  never runs git in a copy, and a permanent test plants a trigger at every
  point git offers and asserts none fires.
  [The log](/working-docs/parallel-fronts/experiment-log.md#the-booby-trap-fix)
  records how.
- **Experiment three, part 2: option B.** A 20-line wrapper around
  Sandcastle's podman plug-in closes the **Workspace collision** with no
  fork and no standards change, proven with the stand-in on a
  mission-control front and a dev-playbook front. The user then chose one
  layout for every front, work copy at `~/assignment/<repo>`.
  [The log](/working-docs/parallel-fronts/experiment-log.md#experiment-three-the-plug-in)
  records the run.
- **Experiment three, part 4: real Claude end to end.** Real Claude, on the
  subscription, did a tiny task in a front through Sandcastle and the
  option B plug-in. Billing, config, and the commit's return passed at once;
  hook logging passed once the two end-of-session hooks were set to wait.
  [The log](/working-docs/parallel-fronts/experiment-log.md#part-4-real-claude)
  records the run.
- **Walk the user through the Sandcastle pipeline.** The user saw the
  copies, the plug-in, the round trip, and the hook logging, and named the
  arrangement. A front assigned to change dev-playbook keeps both copies:
  the read-only config copy answers "what does published main say", so the
  front's own unfinished edits never change the rules it runs under
  ([Inside the container](/working-docs/parallel-fronts/pipeline.md#inside-the-container)).
- **Save the pipeline's code.** The plug-in, the parallel run, the
  receiver, the image, and the two dev-playbook changes as patches are
  committed in [`rig/`](/working-docs/parallel-fronts/rig/index.md).
- **Run fronts in parallel.** Two fronts on one fake real repository ran
  at once and closed at once, and every check passed. Nothing changes
  between two fronts and five
  ([Fronts in parallel](/working-docs/parallel-fronts/pipeline.md#fronts-in-parallel)).
- **Discuss: what this gives the user.** The ability to call Sandcastle's
  `run()` and carry out any prompt inside a sealed container, holding the
  assigned repository and a read-only copy of published dev-playbook.
  Sandcastle offers more; the set uses only `run()`, with instructions
  passed as `prompt`, until more proves its need
  ([The run() call](/working-docs/parallel-fronts/pipeline.md#the-run-call)).

## Acronyms

None.
