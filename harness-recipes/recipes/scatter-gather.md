---
type: Recipe Description
title: Scatter-gather
description: Running a batch of independent jobs in one parallel fan-out — one fresh agent per job, results in input order
resource: /dotfiles/dot-claude/workflows/scatter-gather.js
---

# Scatter-gather

A batch of independent jobs ground out in a single parallel fan-out — one fresh
`agent()` per job, all at once, returning one structured result per job in input
order. The batch is stateless: no cache, no file reads, nothing carried between
jobs. The fan-out runs in the Workflow runtime, outside any context window.

## When to use it

For many jobs that do not depend on each other and whose results you want
collected in one shot — judging a set of candidates, classifying a list, or
answering the same question against different inputs. Each job is its own isolated
`agent()`; none can see another's work.

This is the parallel-independent counterpart to the [Ralph loop](/harness-recipes/recipes/ralph-loop.md).
Ralph is one large task split into sequential, dependent steps, where disk carries
state between iterations; scatter-gather is the opposite shape — parallel,
independent jobs that share nothing and run at once. If a job needs another job's
output, it is not a scatter-gather job.
`model` and `effort` are pinned **per job** (each job runs under its own fixed
identity), so a batch can mix identities across its jobs.

## How it works

The script validates args, then fans out once with `parallel()`:

1. parse and validate `args` (a JSON string — see below): require a `jobs` array
   whose every entry carries its own `model` and `effort`, and guard the batch
   size, all before any agent spawns,
2. run every job concurrently as its own isolated `agent()`, with that job's own
   `model`/`effort` and the optional batch `schema` pinned from args,
3. return `[{ id, result }]` — one entry per input job, in input order, keyed by
   the job's `id`.

`model` and `effort` are required **on every job**: the script throws, naming the
offending job index and id, if either is missing rather than inheriting the
session's values, because each job runs under its own fixed identity — there is no
batch-level identity and no default. A job that throws or is skipped yields
`{ id, result: null }` — the per-job catch keeps the `id` rather than dropping the
key, so every input job has exactly one output entry. The guards fail loud before
any agent spawns: an unknown arg, a missing per-job `model`/`effort`, and a batch
larger than the runtime's single-run limit (1000, the agent-lifetime cap — one
agent per job, so it binds before the 4096 per-call cap).

## Running it

Build the batch and call the workflow by name, passing the batch as `args`:

    Workflow({ name: "scatter-gather", args: { schema: SCHEMA, jobs: [
      { id: "a", prompt: "...", model: "haiku", effort: "low" },
      { id: "b", prompt: "...", model: "opus",  effort: "high" },
    ]}})

`jobs` is required — no defaults — and each job must carry its own `model` and
`effort`; `schema` is optional. A missing or malformed arg throws. Source:
[`scatter-gather.js`](/dotfiles/dot-claude/workflows/scatter-gather.js).
