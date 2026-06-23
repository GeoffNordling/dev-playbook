# Ralph loop

A large goal ground out by booting a fresh agent each iteration until done. The
goal is fixed on disk; each iteration is a new context window that reads the
current state, does the next step, and records it. The loop itself runs in the
Workflow runtime, outside any context window.

## When to use it

For a large task that splits into small, sequential, dependent steps — each step
builds on the last, and no single step needs the whole task in context at once.
The fixed goal lives in `GOAL.md`; the running log lives in `PROGRESS.md`; git
carries the work. A fresh agent picks up from those each iteration, so the task
can run far longer than any one context window holds.

Not for tasks that need the whole picture in mind at once, or whose steps are
independent (parallelize those instead).

## How it works

Each iteration is one fresh `agent()`:

1. read `GOAL.md` (the fixed goal) and `PROGRESS.md` (what came before),
2. do the single next step,
3. append one line to `PROGRESS.md` and commit,
4. report whether the goal is done.

The runtime repeats this until an agent reports done. No agent remembers the
last — continuity lives entirely on disk. Isolated minds, shared world.

## Running it

Launch from the target repo or worktree (agents inherit that cwd). Seed a
`GOAL.md`, then call the workflow by name:

    Workflow({ name: "ralph-loop", args: { model: "haiku", maxIters: 6 } })

Args, all optional: `goal` (inline, else `GOAL.md`), `model`, `maxIters`
(default 50), `commit` (default true). Source:
`dotfiles/dot-claude/workflows/ralph-loop.js`.

## What we verified (2026-06-23)

Tested directly this session, in an interactive session:

- **Fresh context each iteration.** Later iterations continued a story they had
  no memory of writing; the only link between them was disk.
- **Disk carries state across iterations, in the launching session's directory.**
  A worker inherits the session's working directory — relative-path writes landed
  in that cwd, including inside a git worktree.
- **The iteration prompt can be a file.** A worker performed a task whose
  instructions existed only in an on-disk `.md`, never in the script.
- **Per-iteration model is selectable.** A worker ran on Haiku (confirmed in its
  transcript) while the launching session ran on Opus.
- **No filesystem sandbox.** A worker read a file in a different repo, and wrote
  to `/tmp` and into a `.git/` directory — all outside the worktree, unprompted.
- **Permissions are mode-dependent.** With Auto Mode on, every worker file,
  shell, and commit operation ran with no prompt — hands-off. With Auto Mode
  off, the worker prompted on each edit and commit; approving each let the loop
  finish, so an unattended loop would stall on the first prompt.
- **A workflow can be launched by an agent**, not only by a human pressing a
  button — including by its registered name. (Passing `args` to a named launch
  did not take effect, though — seed `GOAL.md` or hardcode the script instead.)

Frankly, not established:

- What a worker does if a gate is *denied* mid-loop (we only ever approved
  through), and what a truly unattended loop does when it stalls on a prompt.
- The above assumes interactive Auto Mode; a stricter posture changes it.
- Per Anthropic's docs (untested here): a workflow resumes only within the same
  session.
