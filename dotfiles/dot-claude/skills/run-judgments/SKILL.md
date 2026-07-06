---
name: run-judgments
description: Run the judgments workflow. Use when the judgment cache-gate (pytest) is red, or when the user asks to run the judgments.
disable-model-invocation: false
model: opus
effort: low
---

# Run Judgments

A **judgment** is a specific yes/no question about specific files, ruled on by an LLM judge. Judgments are declared as YAML and gated by deterministic pytests. See `instruments/judgments/declarations.md` for the declaration format. Tests pass iff the judgment's exact content has already been judged-and-passed (its key is cached); misses fail. This skill runs the judgment workflow — it dispatches each uncached judgment to the `scatter-gather` agent workflow for an LLM-judged verdict. Passes are recorded in the cache. Failures indicate potential bugs the same way a failed Python test does; they escalate for correction.

This is a thin implementation skill for the judgment workflow, relying on deterministic CLI commands. It only runs the workflow, partitions the verdicts, records the passes, and escalates the failures.

## The loop

### 1. Enumerate the misses

Run `judgments-run plan` and parse its single JSON object:

```json
{ "schema": { … },
  "seen": ["ID#1", …],
  "unseen": [ {"id": "ID#2", "model": "<model>", "effort": "<effort>", "prompt": "Run `judgments-run render ID#2` …"}, … ] }
```

`unseen` is the set of judgments not yet cached. Each entry is a **ready-to-dispatch job** — `id`, its instrument (`model`/`effort`), and the `prompt` that bootstraps the judge. If `unseen` is empty, report "all N judgments already cached; nothing to run" and stop.

### 2. Dispatch

Forward the jobs and the plan's `schema` to the workflow:

```js
Workflow({ name: "scatter-gather", args: { jobs: unseen, schema } })
```

Each job carries its own required `model`/`effort`; `schema` is batch-wide. One judge agent per miss, in parallel. Each agent runs its `prompt` — which tells it to `judgments-run render <id>` and obey that output — so the heavy prompt bytes are produced **inside each judge**, never here. The workflow returns `[{ id, result }]` in input order, where `result` is the schema-validated `{verdict, opinion}`, or `null` for a crashed/skipped job.

### 3. Partition the results

- **pass** — `result.verdict === true`
- **fail** — `result.verdict === false` (keep `result.opinion`)
- **error** — `result` is `null` (the agent crashed, or its `render` step failed)

### 4. Record only the passes

`judgments-run record <pass-id> [<pass-id> …]` — one call with every passing id. **Only passes.** Fails and errors are never recorded. If nothing passed, skip the call.

### 5. Report

Tell the user: skipped (the `seen` count), ran (dispatched), passed, failed (each `id` + its `opinion`), errored (each `id`). Optionally re-run the gate (`pytest` / `make check`); it goes green only if **every** judgment passed — failures keep it red by design.
