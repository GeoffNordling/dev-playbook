---
name: run-judgments
description: Run the judgments workflow. Use when the judgment cache-gate (pytest) is red, or when the user asks to run the judgments.
disable-model-invocation: false
model: opus
effort: low
---

# Run Judgments

A **judgment** is a specific yes/no question about specific files, ruled on by an
LLM judge, declared as YAML and gated by a deterministic pytest that passes iff that
judgment's exact content has already been judged-and-passed. A miss is a red gate.
See `standards/judgments/declarations.md` for the declaration format.

This skill turns a red gate green. The mechanical half — planning the docket,
dispatching the judges, partitioning the verdicts, recording the passes — belongs to
the `judgments` workflow and happens outside your context window. Your job is the
half that needs a mind: **weighing each refutation and making the fixes it warrants.**

**Main loop only.** The `Workflow` tool exists only at the main loop; a subagent does
not have it, must **surface** a red gate rather than work around it, and must never
hand-roll judge calls — that bypasses the per-judgment `model`/`effort` pinning and
the fixed output schema, producing off-bench verdicts that must not be recorded.

## The loop

### 1. Run the workflow

```js
Workflow({ name: "judgments" })
```

That is the whole invocation. It takes no arguments, reads the docket itself, and
judges every uncached judgment in parallel. Once you have set judgments aside
(step 3), name them so they are not re-judged:

```js
Workflow({ name: "judgments", args: { skip: ["some-id", "another-id"] } })
```

### 2. Read the result

The result arrives inline in the workflow's task notification. If you instead open
the task's output file, that file is a wrapper — the workflow's own return value is
under its top-level **`result`** key, not at the top level.

```json
{ "cached": 25, "ran": 3, "passed": ["id-a"],
  "refuted": [ {"id": "id-b", "opinion": "…what to fix…"} ],
  "crashed": ["id-c"], "skipped": [], "green": false }
```

`passed` is already recorded — nothing for you to do. `green` is true when the gate
should now be satisfied. **`refuted` is the only actionable field.**

A **crash is not a verdict** — that judgment was never ruled on, stays uncached, and
is picked up by simply running the workflow again; no fix, no attempt consumed. Twice
running is an environment problem: set it aside and say so.

### 3. Weigh each refutation, then act

**Investigate, don't comply.** A refuted verdict is *one low-intelligence, stochastic
judge's claim, not a proven defect*. We run these judges constantly and will get false
positives; you are the more careful reader. Weigh the `opinion` from first principles
against the repo's own rules and the adjacent artifacts, with the standing default
that **the artifact is correct as written** — overturning it takes genuinely
convincing evidence, and the burden is on the judge, not the text. Then act on what
you actually find:

- **the artifact is wrong** — one focused edit (a section, not a rewrite), guided by
  the `opinion`.
- **the claim overstates** — fix the claim to say what is true; never weaken, drop,
  or reword a judgment merely to pass.
- **the judge is wrong** — change *nothing*. Never pad a standard or doc with
  hedging, caveats, or filler to placate a tripped judge: that trades correct prose
  for slop, worse than a red gate. Set it aside for the user.

Two limits govern this, and you track both yourself as you loop:

- **Two fix attempts per judgment.** Still refuted after two fixes: set it aside.
- **Focused fixes only.** A refutation needing more than one focused edit is set
  aside, unfixed.

### 4. Loop

Run the workflow again. Your edits re-key the judgments you touched, so it picks up
exactly those plus anything that crashed. Stop when `ran` is 0 or nothing is left
but set-aside judgments.

With the user present, two narrow cases let you record a pass without a judge — a
false positive they concur is wrong, and a small edit they watched you make. Both
are governed by
[recording-without-a-judge.md](references/recording-without-a-judge.md); an
autonomous run does neither.

**The user is your escalation path — use it, with an example.** They sit at the main
loop for exactly the hard calls: a genuinely ambiguous artifact-vs-judge question, a
refutation you cannot confidently place, a fix larger than focused. Escalate rather
than guess or force a fix. Quote the specific thing at issue — the artifact line as
written, the claim's exact words, the precise mismatch alleged. The user is not
looking at the code, the doc, or the judgment; give them a concrete example, not an
abstract summary.

## Report

Tell the user: already cached, judged, passed, fixed-then-passed (each id + the edit
made), set aside (each id + its `opinion` or crash history + why), crashed-and-recovered.

The armed gate — `make check-judgments`, and the pre-push hook it backs — goes green
only when **every** judgment passes, so set-aside judgments keep it red by design.
Default `make check`/`make test` skip it (`SKIP_JUDGMENTS=1`); re-check with
`make check-judgments`.
