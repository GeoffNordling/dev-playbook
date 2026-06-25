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

1. runs the project's checks and confirms the plan and progress files exist — if
   checks are red on entry or a file is missing, the loop raises immediately (a
   red entry means a prior iteration left the repo broken),
2. reads the plan and the progress log,
3. implements the single next incomplete task,
4. brings the checks back to green — never commits red,
5. checks the task off in the plan, optionally records a durable fact for later iterations in the plan's Working notes, and appends a line to the progress log,
6. commits via the `/commit` skill,
7. reports whether the plan is complete.

The runtime repeats this until an agent reports done. No agent remembers the
last — continuity lives entirely on disk.

## Running it

Launch from the target repo or worktree (agents inherit that cwd). First seed the plan
and progress files then call the workflow by name:

    Workflow({ name: "ralph-loop", args: { model: "haiku", maxIters: 6, planFile: "PLAN.md", progressFile: "PROGRESS.md" } })

All four args are required — no defaults: `model` (worker model), `maxIters`
(safety rail), `planFile` (the plan: a task list), `progressFile` (the running
log). A missing or malformed arg throws. Source:
[`ralph-loop.js`](~/workspace/dev-playbook/dotfiles/dot-claude/workflows/ralph-loop.js).