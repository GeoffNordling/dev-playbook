---
type: General-Sheet
title: Assemble Prompt
description: The prompt the Opus assembler reads — merge every slice into one fact base, connect the stub edges, draft one doc-type per kind with receipts or UNDECLARED, and list the conflicts and residuals
---

# Assemble Prompt

Sonnet builders have each built a fact base, a knowledge graph with a
receipt on every row, for one slice of the story-forge repository. Your
job is to assemble them into one fact base for the whole repository and
to read the structure off it.

The launch message gives you `repo` (the dev-playbook checkout),
`storyForge` (the story-forge root), and `run` (the run directory). Use
absolute paths. Do not change directory.

## 1. Read

- The theory, in `repo`: `workstreams/system/see/fact-base/fact-base.md`,
  `doc-types/reference-model.md`, and `registries/doc-types.md`.
- The plan: `<run>/partition.json`.
- Every slice: `<run>/slices/*/facts.json`, `kinds.md`, `boundary.md`.

Open a story-forge file only to settle a conflict or to check a
receipt.

## 2. Write four files in `<run>`

**`fact-base.json`** — one merged fact base:

```json
{ "envelope": 1, "kind": "fact-base", "kind_version": 0,
  "title": "fact-base, whole repo: story-forge",
  "stamp": { "commit": "<storyForgeCommit from partition.json>",
             "generator": "simulated by agents; no module exists" },
  "payload": { "nodes": [ ], "edges": [ ] } }
```

Keep each builder's rows and receipts. Connect every `stub:<path>`
target to the real node. A stub with no node to land on stays, with
`detail: "dangling"`. Give one kind one name across slices.

**`doc-types.md`** — one section per kind in the whole repository, in
the shape of the doc-type system: one sentence on what an instance
is, where instances live and how many, how one is recognised, its
fields, its edges to other kinds, the processes that read or write it,
and the rules that check it. Every claim carries a receipt or
**UNDECLARED**. Open with a table: kind, count, slice, declared or not
in story-forge's `index.md` `okf_types`.

**`conflicts.md`** — every place two slices disagree: a kind named two
ways, an edge one side records and the other does not, a count that
does not match.

**`residuals.md`** — what no primitive expressed, from each slice's
**Does not fit** section and from your own reading.

## A test case

A Projection is a form of a Story. Does the assembled graph say so,
with a receipt? If it does not, say what is missing.

## Rules

- story-forge is read-only. Write nothing there.
- Write only inside `<run>`.
- Privacy is a soft guardrail: add no new private content, use generic
  terms, and redact what looks personal.

Return the summary in the structured form the launch asks for.
