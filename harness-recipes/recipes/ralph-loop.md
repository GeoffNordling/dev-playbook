---
type: Recipe-Description
title: Ralph loop
description: Grinding a large task to done by booting a fresh agent each iteration, with plan and progress carried on disk and a reviewing fork at every checkpoint
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
3. implements the single next incomplete task in its segment,
4. brings the gate back to green when one is configured — never commits red,
5. checks the task off in the plan, optionally records a durable fact for later iterations in the plan's Working notes, and appends a line to the progress log,
6. commits via the `/commit` skill,
7. reports how many unchecked tasks are left in its segment.

The runtime repeats this until that count reaches zero. The agent supplies the
count; the rule that reads it stays in the runtime, so no iteration ever
decides whether the loop ends.

## Checkpoints

A plan is cut into segments by checkpoint markers, and the loop runs one
segment per launch. At each stop the launching session forks itself to review
what landed before releasing the next segment.

How many checkpoints a plan carries is decided with the user at setup. The
floor is one, placed after the last task. Every checkpoint above the floor buys
the same review earlier: a mistake is caught one segment after it is made
rather than at the finish.

There is no mode switch and no argument for any of this. The markers are in the
plan, the iteration agent reads the plan, and an argument could only ever
disagree with the file.

Three agents and a runtime, in four different positions:

```
                                  USER
                                    │
             /ralph-setup ──────────┤   skills/ralph-setup/SKILL.md
                                    │     ├─ references/plan-skeleton.md
   agree: N tasks, K checkpoints    │     └─ references/progress-skeleton.md
          K ≥ 1                     │
                                    ▼   writes once, before any loop runs
              ┌──────────────────────────────────────────────┐
              │ PLAN.md       tasks, each with a Verify       │
              │               K × <!-- [ ] checkpoint -->     │
              │               one of them after the last task │
              │ PROGRESS.md   empty log                       │
              └──────────────────────────────────────────────┘
                                    │
                     launch command │  the skill hands it over, never runs it
                                    ▼
   ╔═════════════════════════════════════════════════════════════════════╗
   ║ SESSION      one context window, held across the whole run          ║
   ║              owns control flow — decides what runs next             ║
   ╚═════════════════════════════════════════════════════════════════════╝
        │                           │
        │   ┌───────────────────────▼──────────────────────────────────┐
        │   │ ① Workflow({ name:"ralph-loop", args:{ model, maxIters,  │
        │   │              planFile, progressFile, checkCmd } })       │
        │   └───────────────────────┬──────────────────────────────────┘
        │                           ▼
        │  ╔════════════════════════════════════════════════════════════╗
        │  ║ RUNTIME    workflows/ralph-loop.js                         ║
        │  ║            no context window, no filesystem                ║
        │  ║            owns the stopping rule: while (tasksLeft !== 0) ║
        │  ╚════════════════════════════════════════════════════════════╝
        │        │                  │
        │        │  ┌───────────────▼──────────────────────────────────┐
        │        │  │ RALPH — fresh agent, no memory, dies each pass   │
        │        │  │                                                  │
   OUTER│   INNER│  │   gate ▸ read PLAN + PROGRESS ▸ do 1 task ▸ gate │
    LOOP│    LOOP│  │   ▸ check the task off in PLAN                   │
        │        │  │   ▸ append 1 log line + any judgment calls       │
  1 per │   1 per│  │   ▸ /commit ▸ report tasksLeft                   │
segment │    task│  └───────────────┬──────────────────────────────────┘
        │        │                  │ tasksLeft
        │        └───────── > 0 ────┤
        │                           │ = 0  →  return { iterations, blocker }
        │                           ▼
        │   ┌──────────────────────────────────────────────────────────┐
        │   │ ② /ralph-checkpoint    skills/ralph-checkpoint/SKILL.md  │
        │   └───────────────────────┬──────────────────────────────────┘
        │                           ▼
        │   ┌──────────────────────────────────────────────────────────┐
        │   │ FORK — inherits SESSION's context                        │
        │   │        agents/ralph-checkpointer.md                      │
        │   │                                                          │
        │   │   verify what landed ▸ take stock against the goal      │
        │   │   ▸ adapt the tasks ahead ▸ write PLAN, log decisions   │
        │   │   ▸ [ ] → [x] on the marker ▸ commit                     │
        │   │   ▸ at the last checkpoint, also check                   │
        │   │     PLAN's ## Done when ▸ report ≤ 10 lines              │
        │   └───────────────────────┬──────────────────────────────────┘
        │                           │
        │     unchecked tasks left? │
        └────────────── yes ────────┤
                                    │ no
                                    ▼
                                complete
```

The two loops sit at different levels. The **inner** one is a `while` in
`ralph-loop.js`, held by no context window, turning over one Ralph per task.
The **outer** one is the session's own turn-taking, turning over one segment per
checkpoint. The fork sits in the outer loop, which is why a twelve-segment run
still fits in one session: only ten lines come back from each review.

| | `PLAN.md` | `PROGRESS.md` | git | session context |
|---|---|---|---|---|
| `/ralph-setup` | writes | writes | — | — |
| runtime | — | — | — | none, by construction |
| Ralph | read + check off | read + append | commits | none |
| fork | read + write | read + decisions | commits | inherits the session's |
| session | — | — | — | owns it |

A Workflow script has no filesystem access, which is why `tasksLeft` is
reported up from Ralph rather than counted in the loop.

**The marker.** A checkpoint is an HTML comment, so it is invisible wherever
the plan renders: `<!-- [ ] checkpoint -->` not yet reviewed,
`<!-- [x] checkpoint -->` already reviewed. The plan carries all of its markers
from the start and they get checked off as the run proceeds, exactly as tasks
do — Ralph checks off tasks, the fork checks off checkpoints. Nothing is
deleted, so the finished plan is itself the record of how the run was
segmented.

**The safety rule**, checked on every entry: at least one
`<!-- [ ] checkpoint -->` is present, and no unchecked task sits below the last
one. Together those make it structurally impossible to reach work with no
review after it — including the last task, which is why the final review needs
no special case in the code. A marker that is a near miss —
`<!-- Checkpoint -->`, say — is a comment no parser sees, which would silently
turn a reviewed run into an unreviewed one, so the loop refuses to start on one.

**Why a marker and not a checkpoint task in the list.** The loop's only
completion signal is the count of unchecked tasks. A checkpoint written as a
task would have to be checked off by an agent, which puts the loop's own state
in an agent's hands. A marker is inert to Ralph and legible to the runtime.

**Who owns the plan.** The fork does. Iterations check tasks off and never
change the route; the plan ahead is adapted only at a checkpoint, where
something can see the whole run at once. Adapted, not rewritten — the plan the
user approved is the trajectory, and every checkpoint that adjusts a little
leaves a run that ends somewhere nobody agreed to. Clarifying a task or fixing
an order is free. Adding or dropping a task, changing an approach, or moving a
checkpoint costs a line in the ledger. Two things the fork may not touch: a task
already checked off, and the `## Done when` criteria — a run that edits its own
definition of success has stopped being checkable. Where the plan can no longer
reach the goal at all, the fork says so and stops rather than routing around it.

**Two ledgers, one file.** Iterations write judgment calls into the progress
log for the fork to read at the next checkpoint. The fork writes decisions into
that file's `## Decisions` section for the user to read at PR time. They share a
file because they are one causal chain: the call raised at iteration 4 is what
the decision at checkpoint 1 rules on.

**Judgment calls.** An iteration that hits a point the plan does not settle
records it in the progress log and carries on, rather than stopping. They are
the fork's main evidence about the plan: one call is a gap in a task, the same
call twice is a gap in the plan. Their volume tracks how much new ground the
work breaks, not how far into the run it is, so do not size later segments on
an assumption that a run gets quieter.

## Running it

Launch from the target repo or worktree (agents inherit that cwd). First seed the plan
and progress files — the [`ralph-setup`](/dotfiles/dot-claude/skills/ralph-setup/SKILL.md)
skill interviews you and writes them — then call the workflow by name:

    Workflow({ name: "ralph-loop", args: { model: "haiku", maxIters: 6, planFile: "PLAN.md", progressFile: "PROGRESS.md", checkCmd: "make check" } })

All args are required — no defaults: `model` (worker model), `maxIters`
(safety rail), `planFile` (the plan: a task list), `progressFile` (the running
log), `checkCmd` (the check gate run at the start and end of each iteration — a
shell command meaning "green", e.g. `make check` or `make -C tools check`; pass
`""` for no checks). A missing or malformed arg throws. Source:
[`ralph-loop.js`](/dotfiles/dot-claude/workflows/ralph-loop.js).

The workflow returns `{iterations, blocker}`. A `blocker` — a red gate on
entry, a malformed marker, an iteration that returned nothing — comes back as
a sentence rather than a stack trace, because what reads it is a session
deciding what to do next.

`maxIters` rails one segment, not the run, so size it to the longest segment.
Each stop is followed by
[`/ralph-checkpoint`](/dotfiles/dot-claude/skills/ralph-checkpoint/SKILL.md),
which forks the session to review the segment and hands back the command for
the next one. That pair runs once per segment, the last time to review the
finished plan against its `## Done when` criteria.
