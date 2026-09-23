---
type: Guide
title: The Sandcastle Pipeline
description: The pipeline as built and proven — how one front runs from open to close, the layout inside its container, what it guarantees, where each piece lives, and what it does not yet do
---

# The Sandcastle Pipeline

The Sandcastle pipeline runs one front
([Parallel Fronts Working Root](/working-docs/parallel-fronts/ROOT.md#terms))
from start to finish: throwaway copies go into a sealed container, one
agent works there through Sandcastle and a plug-in of ours, and only its
commit comes back. It is built and proven end to end with real Claude on
the subscription. How each part was found and tested is in
[The Sandbox](/working-docs/parallel-fronts/sandbox.md); this member
describes the result.

## The run, start to finish

```
 HOST                                         CONTAINER (podman)
 ────                                         ─────────
 1 guard      billing-lint: no metered credential
 2 open       front-clone open ─► work copy
              config copy of published main
              credential copy, hook receiver + port file
 3 run        Sandcastle run() ──────────────► agent works in ~/assignment/<repo>
              hook receiver ◄──── hook events ─ Claude's hooks
 4 close      front-clone close ◄── commits ── work copy
              real repo gets the front's branch, same SHA
 5 clean up   copies deleted, receiver stopped, no container left
```

1. **Guard.** `billing-lint` asserts no metered credential on this device,
   and the run itself refuses to start if anything it hands the container
   carries one.
2. **Open.** [`front-clone`](/scripts/front-clone) `open` clones the real
   repository into a throwaway work copy, with no shared files, on the
   front's branch. Beside it go a copy of dev-playbook at published `main`
   (the config copy), a copy of the subscription credential, and a small
   receiver on this machine that writes hook events into the measurement
   database.
3. **Run.** Sandcastle's `run()` starts the container, gives the agent its
   prompt, and waits for it to exit. Its own `claudeCode` agent plug-in
   runs Claude; our plug-in places the work copy (below).
4. **Close.** `front-clone close` brings the front's commits into the real
   repository at the same SHA. It never runs git inside the copy, and it
   refuses, leaving the copy on disk, if the copy holds uncommitted work.
5. **Clean up.** The copies and the credential copy are deleted, and the
   receiver stops.

## Inside the container

```
/home/agent/
    .claude/                  ← links into the config copy: skills, rules, hooks …
    .claude/.credentials.json ← subscription credential copy, read-only
    workspace/
        dev-playbook/         ← config copy, published main, read-only
    assignment/
        <repo>/               ← work copy, the front's branch, read-write
```

The agent can write in one place only, `~/assignment/<repo>`. The config
copy gives it the user's standards and harness exactly as published, so
the agent behaves as it would on the user's machine. A front assigned to
change dev-playbook holds two dev-playbook copies, the config copy and its
work copy, and they stay separate: its own unfinished edits never change
the rules it runs under.

## The plug-in

Sandcastle is used as published. By default it puts the repository at
`~/workspace` itself, which breaks the workspace layout; a 20-line wrapper
around its own podman plug-in moves the work copy to `~/assignment/<repo>`.
The code is in
[What experiment three settled](/working-docs/parallel-fronts/sandbox.md#what-experiment-three-settled).

## What it guarantees

| Problem | How the pipeline answers it |
|---|---|
| **Shared history** — a front could delete other branches and unpushed work | The container sees a copy with its own private history, never the real one |
| **Relabel** — SELinux permanently changes labels on mounted files | Only the copies are mounted, and they are deleted; Sandcastle's shared label (`z`) lands on them alone |
| **Booby trap** — a front plants a command that later runs on the host | `front-clone close` never runs git in the copy |
| **Workspace collision** — Sandcastle's layout misnames the repository | The plug-in keeps the workspace's layout |
| **Hook logging** — the user's hooks must keep logging | Events travel to the host receiver |

Also: the subscription pays (Claude reports no API key in use), and no
front reaches GitHub, since the container holds no GitHub credential.

## Running fronts together

Two fronts on one fake real repository, started at the same moment, each
told to make one small commit, on Haiku. Both were then closed into the
real repository at the same moment. Each run took about 22 seconds.

| Check | Result |
|---|---|
| Commits | Both came back at the same SHA, each on its own branch. `main` and the user's unpushed `issue-123` were unchanged. |
| Closes at once | Both succeeded; git did not refuse the second. |
| Billing | Both runs reported the subscription (`apiKeySource: none`). |
| Hook logging | Each session logged start, prompt, both tool uses, Stop, and SessionEnd, through its own receiver into the one database. |
| Clean up | Both copies deleted, no container left. |

The subscription's limits did not show at two sessions. The run is
[`rig/parallel.mjs`](/working-docs/parallel-fronts/rig/index.md).

## Where each piece lives

| Piece | Where it is now |
|---|---|
| `front-clone` and its trap test | This branch, under `scripts/` and `tests/` |
| The plug-in, the run script, the receiver, the container image | This branch, in [`rig/`](/working-docs/parallel-fronts/rig/index.md) |
| Hook events sent from a container (`measure-event`), and the Stop and SessionEnd hooks set to wait | Patches in `rig/patches/`, not yet applied to dev-playbook |

Everything in `rig/` stays in the set until the work lands on `main`.

## What it does not yet do

These are facts about the pipeline today, each settled by a Planned item
in [the root](/working-docs/parallel-fronts/ROOT.md#planned).

- **More than two fronts at once.** Two fronts ran together and passed
  ([Running fronts together](#running-fronts-together)); three and four
  are untested.
- **No schedule.** No program starts a lap's fronts and ends the lap.
- **No home for real copies.** They must not live under
  `/tmp/claude-<uid>/`, which collides with Claude's own temporary folder
  inside the container.
- **No bound on a stranded container.** Sandcastle removes the container
  only when the run ends in an orderly way.

## Acronyms

- **SHA** — Secure Hash Algorithm; here, the ID of a git commit.
- **SELinux** — Security-Enhanced Linux.
