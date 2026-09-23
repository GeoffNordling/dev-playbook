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

Six bounds are settled — three limitations the user accepts, and three rules
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
absence of a metered credential is asserted rather than assumed. No such
credential exists on this device today; the check is there so that stays
true. Four surfaces could carry one: the live environment, the shell
startup files, `~/.claude/settings.json`, and the repository's
`.claude/settings.json`. `billing-lint` reads all four at the commit gate
and refuses rather than reporting a finding; the same check is to run on
this device immediately before a lap launches, once a driver exists to
carry it. A check
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

**Sandcastle is never forked or patched.** It is used as published, through
the extension points it offers. Any mismatch between Sandcastle and the
workspace is closed either by a plug-in of our own that Sandcastle accepts,
or by changing the workspace standards. A fork would have to be maintained
for as long as the set uses Sandcastle, and the user declines that cost.

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

## The five problems

Every problem the set has met carries one name, used in conversation and in
every member. The user tracks the work at the level of this table.

| Problem | What goes wrong | Solution | Status |
|---|---|---|---|
| **Shared history** | Sandcastle opens the real `.git` to the front, so a front can delete other branches, other worktrees, and the user's unpushed commits | The throwaway copy | Solved, proven by experiment two |
| **Relabel** | The SELinux restamp permanently changes the label on the real files | The throwaway copy | Solved, proven by experiment two |
| **Booby trap** | Something a front plants in its copy's git settings runs on the host when host-side git later works in the copy | Harden `front-clone` | Fix approved, not built |
| **Workspace collision** | Sandcastle puts the repository at `~/workspace` itself, so the repository is misnamed and dev-playbook has no place | Option A or option B | Neither tested |
| **Hook logging** | The user's Claude Code hooks log every event to a database, and must keep doing so from inside the sandbox | The prototype's port file, carried over | Not tested under Sandcastle |

## Where Sandcastle collides

Sandcastle opens windows of its own choosing, because that is how it gets a
front's commits back: it mounts the repository it is pointed at, `.git`
included, read-write. Pointed at the real repository, those are the real
directories, and three of the five problems follow.

**Shared history.** Worktrees share one `.git` with the main checkout. A
front given that directory read-write can write to every branch and every
other worktree, not only its own. Concretely: the user holds unpushed
commits on a worktree `issue-123`, and front A runs
`git branch -D issue-123`, and the commits are gone. Branch protection on
GitHub does not help, because nothing was pushed. This contradicts the
prototype's recorded blast radius, which was measured against a different
window layout.

**Relabel.** Every window Sandcastle opens carries the SELinux suffix, so
the repository's own directories are restamped and stay restamped after the
container exits.

**Workspace collision.** Sandcastle puts the repository at
`/home/agent/workspace`, and forces the agent's home to `/home/agent`, so
the repository sits at `~/workspace` itself rather than in a directory of
its own under it. Both values are fixed in Sandcastle's code
(`SANDBOX_REPO_DIR` in the published package, and the podman plug-in's
`HOME`), and no option changes them. That the word is `workspace` in both
Sandcastle and this workspace is a coincidence. The consequence is drawn
out in [The workspace collision](#the-workspace-collision) below.

## The throwaway copy

Point Sandcastle at a throwaway clone of the work repository, made fresh
for the lap by [`front-clone`](/scripts/front-clone), and let it open all
the windows it likes inside that. Every window then addresses a copy: the
restamp lands on a directory that is deleted at the end of the lap, and the
clone carries its own private `.git`, so a front reaches its own branch and
nothing else. This answers **Shared history** and **Relabel**, and
experiment two proved both.

The clone is made without hard links. A clone taken on one machine shares
file contents with its source by default, and the restamp would reach the
real repository through that sharing.

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

## What the Sandcastle run settled

Experiment two put Sandcastle in the loop: `@ai-hero/sandcastle` 0.12.0,
its podman plug-in, `head` branch mode, pointed at a `front-clone` copy of
a fake repository. A stand-in agent replaced Claude, so the run spent no
tokens. The stand-in is a shell script that reports what it can see, makes
one honest commit, and then misbehaves: it deletes every ref but its own
and plants git hooks and a `core.fsmonitor` command, each of which touches
a marker file at a host path that does not exist inside the container. A
marker appearing therefore proves a command ran on the host. The fake real
repository held a worktree `issue-123` with one unpushed commit, standing
in for the user's own work. A copy of dev-playbook was mounted read-only as
the config source. The harness is throwaway and lives in the session
scratchpad, under `exp2/`.

`head` mode fits the throwaway copy: `front-clone` already checks the
front's branch out in the copy, and Sandcastle's `branch` mode would try
to add a worktree on that same branch and fail.

**The real side came through untouched.** The fake real repository's refs,
worktrees, hooks, local config, and the SELinux label of every file were
identical before and after, and the unpushed `issue-123` commit survived.
So were the labels on the real dev-playbook. Only the copies were
restamped, to `container_file_t`.

**The damage stayed in the copy.** The stand-in deleted every other ref and
planted its hooks in the copy's `.git`, and none of it reached the real
repository.

**Sandcastle mounted copies only.** Inside the container: the copy at
`/home/agent/workspace`, read-write, carrying its own `.git`; the config
copy, read-only, where a write was refused; the stand-in's script,
read-only. Nothing else of the host. The copy's `origin` is the real
repository's host path, which does not exist inside, so a `git fetch` from
inside failed. In `head` mode Sandcastle did not touch `origin` at all.

**The commits came back.** `front-clone close` fetched `front-a` into the
real repository at the SHA the stand-in committed, even though the stand-in
had deleted every other ref in the copy. No container was left behind, and
the copy was deleted.

**The workspace collision is real.** The repo-name code from dev-playbook
(`canonical_repo_name`), run inside the container, returned `workspace`
rather than `mission-control`, and `~/workspace/dev-playbook` did not exist.

**The booby trap is real.** The `core.fsmonitor` command planted in the
copy ran on the host, and the cause is ours, not Sandcastle's: a second run
showed no marker after Sandcastle finished, and the marker appeared when
`front-clone close` ran `git status --porcelain` in the copy. The planted
hooks did not fire only because nothing on the host committed or checked
out in the copy. None of it would have shown in a pull request, since git
never commits or transfers the contents of `.git`.

**Not tested:** Sandcastle's `branch` and `merge-to-head` modes, which run
more git on the host and may trip the booby trap themselves.

## The workspace collision

The workspace standard gives every repository its own directory under
`~/workspace`, with dev-playbook beside it:

```
~/workspace/
    dev-playbook/      ← skills, rules, standards
    mission-control/   ← the repository the front works on
        .git/
        CLAUDE.md
        src/
```

Sandcastle instead empties the repository into `~/workspace` itself:

```
~/workspace/
    .git/              ← mission-control's history
    CLAUDE.md          ← mission-control's instructions
    README.md
    pyproject.toml
    src/
    tests/
```

Two things break. The repository is named `workspace`, because the name is
read from the directory holding `.git` and same-repo resolution
([Same-Repo Resolution](/docs/decisions/0009-same-repo-resolution.md))
compares against it. And dev-playbook has no place: a directory
`~/workspace/dev-playbook` would sit inside the repository's own files, so
the eight `~/.claude/` symlinks dangle and the front starts with no skills,
rules, or hooks, silently.

Sandcastle is never forked or patched (see Constraints), which leaves two
options.

**Option A — change the standards to fit Sandcastle.** dev-playbook moves to
a fixed place of its own outside `~/workspace`, on the user's machine and in
the container alike, and a repository's name is read from the note git keeps
in the copy of where it was cloned from, which needs no network. The cost is
a pass over every standard, skill, and setup step that assumes
`~/workspace/dev-playbook`, and a revision of decision 0009.

**Option B — our own container plug-in.** Sandcastle accepts user-written
sandbox plug-ins (`createBindMountSandboxProvider` is exported), and its own
podman plug-in is one of them, about 300 lines. A plug-in of ours would put
the repository at `~/workspace/mission-control` and the config copy at
`~/workspace/dev-playbook`, so the container matches the user's machine and
no standard changes. The cost is owning that plug-in. Whether Sandcastle
honors a location a plug-in changes is read from its code (the podman
plug-in takes the location from the mounts it is handed) and not yet
confirmed.

## The booby-trap fix

Approved by the user. `front-clone` runs every git command it runs inside a
copy with all of git's known automatic-command points switched off,
without reading what is in them: hooks, `core.fsmonitor`, and whatever
else the specific commands it runs would consult. The step that pulls the
commits back already runs in the real repository and uses the real
repository's own hooks, so it is unaffected. A test plants a trap at every
point, runs `close`, and asserts that no marker appears.

## Hook logging

The user's Claude Code hooks log every event to a measurement database, and
that must continue from inside the sandbox. These are Claude Code hooks, not
git hooks, and the booby-trap fix does not touch them. The `sandbox-probe`
prototype already routed them out through a one-line file carrying a port
(the smaller window described under
[The two windows that matter](#the-two-windows-that-matter)). Whether that
survives under Sandcastle is checked in the first run with real Claude.

## Open

- **Whether the image survives the move.** The eight symlinks are baked at
  image build time and point at an absolute path. Where that path lands
  depends on which option closes the workspace collision; the failure mode
  if it is wrong is the silent one, a front that starts with no skills.
- **Whether a shared SELinux label matters.** Sandcastle labels every
  window as shared (`z`), where the prototype labeled them private (`Z`).
  Experiment two showed the shared label lands only on the copies, so it
  likely does not signify. It is recorded rather than resolved.
- **What bounds a stranded container.** The prototype set a deadline podman
  enforces from inside, so a container outlives neither its lap nor a
  driver killed outright. Sandcastle cleans up only when the driver exits
  in an orderly way.

## Acronyms

None.
