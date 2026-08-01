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
See the [declaration format](~/workspace/dev-playbook/standards/judgments/declarations.md).

This skill turns a red gate green. Steps 1–3 below are mechanical: run a command,
pass its output on untouched, run the command you get back. **Copy, never compose** —
each hand-off is one opaque string, and reading, summarizing, or editing it is how
this goes wrong. Your judgment is spent on step 4 and nowhere else: **weighing each
refutation and making the fixes it warrants.**

**Main loop only.** The `Workflow` tool exists only at the main loop; a subagent does
not have it, must **surface** a red gate rather than work around it, and must never
hand-roll judge calls — that bypasses the per-judgment `model`/`effort` pinning and
the fixed output schema, producing off-bench verdicts that must not be recorded.

## The loop

### 1. Plan

```
uv run judgments-run plan
```

Run it in your own working directory — do not `cd` first. If you are standing in a
worktree, that worktree is the repository to judge. It prints one line of JSON: the
workflow's complete argument payload, already filtered and ready.

The one thing you read in it is `jobs`. **`"jobs": []` ends the loop** — every
judgment is either cached or set aside, and there is nothing to dispatch. Otherwise
the whole line goes to step 2 untouched.

### 2. Judge

```js
Workflow({ name: "judgments", args: <the JSON from step 1, verbatim> })
```

That JSON becomes the `args` value itself — an object in the tool call, not a quoted
string wrapping one. Change nothing inside it.

The result arrives inline in the workflow's task notification. If you instead open
the task's output file, that file is a wrapper — the workflow's own return value is
under its top-level **`result`** key, not at the top level.

```json
{ "record": "/…/python -m … --root /… record id-a",
  "cached": 25, "ran": 3, "passed": ["id-a"],
  "refuted": [ {"id": "id-b", "opinion": "…what to fix…"} ],
  "crashed": ["id-c"], "skipped": [], "green": false }
```

### 3. Record

`record` is a complete shell command. Run it verbatim. It is `null` when nothing
passed — then there is nothing to run. If it fails, the copy was mangled: it records
all or nothing, so copy it again exactly rather than retyping it or dropping an id.

Do this before anything else. Until it runs, the verdicts exist only in that result,
and a re-plan will re-judge everything that passed.

### 4. Weigh each refutation, then act

`refuted` is the only field that needs a mind. `green` means nothing in this run does.

A **crash is not a verdict** — that judgment was never ruled on, stays uncached, and
is picked up by simply looping again; no fix, no attempt consumed. Twice running is
an environment problem: set it aside and say so.

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

### 5. Loop

Back to step 1. Your edits re-key the judgments you touched, so the next plan picks
up exactly those plus anything that crashed. Name what you have set aside so it is
not re-judged:

```
uv run judgments-run plan --skip some-id --skip another-id
```

The loop ends at step 1, when the plan comes back with an empty `jobs`. With the
user present, two narrow cases let you record a pass without a judge — a false positive they concur is wrong, and a small edit they
watched you make — both governed by
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
