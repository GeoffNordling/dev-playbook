# Scatter-gather

A batch of independent jobs run as isolated agents in a single parallel fan-out,
with one structured result collected per job in input order. The batch is
stateless: no cache, no file reads, nothing carried between jobs — every durable
result lives in the caller. The fan-out runs in the Workflow runtime, outside any
context window.

## When to use it

For many jobs that do not depend on each other and whose results you want
collected in one shot — judging a set of candidates, classifying a list,
answering the same question against different inputs. Each job is its own
isolated `agent()`; none can see another's work.

This is the parallel-independent counterpart to the [Ralph loop](ralph-loop.md).
Ralph is for one large task split into *sequential, dependent* steps, where each
step builds on the last and disk carries state between iterations. Scatter-gather
is the opposite shape: *parallel, independent* jobs that share nothing and run at
once. If a job needs another job's output, it is not a scatter-gather job — chain
it with `pipeline()` instead.

`model` and `effort` are pinned to the whole batch (one fixed identity per run),
so scatter-gather is not for work that needs per-job model selection.

## How it works

The batch is one `parallel()` over the jobs — one `agent()` each:

1. normalize `args` (it may arrive as an object or a JSON string — see below),
2. require `model` and `effort`, and guard the batch size, before fanning out,
3. run every job concurrently as its own isolated `agent()`, with `model`,
   `effort`, and the batch `schema` pinned from args,
4. return `[{ id, result }]` — one entry per input job, in input order, keyed by
   the job's `id`.

`model` and `effort` are **required**: the runtime throws if either is missing
rather than inheriting the session's values, because the batch runs under one
fixed identity (the first consumer content-addresses its cache on
`model + effort + prompt + schema`, so an inherited value would corrupt the
fingerprint). A single `schema` applies to every job; `label`/`phase` are
cosmetic.

A job that throws or is skipped yields `{ id, result: null }` — the per-job catch
keeps the `id` rather than dropping to a bare `null` that would lose the key. So
every input job has exactly one output entry, always carrying its id.

Two pre-flight guards fail loud before any agent spawns: missing `model`/`effort`,
and a batch larger than the runtime's binding single-run limit. That limit is the
agent-lifetime cap (1000), not the larger 4096 per-call item cap — scatter-gather
spends one agent per job, so the lifetime cap binds first.

## Running it

Seed the batch and launch the workflow, passing the batch as `args`:

    Workflow({
      scriptPath: ".../dotfiles/dot-claude/workflows/scatter-gather.js",
      args: { model: "haiku", effort: "low", schema: SCHEMA, jobs: [
        { id: "a", prompt: "..." },
        { id: "b", prompt: "..." },
      ]},
    })

`args` may reach the script as a parsed object or as a JSON string, depending on
the launch path, so the runtime normalizes it on the way in — pass a real object
and either form is handled. Launch by `scriptPath` to reach a build that is
not yet in the named registry (`~/.claude/workflows/`, which resolves to the main
checkout); launch by `name: "scatter-gather"` once the file is synced there.
Source: `dotfiles/dot-claude/workflows/scatter-gather.js`.

## What we verified (2026-06-24)

Tested directly this session by launching the workflow:

- **The batch is reliably delivered and normalized.** The jobs arrived intact in
  every run below, and the runtime's normalization handled `args` whether it came
  through as an object or a JSON string — so the batch lands however it is handed
  over. The exact form `args` takes is launch-path dependent and not pinned down
  here; normalizing on the way in makes the recipe robust either way.
- **Order and id-keying.** A three-job batch returned
  `[first → ALPHA, second → BRAVO, third → CHARLIE]` in input order, each entry
  keyed by its job id.
- **Isolation.** Every job reported seeing no other job (`seen: "none"`) — each
  ran in its own context with no view of the others.
- **Parallel, not serial.** Three agents completed in ~5s of wall-clock.
- **`model`/`effort` required.** Omitting `model` throws "model is required";
  omitting `effort` with `model` present throws "effort is required" — neither
  inherits the session value.
- **Over-limit pre-flight guard.** A 1001-job batch threw the cap error before
  spawning any agent (agent count 0); the guard fires at 1000, the agent-lifetime
  cap, below the 4096 per-call cap.
- **One schema, batch-wide.** All three jobs returned the single declared
  `{ word, seen }` shape.

Not established here:

- **Failure or skip → `{ id, result: null }`.** Guaranteed by construction — the
  per-job thunk catches and returns the id with a null result — but not forced
  live, since a real agent failure is hard to trigger on demand.
- **Named-registry launch.** The runtime resolves named workflows from the main
  checkout, so a worktree build is reachable only by `scriptPath` until synced.
  Arg delivery is expected to behave the same on both paths, but only `scriptPath`
  was exercised here.
