---
type: General-Sheet
title: Assemble Prompt
description: The prompt the Opus assembler reads — run the instance script, merge every slice's kinds into one graph of kinds, connect the stub edges, draft one doc-type per kind with receipts or UNDECLARED, list the conflicts and residuals, and rank the declarations the target could add
---

# Assemble Prompt

Sonnet builders have each described the kinds of one slice of a
target repository: a fact base, a knowledge graph with a receipt on
every row, whose nodes are kinds, processes, and rules. Your job is to
assemble them into one fact base for the whole scope and to read the
structure off it.

The launch message gives you `repo` (the dev-playbook checkout),
`target` (the target root), and `run` (the run directory). Use
absolute paths. Do not change directory.

## 1. List the instances

Run the script, which applies every kind's recognition rule to the
target's tracked files:

```
python3 <repo>/workstreams/system/see/story-forge/simulate-fact-base/list_instances.py <target> <run>
```

It writes `<run>/instances.json`: the files each kind matches, and the
empty rules, unexpressible rules, overlaps, and orphans. Do not list
instances by hand. If the script fails, stop and report its error.

## 2. Read

- The theory, in `repo`: `workstreams/system/see/fact-base/fact-base.md`,
  `doc-types/reference-model.md`, and `registries/doc-types.md`.
- The plan: `<run>/partition.json`.
- Every slice: `<run>/slices/*/facts.json` and `kinds.md`.
- `<run>/instances.json`.

Open a target file only to settle a conflict or to check a receipt.

## 3. Write five files in `<run>`

**`fact-base.json`** — one merged fact base:

```json
{ "envelope": 1, "kind": "fact-base", "kind_version": 0,
  "title": "fact-base, kinds: <target name>",
  "stamp": { "commit": "<targetCommit from partition.json>",
             "generator": "simulated by agents; instances by list_instances.py" },
  "payload": { "nodes": [ ], "edges": [ ] } }
```

Keep each builder's rows and receipts. Add each kind's instance count
from `instances.json` to its `attrs.count`. Connect every `stub:`
target to the real node. A stub with no node to land on stays, with
`detail: "dangling"`. Give one kind one name across slices, and prefer
the name the target declares.

**`doc-types.md`** — open with a table: kind, count, slice, and where
the target declares it, or `inferred`. Then one section per kind, in
the shape of the doc-type system: one sentence on what an instance
is, where instances live, how one is recognised, its fields, its edges
to other kinds, the processes that read or write it, and the rules
that check it. Every claim carries a receipt or **UNDECLARED**.

**`conflicts.md`** — every place two slices disagree, and every
overlap, orphan, empty rule, and unexpressible rule from
`instances.json`, each with what it suggests.

**`residuals.md`** — what no primitive expressed, from each slice's
**Does not fit** section and from your own reading.

**`declarations.md`** — the declarations the target could add to turn
`inferred` rows into `declared` ones, ranked by how many inferred rows
each would turn. For each: what to declare, where in the target it
would go (the declared-kinds list, a standard, a check, a folder
index), and the inferred rows it would turn, by source, relation, and
target. Suggest only; the target is read-only.

## A test case

The target's `index.md` declares `Story-Projection`: it takes several
Stories and produces a new, transformed Story told from one angle.
Does the assembled graph say both halves, that a Story-Projection is
`derived-from` Story and that it is a `form-of` Story, each with a
receipt, and is each half declared or inferred? If
it does not, say what is missing, and whether the gap is in the
target's declarations or in the simulation.

## Rules

- The target is read-only. Write nothing there.
- Write only inside `<run>`.
- Privacy is a soft guardrail: add no new private content, use generic
  terms, and redact what looks personal.

Return the summary in the structured form the launch asks for.
