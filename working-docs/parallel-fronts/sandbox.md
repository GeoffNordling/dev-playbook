---
type: General-Sheet
title: The Sandbox
description: What the fence around a front must do — the windows it opens onto the host, the two cases every front falls into, and whether Sandcastle can hold them
---

# The Sandbox

A front runs inside a container, and a container starts able to see
nothing of the machine that launched it. This member records what that
container must nevertheless be able to reach, why, and whether
[Sandcastle](/working-docs/parallel-fronts/sandcastle.md) can arrange it.
The requirements come from the `sandbox-probe` branch, which built and
measured a working container against podman. That branch is a prototype and
prescribes nothing, but the constraints it found are real and hold here.

## Goal

Every sandboxed front reads dev-playbook, whichever repository it is
assigned to change, and always at published state. Some fronts are
assigned to change a dev-playbook branch as well, at the same time. The
set wants every combination of those two facts to work, and wants the
combination to be arranged once rather than reasoned about per front.

## Constraints

Five bounds are settled — three limitations the user accepts, and two rules
the work may not break. They are recorded here so the work does not reopen
them.

**Laps run on Fedora, and nowhere else.** The container, the image it starts
from, and the `claude` binary inside it are all Fedora, and that binary reads
`/etc/os-release` and refuses to run elsewhere. This set is developed on a WSL
Ubuntu machine because that is where the user happens to work, and that
machine has no container runtime at all. It is not a target. Nothing here is
expected to work there, a result measured there does not count, and no effort
is spent making it portable.

**This device holds no metered credential, and something checks.** Every
lap bills the subscription. A billing mistake is the quietest failure in
the set, because the run succeeds and the cost arrives later, so the
absence of a metered credential is asserted rather than assumed. Three
surfaces carry one: the live environment, the shell startup files, and
`~/.claude/settings.json`. The check runs on this device, before a lap
launches, and refuses to launch rather than reporting a finding. A check
that runs where there is no device passes without asserting anything,
which is the failure it exists to prevent.

**No window may point at a real file.** Every window opens onto a copy made
for the lap and deleted after it: a fresh clone of the work repository, a
copy of the config source, a copy of the credential. The reason is the
SELinux restamp described below, which changes the host file's security
label permanently and cannot be prevented by opening the window read-only.
The prototype met this as a real fault, recorded at `NOTES.md:43-51`: a
host program that expects the old label is denied its own file afterwards.
`restorecon -RvF <path>` repairs a file that has been restamped, but this
rule exists so that no repair is needed. A design that hands the container
a window onto anything under `~/workspace/` or onto a real `.git` is wrong
on this ground alone, whatever else recommends it.

**The config source is dev-playbook at published `main`, for every front.**
A front assigned to change a dev-playbook branch therefore reads the
standards as published while it writes their replacement; its own edits are
invisible to it and reach a later lap instead. The alternatives — refreshing
the config source between laps, or letting such a front read its own branch
as config source — are known and declined. The user accepts this as current
state.

**No front reaches GitHub.** The container is handed no GitHub credential,
so inside it `push`, `fetch`, `pull`, and cloning from a URL all fail, and
only local git works: `commit`, `branch`, `diff`, `log`, `reset`,
`checkout`. A front cannot open its own pull request. Its commits leave
through the work checkout window, and whatever pushes them does so outside
the container.

## Why every front reads dev-playbook

Two separate readers need it, and neither is optional.

**The harness reads it before the agent starts.** The eight entries of
`~/.claude/` — among them `skills`, `rules`, `agents`, `hooks`, and
`settings.json` — are symlinks into dev-playbook's `dotfiles/dot-claude/`.
Claude Code follows them at startup. Where dev-playbook is not at the path
those links name, they dangle, and the front starts with no skills, no
rules, and no hooks. The failure is silent: the agent runs, and simply
behaves as though the workspace had no standards.

**The agent reads it during the work.** The global `CLAUDE.md` sends every
agent to `/standards/index.md` before its first task, whichever repository
it is working in, and skills cite dev-playbook paths mid-task. Here a
missing dev-playbook surfaces as a failed read, which is the louder of the
two failures.

## A bind mount

The container reaches the host only through windows opened for it, one per
line of the launch command:

```
--volume=/host/path:/container/path:rw,Z
```

The four fields, left to right: the real directory on the host, where it
appears inside the container, whether the container may write through it,
and an instruction to SELinux.

A window is not a copy. Both sides address the same bytes, so a file the
front writes at `/container/path/x.md` is `/host/path/x.md` on the host
disk at once. That is how a front's commits leave the container at all, and
it is also the whole of the fence: a directory no window names does not
exist inside.

The `Z` is the part with a cost. SELinux runs in enforcing mode on this
machine and refuses reads across security labels, so without it every read
inside the container fails. `Z` tells podman to restamp the host directory
with a label the container may read — and the restamp is permanent, lands
on the real disk, and happens before the container starts, so a read-only
window does not prevent it. The guess is that this single fact drives most
of the design below.

## The two windows that matter

Two roles, and a front always has both.

- **Config source** — dev-playbook at published state, read-only. What the
  eight symlinks point into and where `standards/` is found. Every front
  gets it, identically.
- **Work checkout** — the repository the front is there to change, on the
  front's branch, read-write. The only window a front may write through,
  and therefore the only thing that survives the container.

The two cases the Goal names are then one difference and nothing else:

| | config source | work checkout |
|---|---|---|
| **front assigned to another repository** | dev-playbook, read-only | that repository |
| **front assigned to dev-playbook** | dev-playbook, read-only | dev-playbook, a second and separate copy |

In the second case the container holds two directories named dev-playbook,
and they are separate copies: an edit in the work checkout does not appear
in the config source. That is the point rather than an accident — the
config source answers "what does the published version say", so it must
not show the front its own uncommitted work.

Two smaller windows complete the set: the subscription credential, and a
one-line file carrying a port so the agent's own hook events reach this
machine's measurement store instead of dying with the container.

## What the work checkout is called

The directory holding the work checkout is named for its repository, not
for the front. `canonical_repo_name` derives a repository's name from the
directory holding `.git`, and same-repo resolution
([Same-Repo Resolution](/docs/decisions/0009-same-repo-resolution.md))
compares a citation's first segment against that name. A checkout at a
directory named for the front would silently break every same-repo citation
inside it.

## Where Sandcastle collides

Sandcastle opens windows of its own choosing, because that is how it gets a
front's commits back: it mounts the host worktree and the host `.git`
read-write. Both are the real directories, not copies, and that is the
collision.

**The restamp reaches the real repository.** Every window Sandcastle opens
carries the SELinux suffix, so the repository's own directories are
restamped and stay restamped after the container exits.

**The shared `.git` widens what a front can reach.** Worktrees share one
`.git` with the main checkout. A front given that directory read-write can
write to every branch and every other worktree, not only its own. This is
the finding that matters most, because it contradicts the prototype's
recorded blast radius, which was measured against a different window
layout.

**The work checkout lands at a fixed path.** Sandcastle mounts it at a
directory not named for the repository, which is what the section above
says must not happen.

## The guess at a resolution

Point Sandcastle at a throwaway clone of the work repository, made fresh
for the lap, and let it open all the windows it likes inside that.

Every window then addresses a copy: the restamp lands on a directory that
is deleted at the end of the lap, and the clone carries its own private
`.git`, so a front reaches its own branch and nothing else. One
configuration line answers two of the three collisions. The third, the
fixed path, is answered separately by opening a second window onto the same
host directory at a path named for the repository.

The clone is made without hard links. A clone taken on one machine shares
file contents with its source by default, and the restamp would reach the
real repository through that sharing.

This is a guess. It is read from Sandcastle's source and has not been run.

## What the round trip settled

The first experiment ran the clone half of the resolution with no container
and no driver, so that a failure would point at git rather than at anything
else. [`front-clone`](/scripts/front-clone) is the plumbing it produced, and
`tests/dev_playbook/test_front_clone.py` holds its assertions. Four things
are now known rather than guessed.

**The commits travel by fetch, and the real repository pulls them.** Git
refuses a push into a branch that is checked out, so the clone cannot push.
The real repository fetches `branch:branch` from the clone instead, without
force, which means a branch something else moved meanwhile is rejected as a
non-fast-forward rather than overwritten.

**The sharing is real and the flag prevents it.** A default local clone of
dev-playbook shares 318 object files with its source — one file on disk under
two names, which is how the SELinux restamp would reach the real repository.
The same clone taken with `--no-hardlinks` shares none. The plumbing verifies
this by comparing inodes after every clone, because the flag being passed and
the sharing being absent are two different claims.

**The front's branch exists only in the clone until the commits arrive.** A
lap that never finishes leaves nothing half-started in the real repository.

**Uncommitted work is the one loss git cannot undo.** Everything else the
round trip moves is a commit, and a commit transfers with its whole ancestor
closure or not at all. So a clone holding any uncommitted change is refused
and left on disk to be read, rather than closed and deleted.

## Open

- **What Sandcastle does inside a clone.** The round trip above was driven by
  hand. Sandcastle fast-forwards a branch from `origin` where it judges that
  safe, and in a clone `origin` is the real repository rather than GitHub.
  What it does there is still unknown, and only a run with Sandcastle in the
  loop answers it.
- **Whether the image survives the move.** The eight symlinks are baked at
  image build time and point at an absolute path that Sandcastle fixes
  differently. Changing it is mechanical; the failure mode if it is wrong
  is the silent one, a front that starts with no skills.
- **Whether a shared SELinux label matters.** Sandcastle labels every
  window as shared, where the prototype labeled them private. With every
  window addressing a throwaway copy the difference may not signify. It is
  recorded rather than resolved.
- **What bounds a stranded container.** The prototype set a deadline podman
  enforces from inside, so a container outlives neither its lap nor a
  driver killed outright. Sandcastle cleans up only when the driver exits
  in an orderly way.

## Acronyms

None.
