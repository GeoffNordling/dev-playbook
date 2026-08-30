---
type: Survey
title: Sandboxed headless Claude
description: What the sandbox prototype is, how its fence works, what it found on this machine, and the defect to fix next time
---

# Sandboxed headless Claude — prototype

Run a headless Claude agent inside a podman container, on subscription billing,
with a fence a confused agent cannot cross.

This is a prototype for learning. It works; do not ship it — see §8. The design
it is being replaced by is [Sandboxed agent design](/sandbox_probe/SPEC.md);
where the two disagree, the spec wins.

---

## 1. Goal

One agent, working inside a clone of `dev-playbook`, talking to Anthropic,
billing the subscription.

The agent has the user's usual configuration — skills, rules, agents, hooks —
and can edit and commit in the repo. It cannot reach anything else on the
machine, and it cannot reach GitHub.

## 2. How the fence works

The agent inside a container sees a complete filesystem — home folder, `/usr`,
`/etc` — but none of it is the host's. The host's `~/workspace`, `~/.ssh`, and
personal files do not exist in that process's view.

Host files get in only by being mounted: one named host folder appears at one
chosen path inside. The mount list is therefore the security surface, and it is
short enough to check by eye. `podman.container_argv()` builds that list and
runs nothing, so the fence can be printed and read before it is trusted.

### Mount copies, never originals

Every mount is a copy of the thing it stands for: a throwaway clone of the
repo, and a copy of `.credentials.json`.

SELinux tags every file, and a container may read only files tagged
`container_file_t`. The `:Z` suffix on a mount retags the host file so the
container can read it, and leaves it retagged. A read-only mount does not
prevent this, because the retag happens before the container starts. A host
program that expects the old tag can then be denied its own file.

The agent also writes. Inside a copy, a confused run costs `rm -rf` of the copy.

`restorecon -RvF <path>` puts a tag back, but the copies rule needs no repair.

The clone is made with `git clone --no-hardlinks`. A clone on the same machine
shares file contents by default, and the `:Z` retag would reach the real repo
through that sharing.

### A mount is a window onto the host disk

Files the agent writes through a mount land on the host disk immediately and
survive the container. Files it writes anywhere else die with the container.
The clone is the only writable mount, so it is the only thing a run leaves
behind.

### The fences

1. **Files shared** — what the agent can touch on the machine.
2. **Credentials handed in** — what the agent can touch in the world.

The container does not constrain the second. An agent with a GitHub token can
force-push from inside a container. This prototype hands in no GitHub
credential.

### Two locks on two layers

`--dangerously-skip-permissions` is Claude's rule about itself. A headless run
has nobody to ask for approval, so without the flag every edit is refused and
the agent reports it could not do the job. The `rw` versus `ro` mount mode is
the kernel's rule.

Turning the first off is safe only because the second is the real fence.

## 3. Scope

### In

- The `dev-playbook` repo, mounted read-write, including `dotfiles/`.
- The `claude` program.
- The subscription login.
- Outbound network.
- The user's skills, rules, agents, and hooks configuration.

### Out

- Any GitHub credential. The agent cannot push, fetch, pull, or clone.
- Any host file outside the mounted repo.
- Restricting which hosts the container can reach.
- The real module at `dev-playbook/src/dev_playbook/sandbox/`. See §8.

### Blast radius

Files in one cloned repo, recoverable with `git checkout .` or a fresh clone.
Nothing else on the machine or on GitHub is reachable.

## 4. Billing

The run must draw on the subscription, never the metered API.

In non-interactive mode a configured API key is always used when present,
silently. So the launcher refuses to start if any of these is set:

```
ANTHROPIC_API_KEY              CLAUDE_CODE_USE_BEDROCK    ANTHROPIC_PROFILE
ANTHROPIC_AUTH_TOKEN           CLAUDE_CODE_USE_VERTEX     ANTHROPIC_FEDERATION_RULE_ID
ANTHROPIC_BASE_URL             CLAUDE_CODE_USE_FOUNDRY    ANTHROPIC_ORGANIZATION_ID
```

It also refuses if a settings file carries `apiKeyHelper`, `awsAuthRefresh`, or
`awsCredentialExport`, which mint or redirect a credential.

`CLAUDE_CODE_OAUTH_TOKEN` is safe — it is a subscription credential. `--bare`
skips the login and demands an API key, so it is never passed.

`billing.py` is the only safety-critical logic here, and the only module with a
test file.

### How a run reports which account it billed

Run with `--output-format stream-json --verbose`. Claude writes one JSON object
per line. The `init` line carries `apiKeySource`, `session_id`, `cwd`, `model`,
`permissionMode`, `tools`, `agents`, and `skills`. A subscription run reports
`apiKeySource: "none"`.

Plain `--output-format json` does not carry that field.

## 5. Decisions

### Podman, not Docker

Docker is the better tool in general: a larger ecosystem, Compose, and a
desktop product for Mac and Windows. None of that applies to running one
container to completion on a Linux box.

For this narrow case podman is simpler. It is already installed and working
with SELinux here, it is rootless by default so it leaves no root-owned files
in the repo, and there is no background service to configure.

Switching later is cheap — the two share a CLI and an image format, so the
recipe file carries over.

### Bake the image, do not share the binary in

The container needs `git` installed regardless, so an image is being built
either way. Adding `claude` to the recipe is one more line, and one method is
simpler to maintain than two.

`COPY claude /usr/local/bin/claude` needs the 214 MB binary inside the build
context, which is the repo root, so `.gitignore` carries `/claude` to keep it
out of the repo.

### Fedora base image

`claude` here is a single ELF binary compiled against the host's Fedora
libraries, so the base image has to carry those libraries.

`sync-dotfiles` itself has no opinion — nothing under
`dev_playbook.dotfiles.sync` reads `/etc/os-release`, so the stow step would
run on any base. The hooks do have one. `measure-event` records only on the
Fedora primary, and detects it by reading `/etc/os-release` itself:

```python
if not on_fedora():
    return
```

A Fedora base is what makes that guard pass inside the container, so the
choice of image decides whether a sandboxed session is measured at all.

### Mirror the host paths

The user's configuration is symlinked out of the repo. `~/.claude/skills`
contains exactly:

```
../workspace/dev-playbook/dotfiles/dot-claude/skills
```

That path is relative, resolved from the folder holding the link
(`/home/geoff/.claude/`), giving
`/home/geoff/workspace/dev-playbook/dotfiles/dot-claude/skills`.

So inside the container: set `HOME=/home/geoff` and mount the repo at
`/home/geoff/workspace/dev-playbook`. Mount it at `/work` instead and every one
of the links dangles.

### Reproduce the configuration with the real script, at build time

Run `dev-playbook/scripts/sync-dotfiles` as a step in the `Containerfile`. It
uses `stow`, so it builds the whole `~/.claude/` layout. Using the real script
keeps the sandbox identical to the host by construction, with no second
definition to drift.

Doing it in the build rather than in a container means the links are already in
the image when a run starts. Nothing is handed from one run to the next, so
there is no shared directory between them — which is what closes the ownership
defect this prototype originally exposed.

`settings.json` is a symlink like the rest, stowed from
`dotfiles/dot-claude/settings.json` — one shared file, so what the sandbox
reads is byte for byte what the host reads.

### Hand in the subscription credential as a file

Copy `~/.claude/.credentials.json` to a temporary directory and mount the copy
read-only. The temporary directory is deleted when the container exits, so the
copy exists only while a run is in flight.

### Git works locally, not remotely

`commit`, `branch`, `diff`, `log`, `stash`, `reset`, and `checkout` all work —
they read and write the `.git` folder inside the repo. Only `push`, `fetch`,
`pull`, and cloning from a URL fail, for want of a credential.

### A four-hour ceiling

`TASK_TIMEOUT = 4 * 60 * 60` is passed to `podman run --timeout`. It exists to
end a container that survived a `kill -9` of its runner (§6.5), and is
deliberately past anything a real task would reach. A cap on how long work may
take is a different decision, and should say why it stopped rather than kill
silently.

## 6. Facts

### 6.1 The machine

Verified 2026-08-27.

| Thing | Value |
|---|---|
| Podman | 5.8.4, rootless, `crun` runtime, `netavark` networking |
| Docker | not installed; `/usr/bin/docker` is a shim that execs podman |
| `claude` | single ELF binary, 214 MB, `~/.local/share/claude/versions/` |
| Node | present on host, not needed — this is the native installer |
| Subscription login | `~/.claude/.credentials.json`, 509 bytes, mode 600 |
| `CLAUDE_CODE_OAUTH_TOKEN` | not set |
| GitHub token | `~/.config/gh/hosts.yml`, 94 bytes, mode 600 |
| `GH_TOKEN` / `GITHUB_TOKEN` | not set in the environment |
| git credential helper | none configured |
| SELinux | Enforcing — a bind mount needs `:Z`, which retags the host file |
| Internet | available |

The GitHub token is in one unmounted file, with nothing in the environment and
no credential helper, so denying GitHub access is a matter of omission rather
than configuration.

### 6.2 Billing works from inside

`apiKeySource: "none"` on the init line, with the credential copy mounted
read-only. The subscription is billed.

### 6.3 The configuration reproduces

`sync-dotfiles` runs as the last build step and reports `stowed 13 link(s)`. A
run's init line then lists 12 agents and 72 skills — the user's own — with the
clone as the only mount.

The host-compiled `claude` binary runs on the Fedora base image.

### 6.4 Ownership comes back right

`--userns=keep-id` makes a file the agent writes through a mount come back
owned by `geoff`. `run-task` proves it: the agent writes `NOTES.md` in the
clone, and `git status` on the host reports `geoff  ?? NOTES.md`.

It does not apply to a directory podman creates for a missing mountpoint. That
only reaches the host disk if the missing mountpoint is itself inside a
host-backed mount, so mounting nothing at `/home/geoff` is what keeps it inside
the container.

### 6.5 `kill -9` on the runner strands the container

`--rm` deletes the container when the command inside exits. It does not fire
when the runner is killed with `SIGKILL`, because nothing runs cleanup code on
`SIGKILL`. Measured:

| Signal to the runner | Container |
|---|---|
| `SIGINT` | gone |
| `SIGTERM` | gone |
| `SIGKILL` | `Up 3 seconds` |

A stranded container keeps running with every mount attached, including the
copy of the login, and Claude inside keeps billing.

`podman run --timeout N` is the fix. Podman enforces the deadline from inside,
so it still works when the runner is dead. With `--timeout 10` and the runner
killed, the container was fully gone at +10s.

`check-cleanup` asserts both halves, including that `SIGKILL` *does* strand the
container, so a change in podman's behaviour is caught.

Untested: killing the runner breaks the pipe Claude writes to, and a program
writing to a broken pipe usually dies at once. If so the real exposure is
seconds. The ceiling is kept anyway.

### 6.6 Reading the stream

What the parser has to allow for:

- **The `init` line is not the first line.** A session with `SessionStart`
  hooks announces each one first, as
  `{"type":"system","subtype":"hook_started",...}`. `stream.parse_init` finds
  the message by identity, not by position.
- **A failed run still exits zero.** Podman reports success whether the agent
  did the job or refused it. The `result` line's `subtype` and `is_error` are
  the only place failure shows.

## 7. Fix next time

This is not a fence problem; it is something the prototype exposed and left
standing.

### 7.1 The events database is created fresh and thrown away

**What happens.** `dotfiles/dot-claude/hooks/measure-event` appends every hook
event to `~/.local/share/claude-measure/events.db`. Inside the container `HOME`
is `/home/geoff`, which nothing is mounted at, so the sandbox writes its events
to a path in the container's own filesystem:

```
/home/geoff/.local/share/claude-measure/events.db
```

That file is created by the run, holds only that run's events, and dies with the
container. The host's real database at
`~/.local/share/claude-measure/events.db` never sees a sandboxed run.

**What it costs.** Every usage report and measurement query is blind to work
done in the sandbox. If sandboxed runs become the normal way to work, the
measurement store stops describing the machine.

**Fix direction.** §8 says hooks inside the sandbox should reach the host
database. The decision and the options behind it are in
[Sandbox measurement options](/sandbox_probe/MEASUREMENT-OPTIONS.md): a live
TCP writer on the host, reachable from inside the container, with the post-run
dump kept as the fallback. Both halves are built, and `run-task` now carries
them: a real sandboxed agent's own hooks wrote rows 75394 to 75397 of
`~/.local/share/claude-measure/events.db` on 2026-08-29, between the rows of
the host session that launched it.

Whatever the answer, do not hardcode “sandbox means no hooks.”

## 8. After the prototype

**Refactor before use.** This is a prototype for learning: mostly check
commands. The checks earned their keep by finding the defects, but the shape is
wrong for a thing to depend on. Consolidate it before building on it, against
[SPEC.md](/sandbox_probe/SPEC.md) rather than against what is here — in
particular the probe still runs one repo mount where the spec calls for a
read-only config source and a separate writable work checkout.

**The real module** lives at `dev-playbook/src/dev_playbook/sandbox/`. Its API
covers one thing — launching one sandboxed Claude session. No database; a caller
that wants history writes its own. No entanglement with the rest of the repo.

**GitHub access.** Deferred; the user has an approach in mind. Until then the
sandbox has no GitHub credential.

Once it has one, work leaves the sandbox as a pushed branch rather than as a
directory to inspect afterwards. The clone is then thrown away instead of
reconciled, and the mount stays a copy for real work as much as for this
prototype.

**Network egress restriction.** Deferred.

## 9. Running it

`python3 -m probe <command>`, from `sandbox_probe/`. Standard library only.

| Command | What it does |
|---|---|
| `build-image` | build the image from the `Containerfile` |
| `check-tools` | git, stow, jq, python3, uv all report a version inside |
| `check-fence` | the host filesystem is not visible from inside |
| `check-claude` | the host-compiled `claude` binary runs inside |
| `check-billing` | the run drew on the subscription, not the API |
| `check-config` | Claude loaded the user's skills, agents, and hooks |
| `run-task` | give the agent a real prompt in the clone, and record its hook events on the host |
| `check-cleanup` | what a killed runner leaves behind, and that it ends |
| `check-host-tcp` | a message from inside reaches a listener on the host |
| `check-measure-sink` | the measurement path alone, on made-up events, spending no quota |

Everything up to `check-claude` needs no credential and spends no quota;
`check-billing` is the first command that costs anything.

The unit tests run from here too — `uv run pytest tests` — and not through the
repo's `make test`, which pins `testpaths` to `["tests"]` at the root.

**Re-run `check-fence` after changing any mount list.** `check-config` and
`run-task` add a mount, which is how a fence gets widened by accident. The
check is the forbidden-path list, not an empty home directory: the image builds
`.claude`, `.agents`, `.bashrc.d`, `.cache`, and `workspace`, so a populated
`/home/geoff` is expected. What must not appear is `~/.config/gh`, `~/.ssh`,
`~/.aws`, or the host's `~/.local/share/claude`.

### The files

```
sandbox_probe/
  Containerfile          the image recipe
  probe/
    podman.py            mounts, argv assembly, build, run, cleanup
    billing.py           refuse to start if the run could bill the API
    stream.py            read the JSON the run writes back
    commands.py          one function per command above
    __main__.py          `python3 -m probe check-billing`
  tests/
    test_billing.py
  scratch/               throwaway clone; gitignored
```
