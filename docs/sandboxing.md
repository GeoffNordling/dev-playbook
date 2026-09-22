---
type: General-Sheet
title: Sandboxing Claude agents
description: The native sandbox is off, pending a redesign under issue 261; the container direction for work with no user attached has a working prototype, not yet integrated
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
tools included — sees only the directories we chose to put there.

**A prototype has proven the mechanics work, on a local branch not yet
merged.** `sandbox-probe` runs a real headless Claude agent inside a podman
container, billing the subscription rather than the metered API, with the
user's own skills, rules, and hooks reproduced by baking `sync-dotfiles` into
the image. The only things the container can reach on the host are a
throwaway clone of the repo being worked on and a copy of the credentials
file — no GitHub token, nothing else. It also fixed a problem the fence
itself caused: hook events from inside the container were vanishing instead
of reaching the host's measurement database, fixed with a small TCP receiver
on the host. None of this is integrated — the branch is mostly one-off check
commands for learning, not something to build against, and a real
`dev_playbook.sandbox` module has not been started.

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
- **Podman, not Docker.** Fedora's own tool: already installed and working
  with SELinux here, rootless by default so it leaves no root-owned files
  behind, and no background service to configure. The prototype used it
  without friction. Docker and podman read the same setup file, so switching
  later stays cheap if it's ever worth it.
- **Limiting which sites the agent can reach comes later.** A container reaches
  the whole internet by default. Narrowing that means running a second small
  program beside the agent, with all its traffic passing through — every
  destination checked against a list we maintain. Worth having eventually, so a
  hijacked agent can't phone home. Deferred because a missing entry doesn't
  announce itself: the agent stalls or reports something unrelated, and you
  debug the wrong thing.

## Open

- **What the container can read.** The prototype's design landed on an answer:
  a read-only mount of dev-playbook's main checkout as the config source
  (what the baked-in skills, rules, and hooks read from), separate from a
  read-write clone of whatever repo is being worked on. Not yet adopted for
  real.
- **Whether we ever restrict the agent's internet access**, and what would be on
  the allowed list.
- **Whether a reintroduced native sandbox also runs inside the container.** Belt
  and braces, or redundant ceremony.
