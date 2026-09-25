---
type: Workstream
title: Sandcastle Workstream
description: The head file of the sandcastle workstream inside delegation — the pipeline that runs an unattended stint in a sealed container, the hard bounds it runs under, how to report on it, its words, and its worklist
---

# Sandcastle Workstream

This workstream is speculative, as its parent is: every member writes a guess as a
guess. It holds the machinery for one part of
[the delegation workflow](/workstreams/delegation/WORKSTREAM.md): running an
unattended stint safely, an agent in a sealed container on a throwaway
copy, with only its commit coming back. What a stint is, and how it is
tracked, is the parent's; how it runs is this workstream's. The
[Sandcastle pipeline](/workstreams/delegation/sandcastle/pipeline.md) is
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
  [the parent's constraints](/workstreams/delegation/WORKSTREAM.md#constraints)
  require, so only local git works inside it, and whatever pushes its
  commits does so outside.
- The user's hooks keep logging every event to the measurement database
  from inside a container.
- Sandcastle is never forked or patched. It is used as published, through
  the plug-ins it accepts, since a fork would need maintaining for as long
  as the workstream uses it.

### Working with the user

A report to the user sits at the level of the problem table in
[What it guarantees](/workstreams/delegation/sandcastle/pipeline.md#what-it-guarantees):
plain language, each problem and solution by its name, and a concrete
picture where one helps, such as a directory tree with enough rows to show
what the files are.

## Terms

The Sandcastle pipeline is defined with
[the delegation workflow's terms](/workstreams/delegation/WORKSTREAM.md#terms),
since the parent uses it too.

## Planned

Nothing is planned. The tool is the `stint` command in
[`src/dev_playbook/stint/`](/src/dev_playbook/stint/cli.py); the
delegation workflow's remaining work is on the
[parent's worklist](/workstreams/delegation/WORKSTREAM.md#planned).

### Delete after the merge

- The patches in `src/dev_playbook/stint/patches/` and the step in
  `config.py` that applies them: once `main` holds the three changes, the
  config copy needs none, and `git apply` fails loud on a patch already
  applied.

## Completed

- **Survey Sandcastle.** What the tool offers is recorded in
  [Sandcastle](/workstreams/delegation/sandcastle/survey.md).
- **State the sandbox requirement.** What a container must reach, and
  where Sandcastle collides with it, is recorded in
  [The five problems](/workstreams/delegation/sandcastle/experiment-log.md#the-five-problems).
- **Assert this device holds no metered credential.** The billing
  checks assert it at the commit gate, under
  [Billing Credentials](/standards/billing/credentials.md).
- **Experiment one: the clone round-trip.** Commits made in a throwaway
  clone reach the real repository at the same SHA, or the run stops.
  [`front-clone`](/src/dev_playbook/stint/workcopy.py) is the plumbing, and
  [the log](/workstreams/delegation/sandcastle/experiment-log.md#experiment-one-the-clone-round-trip)
  records what the run settled.
- **Experiment two: Sandcastle against a copy.** Sandcastle, pointed at a
  `front-clone` copy with a misbehaving stand-in agent, left the real
  repository and the user's unpushed work untouched, and the commit came
  back. [The log](/workstreams/delegation/sandcastle/experiment-log.md#experiment-two-sandcastle-against-a-copy)
  records the details.
- **Experiment three, part 1: the booby-trap fix.** `front-clone close`
  never runs git in a copy, and a permanent test plants a trigger at every
  point git offers and asserts none fires.
  [The log](/workstreams/delegation/sandcastle/experiment-log.md#the-booby-trap-fix)
  records how.
- **Experiment three, part 2: option B.** A 20-line wrapper around
  Sandcastle's podman plug-in closes the **Workspace collision** with no
  fork and no standards change, with the work copy at
  `~/assignment/<repo>`.
  [The log](/workstreams/delegation/sandcastle/experiment-log.md#experiment-three-the-plug-in)
  records the run.
- **Experiment three, part 4: real Claude end to end.** Real Claude, on the
  subscription, did a tiny task through Sandcastle and the plug-in.
  Billing, config, and the commit's return passed at once; hook logging
  passed once the two end-of-session hooks were set to wait.
  [The log](/workstreams/delegation/sandcastle/experiment-log.md#part-4-real-claude)
  records the run.
- **Walk the user through the Sandcastle pipeline.** The user saw the
  copies, the plug-in, the round trip, and the hook logging, and named the
  arrangement
  ([Inside the container](/workstreams/delegation/sandcastle/pipeline.md#inside-the-container)).
- **Save the pipeline's code.** The plug-in, the parallel run, the
  receiver, the image, and the two dev-playbook changes as patches are
  committed in [`rig/`](/workstreams/delegation/sandcastle/rig/index.md).
- **Run in parallel.** Two agents on one fake real repository ran at once
  and closed at once, and every check passed
  ([Stints in parallel](/workstreams/delegation/sandcastle/pipeline.md#stints-in-parallel)).
- **Discuss: what this gives the user.** The ability to call Sandcastle's
  `run()` and carry out any prompt inside a sealed container, holding the
  assigned repository and a read-only copy of published dev-playbook
  ([The run() call](/workstreams/delegation/sandcastle/pipeline.md#the-run-call)).
- **Nest under delegation.** Done 2026-09-24: the Sandcastle members moved
  from the delegation head file into this workstream, and the `rig/` scripts find the
  repository root one level further up.
- **Test the container's lifetime.** Done 2026-09-24: the work copy opens
  once per stint, and each agent call gets a new container on it. Only the
  work copy carries from one call to the next, uncommitted files included,
  and Sandcastle runs nothing on the host that the agent can plant
  ([The container's lifetime](/workstreams/delegation/sandcastle/experiment-log.md#the-containers-lifetime)).
- **One unattended stint by hand.** Done 2026-09-24: a four-task stint
  ran to done with every call sealed, and the principal was one
  conversation across its three calls, resumed from a session file kept
  in the stint's folder
  ([One unattended stint by hand](/workstreams/delegation/sandcastle/experiment-log.md#one-unattended-stint-by-hand),
  [The principal's conversation](/workstreams/delegation/sandcastle/experiment-log.md#the-principals-conversation)).
- **Write the headless loop script.** Done 2026-09-24:
  [`rig/stint.py`](/workstreams/delegation/sandcastle/rig/index.md) ran a
  stint to done with no person in the loop, every call sealed, and
  `rig/rules.py` checks its stop rules with no tokens. The user ruled that
  every call runs in a container, so the local step is removed
  ([The headless driver](/workstreams/delegation/sandcastle/experiment-log.md#the-headless-driver)).
- **Close the implementation testing.** Done 2026-09-24: the user ruled
  that an iteration ticking other than one task is a note the principal
  and the user see, not a stop, and that the driver checks no call's
  billing. The pipeline's remaining work is the Planned list above and
  the board in the
  [parent's worklist](/workstreams/delegation/WORKSTREAM.md#planned).
- **Connect a stint.** Done 2026-09-24: `rig/stint.py` takes any
  repository, a base branch, the workstream directory, and a budget. It
  makes the work copy and the config copy in `~/stints/<repo>/<stint>/`,
  runs the stint, lands its branch, deletes both copies, and keeps the
  record. Stint 5 ran through it live to done
  ([The start command](/workstreams/delegation/sandcastle/experiment-log.md#the-start-command)).
- **Write a sandboxed commit skill.** Done 2026-09-24: `commit-sandbox`
  commits everything to the branch checked out and never pushes. It
  shares one procedure, `commit-inherit/references/commit.md`, with
  `commit-inherit` and `commit-sonnet`; those two also read
  `references/host.md`, which holds the target, the staging rule, and
  the push. The stint's prompts run it, and
  `rig/patches/commit-sandbox.patch` puts it in the config copy until it
  is on `main`.
- **Re-word the members.** Done 2026-09-24: `pipeline.md`,
  `survey.md`, `experiment-log.md`, and `rig/index.md` in the
  delegation workflow's terms.
- **Close the workstream: move the tool to `src/dev_playbook/stint/`.**
  Done 2026-09-24: one package, the work copy included, as the installed
  `stint` command with every argument required
  ([Running a Stint](/guides/running-a-stint.md)). Node does only
  Sandcastle's `run()`; the call, the loop, and the records are Python,
  tested with no container. A live `stint setup` and `stint run` with
  Sonnet on a practice repository ran the four-task `wordcount` plan to
  done in 9 calls and 9.6 minutes: every call billed to the subscription,
  the hooks logged, the branch landed with its six commits, and both
  copies were deleted. The experiments' code stays in `rig/` as history.

## Acronyms

- **PR** — pull request.
- **SELinux** — Security-Enhanced Linux, the kernel's access-control layer.
- **SHA** — the hash that names a commit.
- **WSL** — Windows Subsystem for Linux.
