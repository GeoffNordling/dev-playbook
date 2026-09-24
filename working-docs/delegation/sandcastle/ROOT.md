---
type: General-Sheet
title: Sandcastle Working Root
description: The root of the sandcastle set inside delegation — the pipeline that runs an unattended stint in a sealed container, the hard bounds it runs under, how to report on it, its words, and its worklist
---

# Sandcastle Working Root

This set is speculative, as its parent is: every member writes a guess as a
guess. It holds the machinery for one part of
[the delegation workflow](/working-docs/delegation/ROOT.md): running an
unattended stint safely, an agent in a sealed container on a throwaway
copy, with only its commit coming back. What a stint is, and how it is
tracked, is the parent's; how it runs is this set's. The
[Sandcastle pipeline](/working-docs/delegation/sandcastle/pipeline.md) is
built and proven.

## Constraints

- Every sandboxed agent reads dev-playbook at published `main`, whichever
  repository it is assigned to change. One assigned to change dev-playbook
  reads the standards as published while it writes their replacement.
  The config stays fixed for the whole stint, and never comes from the
  agent's own branch.
- Every run happens on the Fedora machine, and nowhere else. The container,
  its image, and the `claude` binary inside it are Fedora. The WSL Ubuntu
  machine has no container runtime and is not a target.
- The subscription pays for every run, and this is asserted, not assumed.
  The billing checks of `playbook check`, under
  [Billing Credentials](/standards/billing/credentials.md), run at the
  commit gate and again before every run.
- A container never mounts a real file, only copies made for the run and
  deleted after it. Podman's SELinux option permanently relabels whatever
  is mounted, even read-only, and a host program can then be refused its
  own file.
- The container holds no GitHub credential, as
  [the parent's constraints](/working-docs/delegation/ROOT.md#constraints)
  require, so only local git works inside it, and whatever pushes its
  commits does so outside.
- The user's hooks keep logging every event to the measurement database
  from inside a container.
- Sandcastle is never forked or patched. It is used as published, through
  the plug-ins it accepts, since a fork would need maintaining for as long
  as the set uses it.

## Working with the user

A report to the user sits at the level of the problem table in
[What it guarantees](/working-docs/delegation/sandcastle/pipeline.md#what-it-guarantees):
plain language, each problem and solution by its name, and a concrete
picture where one helps, such as a directory tree with enough rows to show
what the files are.

## Terms

The Sandcastle pipeline is defined with
[the delegation workflow's terms](/working-docs/delegation/ROOT.md#terms),
since the parent uses it too.

## Planned

- **Connect a stint.** An unattended stint launches from a
  [workstream](/working-docs/delegation/ROOT.md#terms), counts its budget,
  wraps up at the hard limit, and yields. This settles what the
  pipeline does not yet do
  ([What it does not yet do](/working-docs/delegation/sandcastle/pipeline.md#what-it-does-not-yet-do)):
  what schedules a stint, and where real copies live.
- **Land the sandbox changes on main.** Part 4 ran on two dev-playbook
  changes that exist only in a throwaway config copy
  ([Part 4](/working-docs/delegation/sandcastle/experiment-log.md#part-4-real-claude)):
  `measure-event` sending rows to the host from a sandbox, and the Stop and
  SessionEnd hooks set to wait.
- **Write the headless loop script.** The
  [headless driver](/working-docs/delegation/ROOT.md#settled) in Python,
  developed in [`rig/`](/working-docs/delegation/sandcastle/rig/index.md):
  the loop, the stop rules, and the checkpoints in the script, and the
  step that runs one iteration swappable between a local `claude -p` and
  the Sandcastle pipeline. Sandcastle is a Node library, so the Sandcastle
  step calls a small `.mjs` shim that runs Sandcastle's `run()` for one
  iteration; Sandcastle's own loop goes unused. The iteration prompt moves
  out of `ralph-loop.js` into one file that both drivers read. The
  reviewer runs sealed too, so nothing in a stint
  touches the host but the driver.
- **Plan the landing on main.** The code in `rig/` lands in `scripts/`,
  and the pipeline's document beside it, through one PR or several; which
  PRs, in what order, carrying what.
- **Write a sandboxed commit skill.** It commits with plain git and never
  pushes, since a sealed agent has no GitHub. Today's iteration prompt
  commits through `commit-sonnet`, which pushes
  ([One unattended stint by hand](/working-docs/delegation/sandcastle/experiment-log.md#one-unattended-stint-by-hand)).

## Completed

- **Survey Sandcastle.** What the tool offers is recorded in
  [Sandcastle](/working-docs/delegation/sandcastle/survey.md).
- **State the sandbox requirement.** What a container must reach, and
  where Sandcastle collides with it, is recorded in
  [The five problems](/working-docs/delegation/sandcastle/experiment-log.md#the-five-problems).
- **Assert this device holds no metered credential.** The billing
  checks assert it at the commit gate, under
  [Billing Credentials](/standards/billing/credentials.md).
- **Experiment one: the clone round-trip.** Commits made in a throwaway
  clone reach the real repository at the same SHA, or the run stops.
  [`front-clone`](/scripts/front-clone) is the plumbing, and
  [the log](/working-docs/delegation/sandcastle/experiment-log.md#experiment-one-the-clone-round-trip)
  records what the run settled.
- **Experiment two: Sandcastle against a copy.** Sandcastle, pointed at a
  `front-clone` copy with a misbehaving stand-in agent, left the real
  repository and the user's unpushed work untouched, and the commit came
  back. [The log](/working-docs/delegation/sandcastle/experiment-log.md#experiment-two-sandcastle-against-a-copy)
  records the details.
- **Experiment three, part 1: the booby-trap fix.** `front-clone close`
  never runs git in a copy, and a permanent test plants a trigger at every
  point git offers and asserts none fires.
  [The log](/working-docs/delegation/sandcastle/experiment-log.md#the-booby-trap-fix)
  records how.
- **Experiment three, part 2: option B.** A 20-line wrapper around
  Sandcastle's podman plug-in closes the **Workspace collision** with no
  fork and no standards change, with the work copy at
  `~/assignment/<repo>`.
  [The log](/working-docs/delegation/sandcastle/experiment-log.md#experiment-three-the-plug-in)
  records the run.
- **Experiment three, part 4: real Claude end to end.** Real Claude, on the
  subscription, did a tiny task through Sandcastle and the plug-in.
  Billing, config, and the commit's return passed at once; hook logging
  passed once the two end-of-session hooks were set to wait.
  [The log](/working-docs/delegation/sandcastle/experiment-log.md#part-4-real-claude)
  records the run.
- **Walk the user through the Sandcastle pipeline.** The user saw the
  copies, the plug-in, the round trip, and the hook logging, and named the
  arrangement
  ([Inside the container](/working-docs/delegation/sandcastle/pipeline.md#inside-the-container)).
- **Save the pipeline's code.** The plug-in, the parallel run, the
  receiver, the image, and the two dev-playbook changes as patches are
  committed in [`rig/`](/working-docs/delegation/sandcastle/rig/index.md).
- **Run in parallel.** Two agents on one fake real repository ran at once
  and closed at once, and every check passed
  ([Stints in parallel](/working-docs/delegation/sandcastle/pipeline.md#stints-in-parallel)).
- **Discuss: what this gives the user.** The ability to call Sandcastle's
  `run()` and carry out any prompt inside a sealed container, holding the
  assigned repository and a read-only copy of published dev-playbook
  ([The run() call](/working-docs/delegation/sandcastle/pipeline.md#the-run-call)).
- **Nest under delegation.** Done 2026-09-24: the Sandcastle members moved
  from the delegation root into this set, and the `rig/` scripts find the
  repository root one level further up.
- **Test the container's lifetime.** Done 2026-09-24: the work copy opens
  once per stint, and each agent call gets a new container on it. Only the
  work copy carries from one call to the next, uncommitted files included,
  and Sandcastle runs nothing on the host that the agent can plant
  ([The container's lifetime](/working-docs/delegation/sandcastle/experiment-log.md#the-containers-lifetime)).
- **One unattended stint by hand.** Done 2026-09-24: a four-task stint
  ran to done with every call sealed, and the principal was one
  conversation across its three calls, resumed from a session file kept
  in the stint's folder
  ([One unattended stint by hand](/working-docs/delegation/sandcastle/experiment-log.md#one-unattended-stint-by-hand),
  [The principal's conversation](/working-docs/delegation/sandcastle/experiment-log.md#the-principals-conversation)).

- **Re-word the members.** Done 2026-09-24: `pipeline.md`,
  `survey.md`, `experiment-log.md`, and `rig/index.md` in the
  delegation workflow's terms.

## Acronyms

- **PR** — pull request.
- **SELinux** — Security-Enhanced Linux, the kernel's access-control layer.
- **SHA** — the hash that names a commit.
- **WSL** — Windows Subsystem for Linux.
