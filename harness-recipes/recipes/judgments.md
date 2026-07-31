---
type: Recipe-Description
title: Judgments
description: Judging a repo's uncached judgments in one parallel fan-out — the docket arrives as an argument, one pinned judge per entry, verdicts partitioned by the script
resource: /dotfiles/dot-claude/workflows/judgments.js
---

# Judgments

One parallel fan-out that judges a docket of uncached judgments: one isolated
agent per judgment, each pinned to the model and effort its own declaration
names, with the verdicts partitioned by the script rather than by any model. It
hands back a ready-to-run `record` command for the passes and the refutations to
weigh. It plans nothing and records nothing — both are shell work, and this layer
has no shell.

## When to use it

When the judgment cache gate is red. This is the engine behind the `run-judgments`
skill, which is the ordinary way to reach it.

It is shaped like [scatter-gather](/harness-recipes/recipes/scatter-gather.md)
rather than built on it: the fan-out is the same single `parallel()` over
per-job-pinned agents, written out here rather than delegated. What it adds is a
fixed job shape — every job is "judge one declared claim" — so the caller passes
a docket rather than assembling prompts, and gets verdicts partitioned rather than
raw results.

## Why the docket arrives as an argument

Planning a run means keying every judgment and asking the seen-set which keys it
already holds. That is deterministic work that has to read files, and the three
layers of a run each afford only one kind of work:

| Layer | Deterministic? | Reads files? |
|---|---|---|
| the Claude Code session, through its Bash tool | yes | yes |
| this workflow script | yes | **no** |
| a judge agent | no | yes |

The Workflow runtime gives a script `agent()`, `parallel()`, `pipeline()`,
`phase()`, `log()` and `args` — no filesystem, no subprocess, no network. So the
only place that is both deterministic and able to read the repo is the session's
Bash tool, and planning happens there, before this workflow is called.

An earlier version spawned a cheap agent to run the planner and transcribe its
output. That agent had discretion it should never have had over a pure function,
and it used it — it left the worktree it was launched in and planned the main
checkout instead. The docket is an argument now, and every agent this workflow
spawns is a judge.

## How it works

One phase. `judgments-run plan` has already produced the entire argument payload,
so the script's whole job is to validate it, fan out, and partition:

1. **Validate** the plan: exactly the seven keys the CLI emits, no more and no
   fewer; a `cli` carrying an explicit `--root`; a `judge_prompt` with its `{id}`
   placeholder intact; a well-formed job list within the runtime's agent cap.
   Every check runs before a single agent spawns, and every failure is fatal —
   a plan that does not match is a plan that did not come from the CLI.
2. **Judge** — one isolated `agent()` per job, all at once, each pinned to that
   job's `model` and `effort` and constrained to the plan's `{verdict, opinion}`
   schema. An empty docket spawns nothing and returns the same result shape.
3. **Partition** — plain script code, never an agent's call: `verdict === true`
   is a pass, `verdict === false` is a refutation carrying its `opinion`, and a
   null result is a crash. A crash is not a false verdict; it means the judgment
   was never ruled on, so it stays uncached and the next run picks it up.

The judge prompt is a bootstrap: *run `… render <id>`, obey its stdout*. The real
prompt — the claim plus the full text of every evidence file — is produced by that
command **inside the judge's own context**, so the heavy bytes never pass through
this script or the calling agent's window. The prompt ships once, with `{id}`
where the judgment id goes, rather than once per job: only the id varies, and
repeating the rest would multiply the payload the caller carries for nothing.

Every command in the run is built from the plan's `cli`, which names an absolute
interpreter and an explicit `--root` — so a judge runs it without a PATH lookup,
an activated virtualenv, or any particular working directory.

## Running it

Run the planner, then pass its stdout through unedited:

```
uv run judgments-run plan          # → one line of JSON
```

```js
Workflow({ name: "judgments", args: <that JSON, verbatim> })
```

`args` is required. To leave judgments unjudged, name them to the planner —
`judgments-run plan --skip some-id --skip another-id` — so the payload stays
something the caller copies rather than edits.

It returns one summary, `record` first because it is the one thing to act on
before anything else:

```json
{ "record": "/…/python -m dev_playbook.judgments.runner --root /… record id-a",
  "cached": 25, "ran": 3, "passed": ["id-a"],
  "refuted": [ {"id": "id-b", "opinion": "…what to fix…"} ],
  "crashed": ["id-c"], "skipped": [], "green": false }
```

`record` is the exact command to run, over ids this script computed and no agent
chose; it is `null` when nothing passed. `green` means nothing in this run needs a
human mind — everything that ran passed, nothing crashed, nothing was set aside —
but the gate itself goes green only once `record` has run.

The workflow is stateless. Fix attempts, set-aside decisions, and every judgment
about a refutation live with the caller. Source:
[`judgments.js`](/dotfiles/dot-claude/workflows/judgments.js).
