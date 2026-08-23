---
type: Guide
title: Sandboxing Claude agents
description: The native sandbox is off, pending a redesign under issue 261; the container direction for work with no user attached is still ahead
---

# Sandboxing Claude agents

**Anthropic's [native sandbox](https://code.claude.com/docs/en/sandboxing) is
off.** [Decision Record 0024](/docs/decisions/0024-disable-native-sandbox.md)
has the reasoning — months of false positives with no real catch to show for
them — and #261 tracks redesigning a tighter, trustworthy surface and
reintroducing it.

## The container direction

AFK work — headless, no user attached — has no fence today, regardless of the
native sandbox's on/off state: [headless.md](/docs/headless.md) covers why
path-scoped permission rules don't help there. **A container** is the intended
fence. The whole `claude` process would run inside it, so every tool — file
tools included — sees only the directories we chose to put there. Nothing is
built yet.

**[Sandcastle](https://github.com/mattpocock/sandcastle) — declined.** Matt
Pocock's framework is AFK *orchestration* that uses containers as a component.
We want a sandbox: adopting it means adopting the loop our own factory owns,
and writing a TypeScript file per run to do it. Declined on that alone.

## How we intend to operate

- **AFK work runs in a container.** A container starts empty: the only
  directories from this machine that exist inside it are the ones we hand it.
  That list is the fence — a worktree the agent may write to, plus whatever it
  needs to read. Everything else on the disk is not there.
- **We own the command that starts the container.** Whatever we build around
  it, that command stays ours to write and change. A framework owning it is why
  Sandcastle is declined.
- **Limiting which sites the agent can reach comes later.** A container reaches
  the whole internet by default. Narrowing that means running a second small
  program beside the agent, with all its traffic passing through — every
  destination checked against a list we maintain. Worth having eventually, so a
  hijacked agent can't phone home. Deferred because a missing entry doesn't
  announce itself: the agent stalls or reports something unrelated, and you
  debug the wrong thing.

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
- **Whether a reintroduced native sandbox also runs inside the container.** Belt
  and braces, or redundant ceremony.
