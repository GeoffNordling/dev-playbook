---
name: run-judgments
description: Run the judgments workflow. Use when the judgment cache-gate (pytest) is red, or when the user asks to run the judgments.
disable-model-invocation: false
model: opus
effort: low
---

# Run Judgments

A **judgment** is a specific yes/no question about specific files, ruled on by an LLM judge. Judgments are declared as YAML and gated by deterministic pytests. See `standards/judgments/declarations.md` for the declaration format. Tests pass iff the judgment's exact content has already been judged-and-passed (its key is cached); misses fail. This skill runs the judgment workflow: it dispatches each uncached judgment to the `scatter-gather` agent workflow for an LLM-judged verdict, records the passes, fixes the refutations, and loops until the gate is green — escalating to the user when a fix is beyond it.

This is a thin implementation skill relying on deterministic CLI commands: the CLI enumerates the work and records the outcomes, the judges produce the verdicts, and this skill's own judgment is confined to the fixes.

**Main loop only.** This skill dispatches judges through the `Workflow` tool, which exists only at the main loop — a subagent does not have it. A subagent that hits a cache miss (a red judgment gate) must **surface** it for the main loop or the user to run this skill; it must never hand-roll judge calls, which would bypass the per-judgment `model`/`effort` pinning and schema validation and produce off-bench verdicts that must not be recorded.

## The loop

Repeat steps 1–5 until step 1 finds nothing left to run. Two limits govern every pass through it:

- **Two fix attempts per judgment.** A judgment still refuted after two fixes is set aside for the user.
- **Focused fixes only.** A fix is one focused edit — a section, not a rewrite. A refuted judgment needing more is set aside for the user, unfixed.

### 1. Enumerate the misses

Run `judgments-run plan` and parse its single JSON object:

```json
{ "schema": { … },
  "seen": ["ID#1", …],
  "unseen": [ {"id": "ID#2", "model": "<model>", "effort": "<effort>", "prompt": "Run `judgments-run render ID#2` …"}, … ] }
```

`unseen` is the set of judgments not yet cached. Each entry is a **ready-to-dispatch job** — `id`, its bench (`model`/`effort`), and the `prompt` that bootstraps the judge. Drop any set-aside judgment from the list. If nothing remains, stop and report: on a first pass that reads "all N judgments already cached; nothing to run"; on a later pass the loop is done.

### 2. Dispatch

Forward the remaining jobs and the plan's `schema` to the workflow:

```js
Workflow({ name: "scatter-gather", args: { jobs, schema } })
```

Each job carries its own required `model`/`effort`; `schema` is batch-wide. One judge agent per miss, in parallel. Each agent runs its `prompt` — which tells it to `judgments-run render <id>` and obey that output — so the heavy prompt bytes are produced **inside each judge**, never here. The workflow returns `[{ id, result }]` in input order, where `result` is the schema-validated `{verdict, opinion}`, or `null` for a crashed/skipped job.

### 3. Partition the results

- **pass** — `result.verdict === true`
- **refuted** — `result.verdict === false` (keep `result.opinion`: it names what to fix)
- **crashed** — `result` is `null` (the agent crashed, or its `render` step failed). A crash is **not a verdict** — the judgment was never ruled on — and is handled differently from a refutation in step 5.

### 4. Record the passes

`judgments-run record <pass-id> [<pass-id> …]` — one call with every passing id. **Only passes are ever recorded.** If nothing passed, skip the call.

### 5. Fix, requeue, loop

- **Refuted** — a refuted verdict is a real defect: fix the artifact when the claim is right, fix the claim when it overstates; never weaken, drop, or reword a judgment merely to pass. Make one focused edit per refuted judgment, guided by its `opinion` — this consumes one of its two fix attempts. The edit changes the judgment's content key, so the next `plan` re-lists it automatically; no bookkeeping.
- **Crashed** — requeue as-is: no fix, no attempt consumed. A judgment that crashes twice in a row is set aside like a spent one — a repeating crash is an environment problem to surface, not a verdict.
- Set aside any judgment that is out of fix attempts or needs more than a focused fix, then loop back to step 1.

## Report

When the loop stops, tell the user: skipped (already cached), ran, passed (recorded), fixed-then-passed (each id + the edit made), set aside (each id + its `opinion` or crash history + why), crashed-and-recovered. The armed gate — `make check-judgments`, the pre-push hook's entry (a bare `uv run pytest` arms it too) — goes green only when **every** judgment passes; set-aside judgments keep it red by design. Default `make check`/`make test` skip the gate (`SKIP_JUDGMENTS=1`), so re-check against `make check-judgments`.
