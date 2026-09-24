---
type: Guide
title: The Sandcastle Pipeline
description: The pipeline as built and proven — how a stint's run goes from open to close, how stints run in parallel, the layout inside a container, how a run is told what to do, what it guarantees, where each piece lives, and what it does not yet do
---

# The Sandcastle Pipeline

The Sandcastle pipeline runs unattended stints
([the delegation terms](/workstreams/delegation/WORKSTREAM.md#terms))
in parallel, each from start to finish in its own sealed container:
throwaway copies go in, one agent works there through Sandcastle and a
plug-in of ours, and only its commit comes back. It is built and proven
with real Claude on the subscription, and bound by the workstream's
[Constraints](/workstreams/delegation/sandcastle/WORKSTREAM.md#constraints). How
each part was found and tested is in the
[Experiment Log](/workstreams/delegation/sandcastle/experiment-log.md); this
member describes the result.

## The run, start to finish

```
 HOST                                         CONTAINER (podman)
 ────                                         ─────────
 1 guard      billing checks: no metered credential
 2 open       front-clone open ─► work copy
              config copy of published main
              credential copy, hook receiver + port file
 3 run        Sandcastle run() ──────────────► agent works in ~/assignment/<repo>
              hook receiver ◄──── hook events ─ Claude's hooks
 4 close      front-clone close ◄── commits ── work copy
              real repo gets the stint's branch, same SHA
 5 clean up   copies deleted, receiver stopped, no container left
```

1. **Guard.** The billing checks of `playbook check` assert no metered credential on this device,
   and the run itself refuses to start if anything it hands the container
   carries one.
2. **Open.** [`front-clone`](/scripts/front-clone) `open` clones the real
   repository into a throwaway work copy, on the stint's branch. The clone
   shares no files with the real repository, checked after every clone:
   a shared file would carry the SELinux relabel back to the real one. Beside it go a copy of dev-playbook at published `main`
   (the config copy), a copy of the subscription credential, and a small
   receiver on this machine that writes hook events into the measurement
   database.
3. **Run.** Sandcastle's `run()` starts the container, gives the agent its
   prompt, and waits for it to exit. Its own `claudeCode` agent plug-in
   runs Claude; our plug-in places the work copy (below).
4. **Close.** `front-clone close` brings the stint's commits into the real
   repository at the same SHA. The real repository fetches them without
   force, so a branch that something else moved meanwhile is refused, not
   overwritten. It never runs git inside the copy, and it refuses, leaving
   the copy on disk, if the copy holds uncommitted work. Until the close,
   the stint's branch exists only in the copy.
5. **Clean up.** The copies and the credential copy are deleted, and the
   receiver stops.

## Stints in parallel

Every stint runs these five steps on its own: its own copies, its own
container, its own receiver. Stints share only two things, and neither
limits how many run:

- **The real repository.** Each close writes a different branch.
- **The measurement database.** Each receiver adds rows one at a time.

```
                 one base commit
        ┌──────────┬───┴──────┬──────────┐
     stint-a    stint-b    stint-c     …        each in its own container
        └──────────┴───┬──────┴──────────┘
                 real repository: one branch per stint
```

Proven with two stints on one repository, started at the same moment and
closed at the same moment, by
[`rig/parallel.mjs`](/workstreams/delegation/sandcastle/rig/index.md):

| Check | Result |
|---|---|
| Commits | Both came back at the same SHA, each on its own branch. `main` and the user's unpushed `issue-123` were unchanged. |
| Closes at once | Both succeeded. |
| Billing | Both runs reported the subscription (`apiKeySource: none`). |
| Hook logging | Each session logged start, prompt, tool uses, Stop, and SessionEnd into the one database. |
| Clean up | Both copies deleted, no container left. |

Nothing in the pipeline changes between two stints and five, so there is
no technical reason three, four, or five cannot run at once.

## Inside the container

```
/home/agent/
    .claude/                  ← links into the config copy: skills, rules, hooks …
    .claude/.credentials.json ← subscription credential copy, read-only
    workspace/
        dev-playbook/         ← config copy, published main, read-only
    assignment/
        <repo>/               ← work copy, the stint's branch, read-write
```

The agent can write in one place only, `~/assignment/<repo>`. Every stint
uses this one layout, whatever its repository. The folder is named
`assignment` because it holds the one repository the agent is assigned to
change. The work copy's own folder carries the repository's name, because
the workspace reads a repository's name from that folder
([Same-Repo Resolution](/docs/decisions/0009-same-repo-resolution.md)).

Every stint needs the config copy, for two readers:

- **The harness, before the agent starts.** The links in `~/.claude/`
  point into the config copy. Without it they dangle, and the agent runs
  silently with no skills, rules, or hooks.
- **The agent, during the work.** The global `CLAUDE.md` sends it to the
  standards before its first task, and skills cite dev-playbook paths.

A stint assigned to change dev-playbook holds two dev-playbook copies, the
config copy and its work copy, and they stay separate: its own unfinished
edits never change the rules it runs under.

## The plug-in

Sandcastle is used as published. By default it puts the repository at
`~/workspace` itself, which breaks the workspace layout; a 20-line wrapper
around its own podman plug-in moves the work copy to `~/assignment/<repo>`.
The code is [`rig/relocated.mjs`](/workstreams/delegation/sandcastle/rig/index.md).
Why the pipeline leaves the workspace standards unchanged is in
[Experiment three](/workstreams/delegation/sandcastle/experiment-log.md#experiment-three-the-plug-in).

## The run() call

The pipeline calls one Sandcastle function, `run()`, which runs one agent
from start to finish. Sandcastle's other functions wait until a need
proves them
([Principles](/workstreams/delegation/WORKSTREAM.md#principles)).

**Instructions go in as `prompt`.** The driver reads the task from a file,
such as `PROMPT.md`, and passes the text as `run()`'s `prompt` argument.
Sandcastle hands it to the agent exactly as written. The other way,
`promptFile`, fills in `{{KEY}}` placeholders and runs `` !`command` ``
lines inside the container first; that is Sandcastle syntax the pipeline
does not need. Where a value such as the stint's name belongs in the
text, the driver puts it there with ordinary code.

**An iteration is one fresh Claude session.** Claude takes as many turns as
it needs, commits, and exits. A next iteration starts a new session with
the same prompt and no memory of the last; only the repository carries
over. Two arguments control the loop:

| Argument | Default | Meaning |
|---|---|---|
| `maxIterations` | 1 | The most sessions a run starts |
| `completionSignal` | `<promise>COMPLETE</promise>` | Text that ends the loop early. Sandcastle never tells the agent this text, so the prompt names it |

The rig uses the defaults: one session per run.

**The branch strategy is `head`**, of Sandcastle's
[branch modes](/workstreams/delegation/sandcastle/survey.md#what-it-fixes-and-where-it-bends).
`front-clone` has already checked the stint's branch out in the copy, so a
mode that adds a worktree of its own on that branch would fail.

## What it guarantees

| Problem | How the pipeline answers it |
|---|---|
| **Shared history** — an agent could delete other branches and unpushed work | The container sees a copy with its own private history, never the real one |
| **Relabel** — SELinux permanently changes labels on mounted files | Only the copies are mounted, and they are deleted |
| **Booby trap** — an agent plants a command that later runs on the host | `front-clone close` never runs git in the copy |
| **Workspace collision** — Sandcastle's layout misnames the repository | The plug-in keeps the workspace's layout |
| **Hook logging** — the user's hooks must keep logging | Events travel to the host receiver |

Also: the subscription pays (Claude reports no API key in use), and no
stint reaches GitHub, since the container holds no GitHub credential.

## Where each piece lives

| Piece | Where it is now |
|---|---|
| `front-clone` and its trap test | This branch, under `scripts/` and `tests/` |
| The plug-in, the parallel run, the receiver, the container image | This branch, in [`rig/`](/workstreams/delegation/sandcastle/rig/index.md) |
| `measure-event` sending hook events from a container, and the Stop and SessionEnd hooks set to wait | Patches in `rig/patches/`, not yet applied to dev-playbook |

Everything in `rig/` stays in the workstream until the work lands on `main`.

## What it does not yet do

Both gaps this section listed are closed by `rig/stint.py`
([The start command](/workstreams/delegation/sandcastle/experiment-log.md#the-start-command)):
one command starts a stint on any repository and ends it, and it keeps
each stint's copies in `~/stints/<repo>/<stint>/`, outside Claude's own
temporary folder. What remains is on the
[head file's worklist](/workstreams/delegation/sandcastle/WORKSTREAM.md#planned).

## Acronyms

- **SHA** — Secure Hash Algorithm; here, the ID of a git commit.
- **SELinux** — Security-Enhanced Linux.
