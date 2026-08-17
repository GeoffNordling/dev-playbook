---
type: Guide
title: Sandboxing Claude agents
description: Which tools fence a Claude agent, and the container direction for work with no user attached
---

# Sandboxing Claude agents

Which tools we use to fence a Claude agent, and how we intend to fence AFK work
once it moves to headless. The specific allow and deny settings live in the
settings files, not here — they change, and a copy of them here would only go
stale.

## The tools

**Anthropic's [native sandbox](https://code.claude.com/docs/en/sandboxing)
(`/sandbox`)** is what we run for everyday Inline work. It fences the agent
using features built into Linux itself rather than a container, so it costs
nothing to start and nothing to maintain.

Its one structural limit decides everything downstream: **it bounds shell
commands, not the agent's own file tools.** Read, Edit, and Write ride the
permission system instead. With the user at the terminal that is fine — the
permission prompts are the fence. With no user attached there are no prompts, so
the file tools are unbounded.

Settings cannot stand in for the prompts either: path-scoped permission rules
are silently ignored headless, so a file tool is allowed everywhere or nowhere
([headless.md](/docs/headless.md)).

**A container** is therefore the fence for AFK work. The whole `claude` process
runs inside it, so every tool — file tools included — sees only the directories
we chose to put there. This is the direction. Nothing is built yet.

**[Sandcastle](https://github.com/mattpocock/sandcastle) — declined.** Matt
Pocock's framework is AFK *orchestration* that uses containers as a component.
We want a sandbox, not a workflow engine: adopting it means adopting the loop
our own factory already owns, and writing a TypeScript file per run to do it.
Declined on that alone, not on its quality.

## How we intend to operate

- **Inline work keeps the native sandbox.** Always on, no per-run ceremony, and
  the permission prompts cover what it doesn't.
- **AFK work runs in a container.** A container starts empty: the only
  directories from this machine that exist inside it are the ones we hand it.
  That list is the fence — a worktree the agent may write to, plus whatever it
  needs to read. Everything else on the disk is simply not there.
- **We own the command that starts the container.** Whatever we build around
  it, that command stays ours to write and change. A framework owning it is why
  Sandcastle is declined.
- **Limiting which sites the agent can reach comes later.** A container reaches
  the whole internet by default. Narrowing that means running a second small
  program beside the agent, with all its traffic passing through — every
  destination checked against a list we maintain. Worth having eventually, so a
  hijacked agent can't phone home. Deferred because a missing entry doesn't
  announce itself: the agent stalls or reports something unrelated, and you
  debug the wrong thing. A working container first.

## Open

- **Docker or podman.** Two programs that do the same job. Docker is the
  industry default — tutorials, prebuilt images, and Anthropic's own reference
  setup all assume it, which is worth real money when something breaks at an
  inconvenient hour. Podman is Fedora's own, and runs containers as an ordinary
  user rather than as the machine's administrator: if an agent ever got out of
  its container, it would land with our own permissions rather than full control
  of the machine. Both read the same setup file, so the container itself is
  identical and switching later is a few settings in one script — cheap to leave
  undecided.
- **What the container can read.** AFK agents need the workspace standards that
  live in dev-playbook. Whether those arrive as a directory handed to the
  container, a copy built into it, or something else is unsettled.
- **Whether we ever restrict the agent's internet access**, and what would be on
  the allowed list.
- **Whether the native sandbox also runs inside the container.** Belt and
  braces, or redundant ceremony.
