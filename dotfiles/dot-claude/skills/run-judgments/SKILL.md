---
name: run-judgments
description: Run the judgments workflow. Use when the judgment cache-gate (pytest) is red, or when the user asks to run the judgments.
disable-model-invocation: false
model: opus
effort: low
---

# Run Judgments

A **judgment** is a specific yes/no question about specific files, ruled on by an LLM judge. Judgments are declared as YAML and gated by deterministic pytests. See `standards/judgments/declarations.md` for the declaration format. Tests pass iff the judgment's exact content has already been judged-and-passed (its key is cached); misses fail. This skill runs the judgment workflow: it dispatches each uncached judgment to the `scatter-gather` agent workflow for an LLM-judged verdict, records the passes, fixes the refutations, and loops until the gate is green — escalating to the user when a fix is beyond it.

This is a thin implementation skill relying on deterministic CLI commands: the CLI enumerates the work and records the outcomes, the judges produce the verdicts, and this skill's own judgment is spent weighing each refutation and making the fixes it warrants.

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

- **Refuted — investigate, don't comply.** A refuted verdict is *one low-intelligence, stochastic judge's claim, not a proven defect*. We run these judges constantly and will get false positives; the main loop is the more careful reader, so weigh the `opinion` from first principles against the repo's own rules and adjacent artifacts, with the standing default that **the artifact is correct as written**. Overturning that default takes genuinely convincing evidence — the burden is on the judge, not on the text. Then act on what you actually find:
  - **the artifact is wrong** — one focused edit (a section, not a rewrite), guided by the `opinion`; consumes one of the judgment's two fix attempts, and the changed content key re-lists it on the next `plan`.
  - **the claim overstates** — fix the claim to say what is true; never weaken, drop, or reword a judgment merely to pass.
  - **the judge is wrong** — change *nothing*. Never pad a standard or doc with hedging, caveats, or filler to placate a tripped judge: that trades correct prose for slop, worse than a red gate. With the user's concurrence, `record` the pass on the unchanged content to override the false positive — the deliberate "no need to rerun the judge" path; an autonomous run sets the suspected false positive aside for the user instead of self-clearing it.
- **Edited with the user watching — mark it, don't re-run.** When a refutation or a caveat leads to a **small** edit you made yourself while the user was in the loop — they asked for it, or they saw the wording and concurred — `record` the pass on the edited content instead of re-dispatching. Say so plainly in the report: the judge was skipped and the judgment marked passing, on content no judge has read. A second opinion on a clause the user just approved buys nothing they have not already supplied, and the round trip costs a full judge run.

  Scope this tightly. It is for minor edits — a reworded clause, a tightened table cell, a corrected name — where the fix is obvious and the judge's own `opinion` named it. A new section, a changed rule, or a claim that now asserts something different goes back through a judge. So does any edit made without the user present: an autonomous run re-judges, always.
- **Crashed** — requeue as-is: no fix, no attempt consumed. A judgment that crashes twice in a row is set aside like a spent one — a repeating crash is an environment problem to surface, not a verdict.
- Set aside any judgment that is out of fix attempts, needs more than a focused fix, or is a suspected false positive. Escalate these to the user.

**The user is your escalation path — use it, with an example.** The user sits at the main loop for exactly the hard calls: a genuinely ambiguous artifact-vs-judge question, a refutation you cannot confidently place, a fix larger than focused. Escalate rather than guess or force a fix. When you do, quote the specific thing at issue — the artifact line as written, the claim's exact words, the precise mismatch the `opinion` alleges. The user is not looking at the code, the doc, or the judgment; present a specific example, not an abstract summary.

## Report

When the loop stops, tell the user: skipped (already cached), ran, passed (recorded), fixed-then-passed (each id + the edit made), marked-without-re-judging (each id + the edit and that no judge read it), set aside (each id + its `opinion` or crash history + why), crashed-and-recovered. The armed gate — `make check-judgments`, the pre-push hook's entry (a bare `uv run pytest` arms it too) — goes green only when **every** judgment passes; set-aside judgments keep it red by design. Default `make check`/`make test` skip the gate (`SKIP_JUDGMENTS=1`), so re-check against `make check-judgments`.
