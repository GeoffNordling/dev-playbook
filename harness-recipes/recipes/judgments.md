---
type: Recipe-Description
title: Judgments
description: Judging a multi-root docket of uncached judgments in one parallel fan-out — the docket arrives as an argument, one pinned judge per entry, verdicts partitioned by the script
resource: /dotfiles/dot-claude/workflows/judgments.js
---

# Judgments

One parallel fan-out that judges a docket of uncached judgments from any
number of repos: one isolated agent per judgment, each pinned to the model
and effort its own declaration names, with the script partitioning the
verdicts. It hands back ready-to-run per-root `record` commands for the
passes and the refutations to weigh. Planning and recording happen in the
shell, outside this layer.

## When to use it

When a judgments sweep is dispatching its docket. This is the engine behind
the [`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
skill, which is the ordinary way to reach it.

It is shaped like [scatter-gather](/harness-recipes/recipes/scatter-gather.md)
rather than built on it: the fan-out is the same single `parallel()` over
per-job-pinned agents, written out here. What it adds is a fixed job shape —
every job is "judge one declared claim" — so the caller passes a docket
rather than assembling prompts, and gets verdicts partitioned rather than raw
results.

## Why the docket arrives as an argument

Planning a run means keying every judgment and asking the seen-set which
keys it already holds. That is deterministic work that has to read files,
and the layers of a run each afford only one kind of work:

| Layer | Deterministic? | Reads files? |
|---|---|---|
| the Claude Code session, through its Bash tool | yes | yes |
| this workflow script | yes | **no** |
| a judge agent | no | yes |

The Workflow runtime gives a script `agent()`, `parallel()`, `pipeline()`,
`phase()`, `log()` and `args` — no filesystem, no subprocess, no network. So
the only place that is both deterministic and able to read the repo is the
session's Bash tool, and planning happens there, before this workflow is
called.

An earlier version spawned a cheap agent to run the planner and transcribe
its output. That agent had discretion it should never have had over a pure
function: it left the worktree it was launched in and planned the main
checkout instead. The docket is an argument now, and every agent this
workflow spawns is a judge.

## How it works

One phase. `judgments-run plan` has produced the entire argument payload, so
the script's whole job is to validate it, fan out, and partition:

1. **Validate** the plan: exactly the six keys the CLI emits; a
   `judge_prompt` with its `{cli}`/`{root}`/`{id}` placeholders intact; a
   `roots` map naming every swept repo; a well-formed job list, each job's
   `root` inside that map, within the runtime's agent cap. Every check runs
   before a single agent spawns, and every failure is fatal: a mismatched
   plan did not come from the CLI.
2. **Judge** — one isolated `agent()` per job across every root, all in one
   fan-out, so a bulk sweep costs one round; each pinned to that job's
   `model` and `effort` and constrained to the plan's `{verdict, opinion}`
   schema. An empty docket spawns nothing and returns the same result shape.
3. **Partition** — plain script code, never an agent's call: `verdict ===
   true` is a pass, `verdict === false` is a refutation carrying its
   `opinion`, and a null result is a crash. A crash is not a false verdict;
   it means the judgment was never ruled on, so it stays uncached and the
   next run picks it up. Every entry keeps its root — two repos can declare
   the same id, and a refutation is weighed against the repo that declared
   it.

The judge prompt is a bootstrap: *run `… --root <root> render <id>`, obey
its stdout*. The real prompt — the claim plus the full text of every
evidence file — is produced by that command **inside the judge's own
context**, so the heavy bytes never pass through this script or the calling
agent's window. The prompt ships once, with `{cli}`/`{root}`/`{id}` where
each job's coordinates go, rather than once per job: only those vary, and
repeating the rest would multiply the payload the caller carries for
nothing.

Every command in the run is built from the plan's `cli` — an absolute,
root-free interpreter invocation — plus a substituted explicit `--root`, so a
judge runs it without a PATH lookup, an activated virtualenv, or any
particular working directory.

## Running it

Run the planner over the roots to sweep, then pass its stdout through
unedited:

```
uv run judgments-run --root /abs/repo-a --root /abs/repo-b plan   # → one line of JSON
```

```js
Workflow({ name: "judgments", args: <that JSON, verbatim> })
```

`args` is required. To leave judgments unjudged, name them to the planner —
`judgments-run --root … plan --skip some-id --skip another-id` — so the
payload stays something the caller copies rather than edits.

It returns one summary, `record` first because it is the one thing to act
on before anything else:

```json
{ "record": [
    "/…/python -m dev_playbook.judgments.runner --root /…/repo-a record id-a"
  ],
  "roots": { "/…/repo-a": {"cached": 25}, "/…/repo-b": {"cached": 16} },
  "ran": 3,
  "passed": [ {"id": "id-a", "root": "/…/repo-a"} ],
  "refuted": [ {"id": "id-b", "root": "/…/repo-b", "opinion": "…what to fix…"} ],
  "crashed": [ {"id": "id-c", "root": "/…/repo-a"} ],
  "skipped": [], "green": false }
```

`record` is the exact commands to run — one per root that had passes, over
ids this script computed; it is empty when nothing passed. `green` means
nothing in this run needs the user — everything that ran passed, nothing
crashed, nothing was set aside — but the cache fills only once every
`record` command has run.

The workflow is stateless. Fix attempts, set-aside decisions, and every
judgment about a refutation live with the caller. Source:
[`judgments.js`](/dotfiles/dot-claude/workflows/judgments.js).
