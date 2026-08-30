---
type: Guide
title: Sandboxed agent design
description: The prescribed build-and-run design for a sandboxed Claude agent — one image, four mounts, and the path layout that makes one instruction work inside and outside podman
---

# Sandboxed agent design

This document prescribes how a sandboxed Claude agent is built and run. It
replaces the staged prototype described in
[Sandboxed headless Claude](/sandbox_probe/NOTES.md), which stays as the record
of what was measured.

The problem this design solves: an instruction you write once must work whether
the agent runs inside podman or outside it. The path layout below is chosen for
that, and the grid near the end shows the layout holding in all four situations.

## Constraints

Every agent reads dev-playbook, whatever repo it is working on, for two
separate reasons.

**Configuration, read by the harness.** The 8 entries of `~/.claude/` — among
them `skills`, `rules`, `agents`, `hooks`, and `settings.json` — are symlinks
into `/dotfiles/dot-claude/`. Claude Code follows them at startup, before the
agent does anything. Without dev-playbook at the path the links name, they
dangle and the agent starts with no skills, no rules, and no hooks.

**Documentation, read by the agent.** Governing documents live in dev-playbook
and are cited from anywhere: the global `CLAUDE.md` tells an agent to read
`/standards/index.md` before its first task, whichever repo it is in. Here the
agent opens the file itself, mid-task, and a missing dev-playbook shows up as a
failed read.

So a podman agent runs in one of two scenarios:

1. It reads dev-playbook and writes to a different repo.
2. It reads and writes dev-playbook.

One cross-repo citation is supported: from the other repo to dev-playbook. A
citation to any third repo — for example `~/workspace/mission-control/` in the
`log-friction` skill — points at a path no container mounts, and fails.

A job that violates these constraints runs outside podman. No work is planned
to widen them. In particular, an agent never writes to two repos at once.

## Two halves: build and run

- **Containerfile** — the recipe. One file, a list of steps.
- **Image** — what the build produces. A frozen, read-only snapshot of a
  set-up machine.
- **Container** — one running copy started from the image.

The build runs before every launch, but it does almost nothing when nothing has
changed — 0.65 s. Four agents working at once are four containers started from
one image, not four separate setups.

## Build

### The recipe

The recipe is `/sandbox_probe/Containerfile`. It is not reproduced here — read
it there, where the build reads it. Every step carries a comment saying what it
does and why.

Its shape: install the four tools `sync-dotfiles` checks for, install `uv`,
create the home directory, copy the `claude` binary in, switch to UID 1000, copy
in the three trees `sync-dotfiles` needs, and run `sync-dotfiles`.

Two steps in it exist for reasons the rest of this document explains. `USER 1000`
must precede anything created in the home directory, because root-owned files
there would be unwritable by the agent. The three `COPY` lines must precede the
`RUN`, because they are what makes podman rerun it.

### Why the setup is in the build

Setting the config up at run time means keeping it somewhere between runs, and
a directory shared by two containers is where the ownership defect in
[NOTES.md](/sandbox_probe/NOTES.md) came from. Building it into the image
removes the handoff: nothing passes between runs, so there is nothing to share
and nothing to clean up.

### Build before every run

The launcher builds the image every time it starts a container. Not once, not
when something looks stale — every time.

Podman does not watch the filesystem. `podman build` is a command, and the
comparison that decides whether a step is reused happens only while that
command runs. An image nobody rebuilds never changes, however far the host
moves on. Building every time turns that comparison into something that
happens on its own.

That is what keeps two things current without anyone tracking them: the
`claude` binary, which is baked into the image, and the set of dotfile links,
which changes when a ninth name appears under
`/dotfiles/dot-claude/`.

It is affordable. Measured on this machine, 2026-08-28, on the 11-step recipe:

| Build | Time |
|---|---|
| Nothing changed | 0.65 s |
| Dotfiles edited | ~1 s |
| Claude Code updated — steps 5 to 11 rerun, 214 MB copied | 1.64 s |
| Cold, nothing reused (`--no-cache`) | 13.5 s |

The Claude Code figure is a real measurement, taken by staging 2.1.250 in place
of 2.1.251. It is the worst realistic case: only the Fedora base, the `dnf`
install, and the `uv` install are reused.

Treat the cold figure as tens of seconds rather than a constant — an earlier
cold build measured 38 s, and the difference is network and `dnf` metadata, not
the recipe. It is paid once.

**The work must be committed.** The image copies the working tree, but mount 1
supplies dev-playbook at its main checkout's HEAD, and mount 1 is what the
agent reads at run time. An uncommitted edit is therefore invisible to the
agent. No check enforces this; committing before a run is assumed.

### The COPY lines are the change detector

Podman decides whether to reuse a step from the step's **text**, not from what
the step does. `RUN sync-dotfiles` is unchanging text, so on its own podman
would reuse it forever and never notice the dotfiles changed.

`COPY` behaves differently: podman hashes the contents being copied. Change
anything under `/home/geoff/workspace/dev-playbook/dotfiles/` and that step
stops matching, which rebuilds it and every step below it — including
`sync-dotfiles`.

So the `COPY` lines must stay above the `RUN`. Without them the baked config
goes stale silently.

### What gets baked, and what does not

`stow` links the top level of `/home/geoff/workspace/dev-playbook/dotfiles/dot-claude/`,
which is 8 names: `agents`, `CLAUDE.md`, `hooks`, `rules`, `settings.json`,
`skills`, `statusline.sh`, `workflows`. Each becomes one symlink, for example:

```
/home/geoff/.claude/skills -> /home/geoff/workspace/dev-playbook/dotfiles/dot-claude/skills
```

The image holds the pointer, not the content. The content is read at run time
through the read-only mount, so an edited skill reaches the agent whether or
not the image was rebuilt. Only a ninth name at that top level changes the set
of links, and that alone would need the image rebuilt.

The `COPY` of `dotfiles/` cannot tell those apart — it hashes contents, so any
dotfile edit rebuilds the step. That is more rebuilds than strictly needed, at
about a second each. Since the launcher builds every time anyway, the cost is
the difference between 0.65 s and 1 s, and the safety is that a ninth name can
never be missed.

### The build context

A build may copy only from the one directory it is pointed at — its build
context. The recipe copies `src/`, `scripts/`, and `dotfiles/`, which sit at
the repo root, so the context is the repo root:

```
podman build --tag sandbox-probe --file sandbox_probe/Containerfile <repo root>
```

`--file` and the context are separate arguments, so the recipe stays in
`sandbox_probe/` while the build reads from the root. `podman.build_image()`
assembles exactly that.

Two consequences. The `claude` binary is staged to the repo root rather than to
`sandbox_probe/`, so `.gitignore` excludes `/claude`. And the whole repo would
otherwise enter the context, so `/.containerignore` excludes `.git`,
`.claude/`, the Python caches, and `sandbox_probe/scratch/`.

### Verified

Built and inspected on 2026-08-28:

- The build runs `sync-dotfiles` at step 11 and reports `stowed 13 link(s)`.
- The image carries all 8 links in `/home/geoff/.claude/`, owned by `geoff`.
- `uv` fetches its own Python during a cold build, so the `requires-python
  >= 3.14` header in `/scripts/sync-dotfiles` is satisfied without a Fedora
  package.
- `check-fence` reports none of the forbidden host paths reachable.

One expectation changed. The prototype treated a non-empty `/home/geoff` as a
sign that a mount had leaked. The home directory is now legitimately non-empty
— it holds `.claude`, `.agents`, `.bashrc.d`, `.cache`, and the baked
`workspace` — because the image builds them. The fence check is the list of
forbidden paths, not the emptiness of the home directory.

## Run

One container per agent, started from the shared image. Each container gets
four mounts and nothing else from the host.

### Mount 1 — the config source

```
host:      a copy of dev-playbook's main checkout at its current HEAD
container: /home/geoff/workspace/dev-playbook
mode:      read-only
```

This is what the 8 baked symlinks point into, and where `standards/`,
`CONTEXT.md`, and `software-factory/` are found. Every container gets it, in
both scenarios. All agents may share one copy, because none writes to it.

**It is taken from the main checkout at current HEAD.** This is prescribed, not
incidental: the path is the one an agent reads to answer "what does the
published version say", so the content behind it must actually be published
state.

### Mount 2 — the work checkout

```
host:      a throwaway clone of the work repo, on this agent's branch
container: /home/geoff/work/<repo-name>
mode:      read-write
```

The only mount that differs between agents, and the only writable one. An agent
working on dev-playbook gets `/home/geoff/work/dev-playbook`; one working on
another repo gets `/home/geoff/work/<that-repo>`.

**`<repo-name>` is load-bearing, not decoration.**
`dev_playbook.gitrepo.canonical_repo_name` derives the repo's name from the
directory holding `.git`, and
[cross-references.md](/standards/knowledge-organization/cross-references.md) resolution compares a
citation's first segment against that name. A clone at `/home/geoff/work/agent-1`
would silently break every same-repo citation in it.

The path must not sit under `/home/geoff/workspace/`. Nesting mount 2 inside
mount 1 is possible in Linux but needs the mountpoint to already exist inside a
read-only mount, which is the podman directory-creation behaviour that produced
the UID 524288 defect. Kept flat instead.

### Mount 3 — the credential

```
host:      a copy of /home/geoff/.claude/.credentials.json in a temp directory
container: the path Claude reads it from
mode:      read-only
```

The temp directory is deleted when the run ends, so the copy exists only while
a run is in flight.

### Mount 4 — the measurement sink

```
host:      a one-line file in a temp directory, carrying the receiver's port
container: /home/geoff/.local/share/claude-measure/sink
mode:      read-only
```

The measurement fix, per
[Sandbox measurement options](/sandbox_probe/MEASUREMENT-OPTIONS.md): the
launcher runs a receiver bound to the host's `127.0.0.1`, and `measure-event`
sends each hook event to it whenever this file is present. To make the host's
loopback reachable from inside, the run also gains
`--network=pasta:--map-host-loopback=169.254.1.2`.

The file is generated fresh per run and dies with its temp directory, like
mount 3. Prescribed ahead of implementation; `check-host-tcp` proved the
container-to-host path it depends on.

### Copies, never originals

Every mount is a copy of the thing it stands for. SELinux is Enforcing here, so
a bind mount needs the `:Z` suffix, which retags the host file and leaves it
retagged. A read-only mount does not prevent the retag — it happens before the
container starts.

Clones are made with `git clone --no-hardlinks`. A clone on the same machine
shares file contents by default, and the retag would reach the real repo
through that sharing.

### What survives

The container's filesystem is deleted when the container exits. The only thing
that survives is what the agent wrote through mount 2, because a mount is a
window onto the host disk.

Nothing is handed from one run to the next. There is no shared scratch
directory.

## The four situations

Two dimensions: inside or outside podman, and whether the work repo is
dev-playbook or another repo.

| | work repo = dev-playbook | work repo = other |
|---|---|---|
| **outside podman** | config source `/home/geoff/workspace/dev-playbook`, **writable** · work checkout is a worktree beneath it | config source `/home/geoff/workspace/dev-playbook`, writable · work checkout `/home/geoff/workspace/<repo>` |
| **inside podman** | config source `/home/geoff/workspace/dev-playbook`, **read-only copy** · work checkout `/home/geoff/work/dev-playbook` | config source `/home/geoff/workspace/dev-playbook`, read-only copy · work checkout `/home/geoff/work/<repo>` |

Two roles move across the grid:

- **Config source** — the dev-playbook copy the `~/.claude/` symlinks point
  into, and the one holding `standards/`. Always dev-playbook, always at
  `/home/geoff/workspace/dev-playbook`.
- **Work checkout** — the writable repo the agent is there to change. Always
  the session's working directory.

That is the rule an instruction author relies on: **name the config source by
its absolute path, and name the work checkout as "your checkout" — never as a
literal path.**

### The one asymmetry

Outside podman the config source is writable. An agent that ignores same-repo
resolution edits the main checkout silently.

Inside podman it is read-only. The same mistake raises a permission error. The
failure is loud, which is the better direction.

### Same-repo resolution across the grid

The canonical rule in
[cross-references.md](/standards/knowledge-organization/cross-references.md#same-repo-resolution)
holds in all four cells. `~` expands to `/home/geoff` in every one, because
`HOME=/home/geoff` is set in the image.

`ref-lint` behaves identically inside and out. `resolve_target` in
`/src/dev_playbook/filegraph/graph.py` compares a citation's first segment
against `canonical_repo_name`, which reads the directory holding `.git`. A
clone at `/home/geoff/work/dev-playbook` yields `dev-playbook`, so the
substitution fires.

One divergence remains, and the sandbox prompt covers it. The canonical rule
names where it applies as "its main checkout or any of its worktrees". A
sandbox work checkout is a plain clone — neither. Read strictly, an agent
concludes the rule does not apply to it, does not substitute its own checkout,
and tries to edit the read-only config source. The prompt below states the
substitution directly rather than relying on the agent to extend the rule.

## The sandbox prompt

The bottom row of the grid is the row an agent cannot work out for itself. The
top row is the layout it already knows. In the bottom row it wakes up in a
confusing file system, which may hold two directories named dev-playbook. A
short preamble brings it up to speed:

1. **You are inside a podman container**, alone, running once to completion.

2. **`/home/geoff/work/<repo-name>` is your checkout, and it is writable.**
   Your repo, on your branch. Resolve same-repo paths against it. It is the
   only writable window, so it is the only thing that survives the container.

3. **`/home/geoff/workspace/dev-playbook` is the config source, and it is
   read-only.** A copy of dev-playbook's main checkout at HEAD. Your skills,
   rules, and hooks are symlinked into it, read from it as required, and an
   absolute `/home/geoff/workspace/dev-playbook/...` citation resolves there.

4. **You may be assigned to edit dev-playbook itself.** In that case you have
   two copies of it. `/home/geoff/work/dev-playbook` is the writable one —
   your checkout, the one you change. `/home/geoff/workspace/dev-playbook`
   is the read-only one — the reference copy the harness reads. They are
   separate clones; an edit in one does not appear in the other.

5. **You have Git, but no GitHub.** `commit`, `branch`, `diff`, `log`,
   `reset`, and `checkout` work. `push`, `fetch`, `pull`, and cloning from a
   URL do not.

6. **Everything outside your checkout is discarded** when the run ends — `/tmp`,
   the home directory, anything installed. Put what matters in the checkout.
   Do not bother cleaning up the rest.

## Carried over unchanged

These hold as recorded in [NOTES.md](/sandbox_probe/NOTES.md) and are not
revised here:

- The launcher refuses to start if any environment variable or settings key
  could route the run to metered billing.
- `podman run --timeout` bounds a container whose runner was killed with
  `SIGKILL`, which `--rm` does not clean up.
- The run is read with `--output-format stream-json --verbose`; the `init`
  line is found by identity, not position, and a failed run still exits zero.
- `--userns=keep-id` makes files the agent writes through a mount come back
  owned by `geoff`.

## Not covered

- **GitHub access.** Deferred. Until a credential is handed in, work leaves the
  sandbox only through mount 2.
- **Network egress restriction.** Deferred.
- **Writing to two repos at once.** Ruled out by the constraints above.
