---
type: Guide
title: Running a Stint
description: How a launching agent runs an unattended stint with the stint command — what to prepare, the one-time setup and what the image holds, the pre-commit gate every commit runs, the target check the stint runs at each checkpoint, the run and its arguments, what comes back to the repository, the stint's folder, the exit codes, and every rule that stops a stint
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
- **The target check blocks nothing, and done needs it clean.** The
  workstream's `check` runs the rules the stint works toward. Its findings are a signal, so an iteration may run
  it at any time and commit while it fails. At each checkpoint the stint
  runs it in its own container, spending no tokens, and the principal
  reads its findings. The stint refuses the principal's done while the
  check exits nonzero.
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

The base ref must already hold the workstream folder, with these files:

- `WORKSTREAM.md` — the goal, `## Done when`, the constraints, and a
  `## Stints` whose first entry is the planned one, naming the rule ids
  the stint targets:

  ```markdown
  - **Planned.** Budget: five iterations. Targets: `wordcount.counts-words`.
  ```

- The draft Standards — Markdown files typed `Standard` in the folder, which
  hold every targeted rule. Each rule's trailer says it is `deterministic`;
  a stochastic rule needs the judge, which is not built, so the stint
  refuses one.
- `check` — an executable file that runs the deterministic rules it is
  given. The stint runs it from the repository's root as
  `<workstream>/check <rule-id>…`, with the targeted ids. Exit 0 is zero
  findings; any other exit is findings, printed one per line.
- `PLAN.md` — the tasks, each a `- [ ] ` line at a line's start, in
  segments that end with the exact line `<!-- [ ] checkpoint -->`. Each
  task says how to verify it.
- `PROGRESS.md` — the log each iteration appends to.

The base ref must hold a `.pre-commit-config.yaml`; the stint refuses to
launch without one. It also refuses to launch, with `not launched: …`, when
the head file names no planned target it can run.

The repository needs a `.gitignore` that covers what its check writes, such
as `__pycache__/`: a call that leaves any file uncommitted stops the stint.
The branch `<name>` must not exist yet.

## Run it

```bash
stint run ~/workspace/mission-control \
  --base main \
  --workstream workstreams/wordcount \
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
  commit. An iteration that cannot do its task is stuck: it leaves the task
  unchecked, logs a `- stuck:` line in `PROGRESS.md`, commits, and reports
  why.
- At each checkpoint, `check-<n>` runs `check` on the segment's last
  commit, and `review-<n>` reads the segment's commits cold and commits
  nothing. Both report to `principal-<n>`, the same conversation resumed,
  which rules on their findings and on each stuck iteration, checks off the
  checkpoint, and answers `continue`, `done`, or `stuck`.

No call may change the files that set the target: the head file, the
draft Standards, and `check`. The stint reads them at launch and stops at
the first call that changes one.

## What comes back

The exit code says how the stint ended:

| Exit | Meaning |
|---|---|
| `0` | Done: the principal said done, and the branch landed in the repository |
| `1` | Any other end: a stop rule, the principal's `stuck`, or a work copy kept |
| `2` | The tool could not run: not set up, a bad argument, or a failed step |

On exit 0 or 1 with the copy closed, the repository has the branch `<name>`
holding every commit the stint made, and the copies and the cache are
deleted. On a stop, the branch holds the work up to the stop. A work copy
that cannot close, such as one holding uncommitted work, is kept in the
folder, and the last line names it.

The stint's folder, `<home>/<repo>/<name>/`, stays:

| File | What it holds |
|---|---|
| `stint.json` | The reason it ended, iterations spent, the branch's last commit, the notes, the principal's context size per call, each call's session and commits, and each check's exit code |
| `calls/<call>.json` | One call's record: its session, billing source, tokens, commits, uncommitted files, and answer; for `check-<n>`, its exit code, output, and uncommitted files |
| `calls/<call>.request.json` | What the call asked Sandcastle to run, the prompt or the command included |
| `calls/<call>-setup.log` | Sandcastle's log of the hook install that runs before the agent |
| `calls/<call>.log`, `calls/<call>-probe.log` | Sandcastle's logs of the agent or the check, and of the uncommitted-work probe |
| `check-<n>.txt` | The target check's output at checkpoint `n`, and its exit code |
| `review-<n>.md` | The reviewer's report for segment `n` |
| `sessions/` | Every agent's session file; the principal's is resumed from here |

## What stops a stint

This table is the one list of the stint's stop rules. Each rule is checked
in code, in [`loop.py`](/src/dev_playbook/stint/loop.py) and
[`launch.py`](/src/dev_playbook/stint/launch.py), and the reason is the
last line and `stint.json`'s `reason`:

| Reason | What happened |
|---|---|
| `not launched: N tasks, budget B` | The plan has more open tasks than the budget |
| `not launched: …` naming the target | The head file has no planned entry with `Targets:`, a target is no rule of a draft Standard or is stochastic, or `check` is not an executable file |
| `stuck at launch: …` | The principal did not answer `launch` |
| `the principal changed the plan at launch` | `principal-0` committed |
| `iter-k moved a checkpoint marker` | An iteration touched a checkpoint line |
| `segment n has no commits to review` | The segment's iterations committed nothing, not even a `- stuck:` line |
| `<call> changed the target: …` | A call changed, or deleted, the head file, a draft Standard, or `check` |
| `<call> left work uncommitted` | A file was left uncommitted in the copy, by an agent or by the check |
| `<call>: the copy's HEAD is not the call's last commit` | The copy's branch does not match what the call reported |
| `check-n moved the copy's HEAD` | The target check committed |
| `symlink in the copy: …` | A path the stint reads is a symlink |
| `the answer's last line is not JSON` | An answer did not end with its JSON line |
| `review-n committed` | The reviewer committed |
| `principal-n did not check off the checkpoint` | The principal did not mark the checkpoint done |
| `principal-n said done with N tasks left` | Done was said too early |
| `principal-n said done while the check reports findings (exit E)` | Done was said while the target check at that checkpoint exited nonzero |
| `budget: S of B iterations spent` | The budget ran out before done |
| `principal-n left N unchecked tasks above the checkpoint` | A task no segment will reach was left behind the checked-off line |
| `principal-n said continue with no task in the next segment` | The next segment is empty |
| `<call>: would route to metered billing: …` | The billing guard refused the call |
| `<call>: billed to …, not the subscription` | Claude reported a source other than the subscription |
| `<call> ended in error` | Claude's session ended in an error |
| `<call>: run.mjs exited …`, `<call>: N hook rows lost …` | The container call failed, or a hook row did not reach the database |
| `stuck: …` | The principal yielded the stint as stuck |

An iteration that checks off more or fewer than one task, or is stuck, is
not stopped; the stint records a note, and the principal sees it at the
checkpoint. An iteration that checks off no task, or is stuck, ends its
segment early, so the checkpoint comes next.
