---
type: Recipe-Description
title: Judgments
description: Filling a repo's judgment cache in one call — plan the docket, fan out one pinned judge per miss, record the passes, return only what was refuted
resource: /dotfiles/dot-claude/workflows/judgments.js
---

# Judgments

One call that takes a repo's red judgment cache gate and does everything about it a
machine can: reads the docket of uncached judgments, runs one pinned judge agent per
miss in parallel, records the passes, and hands back a compact summary whose only
actionable part is the refutations. The calling agent supplies judgment about those
refutations and nothing else.

## When to use it

When the judgment cache gate is red. This is the engine behind the `run-judgments`
skill, which is the ordinary way to reach it.

It is shaped like [scatter-gather](/harness-recipes/recipes/scatter-gather.md) rather
than built on it: the middle phase is the same single `parallel()` fan-out, written
out here rather than delegated, because this workflow takes no job list from its
caller. What it adds is the deterministic work on either side — obtaining the batch
and committing its results — so the caller never assembles a job list or interprets a
verdict.

## How it works

Three phases, of which only the middle one ever spawns more than a single agent. The
last two are conditional, so a fully-cached repo costs exactly one agent:

1. **Plan** — one cheap agent runs `uv run judgments-run plan` and returns the docket:
   the absolute CLI invocation to reuse for every later command, how many judgments
   are already cached, and for each miss its `id`, its declared `model`/`effort`, and
   a ready-to-run judge prompt. This is the one command in the flow spelled the
   ordinary way — being the bootstrap, it cannot yet know the absolute invocation it
   is about to hand back. The script cannot run a shell command itself, which is why
   this is an agent rather than a direct call.
2. **Judge** — one isolated `agent()` per uncached judgment, all at once, each pinned
   to the `model` and `effort` its own declaration names and constrained to the fixed
   `{verdict, opinion}` output schema. Skipped when the docket is empty.
3. **Record** — the script itself partitions the verdicts, then a courier agent runs a
   single `record` command — built from the invocation Plan returned — over the
   passing ids. Skipped when nothing passed.

The judge prompt is a two-line bootstrap: *run `… render <id>`, obey its stdout*. The
real prompt — the claim plus the full text of every evidence file — is produced by
that command **inside the judge's own context**, so the heavy bytes never pass through
the workflow script or the calling agent's window. The commands the CLI hands out name
an absolute interpreter and an explicit `--root`, so a judge runs them without a PATH
lookup, an activated virtualenv, or any particular working directory.

Deciding what passed is plain script code (`verdict === true`), never an agent's call,
and only passes are ever recorded. A crashed judge yields a null result that keeps its
id: a crash is not a false verdict, it means the judgment was never ruled on, so it
stays uncached and the next run picks it up.

## Running it

```js
Workflow({ name: "judgments" })
```

No arguments — it discovers its own work. The one option is a list of judgment ids to
leave unjudged, for when the caller has already set them aside:

```js
Workflow({ name: "judgments", args: { skip: ["some-id"] } })
```

It returns one summary whose only actionable field is `refuted`:

```json
{ "cached": 25, "ran": 3, "passed": ["id-a"],
  "refuted": [ {"id": "id-b", "opinion": "…what to fix…"} ],
  "crashed": ["id-c"], "skipped": [], "green": false }
```

The workflow is stateless. Fix attempts, set-aside decisions, and every judgment about
a refutation live with the caller — this runs the docket it is given and reports what
happened. Source: [`judgments.js`](/dotfiles/dot-claude/workflows/judgments.js).
