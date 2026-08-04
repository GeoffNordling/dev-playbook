---
type: Recipe-Description
title: Ralph loop
description: Grinding a large task to done by booting a fresh agent each iteration, with plan and progress carried on disk
resource: /dotfiles/dot-claude/workflows/ralph-loop.js
---

# Ralph loop

A plan ground out by booting a fresh agent each iteration until done. The plan
lives on disk as a task list; each iteration is a new context window that reads
the current state, does the next task, and records it. The loop itself runs in
the Workflow runtime, outside any context window.

## When to use it

For a large task that splits into small, sequential tasks — each builds on the
last, and no single task needs the whole thing in context at once. The plan (a
task list) and a running log live on disk in files you name; git carries the
work. A fresh agent picks up from those each iteration, so the task can run far
longer than any one context window holds.

Not for tasks that need the whole picture in mind at once, or whose tasks are
independent (parallelize those instead).

## How it works

Each iteration is one fresh `agent()` that:

1. runs the check gate, when one is configured, and confirms the plan and
   progress files exist — if the gate is red on entry or a file is missing, the
   loop raises immediately (a red entry means a prior iteration left the repo
   broken),
2. reads the plan and the progress log,
3. implements the single next incomplete task,
4. brings the gate back to green when one is configured, so the tree the next iteration inherits is not broken,
5. checks the task off in the plan, optionally records a durable fact for later iterations in the plan's Working notes, and appends a line to the progress log,
6. attempts a commit via the `/commit` skill,
7. reports whether the plan is complete.

The runtime repeats this until an agent reports done. No agent remembers the
last — continuity lives entirely on disk.

**Step 6 currently has no commit authorization.** `git commit` is deny-by-default
under the `git-authority` hook's commit rule family, and an iteration agent is
not one of the committing factory agent types, so lane 1 refuses it. Whether
lane 2 is even reachable from here is unmeasured: it turns on whether a Workflow
`agent()` payload carries an `agent_type` key at all. If it does, lane
exclusivity shuts lane 2 outright; if it does not, the iteration falls through to
the launching session's transcript, and a `/commit-on` typed before launch would
open the lane — the cross-session reach lane exclusivity exists to prevent. That
is an assumption either way, not a measured fact.

The conclusion holds under both branches: expect the commit to be denied unless
someone granted the launching session first, and do not rely on it. Disk is the
loop's only memory, so a loop run this way makes no durable progress, and the
runtime stops on the denial rather than grinding out iterations nothing records.
Giving the iteration a lane of its own, and measuring the payload, is
[#351](https://github.com/GeoffNordling/dev-playbook/issues/351); until it lands,
treat this recipe as describing the loop's shape rather than a working commit
path.

## Running it

Launch from the target repo or worktree (agents inherit that cwd). First seed the plan
and progress files — the [`ralph-setup`](/dotfiles/dot-claude/skills/ralph-setup/SKILL.md)
skill interviews you and writes them — then call the workflow by name:

    Workflow({ name: "ralph-loop", args: { model: "haiku", maxIters: 6, planFile: "PLAN.md", progressFile: "PROGRESS.md", checkCmd: "make check" } })

All five args are required — no defaults: `model` (worker model), `maxIters`
(safety rail), `planFile` (the plan: a task list), `progressFile` (the running
log), `checkCmd` (the check gate run at the start and end of each iteration — a
shell command meaning "green", e.g. `make check` or `make -C tools check`; pass
`""` for no checks). A missing or malformed arg throws. Source:
[`ralph-loop.js`](/dotfiles/dot-claude/workflows/ralph-loop.js).