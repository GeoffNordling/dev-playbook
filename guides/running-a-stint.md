---
type: Guide
title: Running a Stint
description: How a launching agent runs an unattended stint with the stint command — what to prepare, the one-time setup and what the image holds, the pre-commit gate every commit runs, the run and its arguments, what comes back to the repository, the stint's folder, the exit codes, and every rule that stops a stint
---

# Running a Stint

A **stint** works one workstream's plan with no person in the loop. Every
agent call runs in a new sealed container, and the only thing that comes
back to the repository is the stint's branch. The `stint` command, from
[`src/dev_playbook/stint/`](/src/dev_playbook/stint/cli.py), runs one stint
from launch to its end. The words stint, principal, iteration, checkpoint,
and segment are
[the repo's terms](/CONTEXT.md#workstreams-and-loops).

## What the stint guarantees

- **The repository is never touched while the stint runs.** The agents work
  on a throwaway copy of it. At the end, the stint's commits come back as
  the new branch `<name>`, at the same SHAs, and the copy is deleted.
- **Every agent reads published dev-playbook.** Each call mounts, read-only,
  a copy of dev-playbook's `main` made at launch, never the stint's own
  branch.
- **The subscription pays.** Before every call, the stint refuses a
  metered credential on the host, in the config copy's settings, in the work
  copy's `.claude/` settings, or in a `.sandcastle/.env`. After every call,
  it refuses one that Claude reports was billed to anything else.
- **Every commit runs the repository's pre-commit gate.** Before each
  agent starts, the call installs the hooks of the work copy's
  `.pre-commit-config.yaml` in the container, so an agent's `git commit`
  runs the same hooks it runs on the host. A consumer repository runs
  dev-playbook's published `playbook-check` at its pinned commit and its
  own hooks, such as `playbook check --local`; dev-playbook runs its own
  hooks from the branch being worked. A hook set only for `pre-push`, such
  as `make-check`, does not run, since nothing is pushed.
- **`make check` runs in the container.** The image holds what the gate
  and the check call: pre-commit, make, Node and npm, and the Chromium
  that Playwright drives.
- **The container holds no GitHub credential.** Only local git works in it,
  and nothing is pushed. The work copy's `origin` is the repository's own
  URL, for the checks that read the GitHub name from it.
- **The hooks keep logging.** Every hook event inside a container lands in
  the host's measurement database.
- **Host git never runs in the copy.** Between calls the stint reads the
  copy as plain files and refuses a symlink on any path it reads.

```text
  the repository           ~/stints/<repo>/<name>/                  a container per call
  ──────────────           ──────────────────────                   ────────────────────
  base ──open──▶  <repo>/          the work copy, branch <name>  ──rw──▶  ~/assignment/<repo>
                  config/          dev-playbook main             ──ro──▶  ~/workspace/dev-playbook
                  siblings/<other>/ <other>'s main               ──ro──▶  ~/workspace/<other>
                  cache/           pre-commit, uv, npm downloads ──rw──▶  ~/.cache
                  calls/, sessions/, review-<n>.md, stint.json
  branch <name> ◀──close── <repo>/, config/, siblings/, and cache/ deleted
```

`<repo>` is the repository's own name, also when `REPO` is one of its
worktrees, because the checks read a repository's name from its folder.

The sibling copies are for the link checks of the pre-commit gate, which
on the host read every repository under `~/workspace/`. The stint copies
each repository the base's files link to as `~/workspace/<other>/`, from
the `main` of its checkout on the host, and mounts it where the host
keeps it. A consumer that links to no other repository gets none. The
cache is the stint's own: every call of the stint shares it, and no other
stint does.

## Before the first stint

Run setup once, and again after `claude`, the dotfiles, or the Playwright
version in dev-playbook's `uv.lock` change, since the image carries all
three:

```bash
stint setup --playbook ~/workspace/dev-playbook --claude ~/.local/bin/claude
```

It installs Sandcastle from the committed lock file and builds the image
`localhost/stint:latest`. It runs on the Fedora machine only, which has
podman. The image holds pre-commit, make, Node and npm, and the Chromium
of the Playwright version that dev-playbook's `uv.lock` pins. A tool the
gate or the check calls that is not in the image, and that uv, npm, or
pre-commit cannot install, fails the call.

## What the repository must hold

The base ref must already hold the workstream folder, with three files:

- `WORKSTREAM.md` — the goal, `## Done when`, and the constraints.
- `PLAN.md` — the tasks, each a `- [ ] ` line at a line's start, in
  segments that end with the exact line `<!-- [ ] checkpoint -->`. Each
  task says how to verify it.
- `PROGRESS.md` — the log each iteration appends to.

The base ref must hold a `.pre-commit-config.yaml`; the stint refuses to
launch without one.

The repository needs a `.gitignore` that covers what its check writes, such
as `__pycache__/`: a call that leaves any file uncommitted stops the stint.
The branch `<name>` must not exist yet.

## Run it

```bash
stint run ~/workspace/mission-control \
  --base main \
  --workstream workstreams/wordcount \
  --check "python3 -m unittest discover -s tests" \
  --budget 5 \
  --name wordcount-1 \
  --home ~/stints \
  --playbook ~/workspace/dev-playbook \
  --model claude-sonnet-5
```

Every argument is required, and none has a default:

| Argument | What it is |
|---|---|
| `REPO` | The repository the stint changes |
| `--base` | The ref the branch starts at; it holds the workstream |
| `--workstream` | The workstream folder, relative to the repository |
| `--check` | The command that must pass after every change |
| `--budget` | The most iterations the stint may spend; at least the plan's open tasks |
| `--name` | The stint's name, and its branch's |
| `--home` | Where stint folders live |
| `--playbook` | The dev-playbook checkout whose `main` the config copy is cloned from |
| `--model` | The Claude model every call runs |

The command prints one line per call and a last line with the reason the
stint ended.

## The calls, in order

- `principal-0` reads the plan and answers `launch`, or why not.
- `iter-1`, `iter-2`, … each do the first unchecked task, check it off, and
  commit.
- At each checkpoint, `review-<n>` reads the segment's commits cold and
  commits nothing, and `principal-<n>`, the same conversation resumed,
  checks off the checkpoint and answers `continue`, `done`, or `stop`.

## What comes back

The exit code says how the stint ended:

| Exit | Meaning |
|---|---|
| `0` | Done: the principal said done, and the branch landed in the repository |
| `1` | Any other end: a stop rule, the principal's `stop`, or a work copy kept |
| `2` | The tool could not run: not set up, a bad argument, or a failed step |

On exit 0 or 1 with the copy closed, the repository has the branch `<name>`
holding every commit the stint made, and the copies and the cache are
deleted. On a stop, the branch holds the work up to the stop. A work copy
that cannot close, such as one holding uncommitted work, is kept in the
folder, and the last line names it.

The stint's folder, `<home>/<repo>/<name>/`, stays:

| File | What it holds |
|---|---|
| `stint.json` | The reason it ended, iterations spent, the branch's last commit, the notes, the principal's context size per call, and each call's session and commits |
| `calls/<call>.json` | One call's record: its session, billing source, tokens, commits, uncommitted files, and answer |
| `calls/<call>.request.json` | What the call asked Sandcastle to run, the prompt included |
| `calls/<call>-setup.log` | Sandcastle's log of the hook install that runs before the agent |
| `calls/<call>.log`, `calls/<call>-probe.log` | Sandcastle's logs of the agent and of the uncommitted-work probe |
| `review-<n>.md` | The reviewer's report for segment `n` |
| `sessions/` | Every agent's session file; the principal's is resumed from here |

## What stops a stint

Each rule is checked in code, and the reason is the last line and
`stint.json`'s `reason`:

| Reason | What happened |
|---|---|
| `not launched: N tasks, budget B` | The plan has more open tasks than the budget |
| `stuck at launch: …` | The principal did not answer `launch` |
| `the principal changed the plan at launch` | `principal-0` committed |
| `iter-k blocked: …` | The iteration reported a blocker |
| `iter-k committed nothing` | The iteration made no commit |
| `iter-k moved a checkpoint marker` | An iteration touched a checkpoint line |
| `<call> left work uncommitted` | A file was left uncommitted in the copy |
| `<call>: the copy's HEAD is not the call's last commit` | The copy's branch does not match what the call reported |
| `symlink in the copy: …` | A path the stint reads is a symlink |
| `the answer's last line is not JSON` | An answer did not end with its JSON line |
| `review-n committed` | The reviewer committed |
| `principal-n did not check off the checkpoint` | The principal did not mark the checkpoint done |
| `principal-n said done with N tasks left` | Done was said too early |
| `budget: S of B iterations spent` | The budget ran out before done |
| `<call>: would route to metered billing: …` | The billing guard refused the call |
| `<call>: billed to …, not the subscription` | Claude reported a source other than the subscription |
| `<call> ended in error` | Claude's session ended in an error |
| `<call>: run.mjs exited …`, `<call>: N hook rows lost …` | The container call failed, or a hook row did not reach the database |
| `stop: …` | The principal stopped the stint |

An iteration that checks off more or fewer than one task is not stopped;
the stint records a note, and the principal sees it at the checkpoint.
