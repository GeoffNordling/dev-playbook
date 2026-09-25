---
type: Recipe-Description
resource: /workstreams/system/see/story-forge/simulate-fact-base/workflow.js
title: Simulate a Fact Base
description: The repeatable run that simulates a fact base for story-forge by throwing computation at it — one Opus agent plans the slices, one Sonnet agent per slice builds its part of the graph, one Opus agent assembles the whole — with the prompts it reads, where each agent writes, and the cross-repo cautions
---

# Simulate a Fact Base

## Goal

Build a fact base, a knowledge graph of nodes and edges with a receipt
on every row, for the whole story-forge repository, without writing
an extractor first. The run throws computation at the problem: many
agents read the files and write the rows by hand. The result is the
structure that views are drawn from, and a draft of the doc-types
story-forge would need to make that structure deterministic.

The run is repeatable. Each run writes to its own directory under
`runs/`, so two runs can be compared.

## The run

`workflow.js` runs three phases. Each agent reads its prompt from
`prompts/` by file path; the script passes only the parameters.

1. **Plan, one Opus agent,
   [plan.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/plan.md).**
   Reads the theory, the examples, and story-forge's top level. Splits
   story-forge into slices, every file in exactly one slice, and
   writes one short brief per slice.
2. **Build, one Sonnet agent per slice, in parallel,
   [build.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/build.md).**
   Reads its brief and its own folders, nothing else. Records the
   fundamental objects of its slice as nodes and edges, and leaves an
   edge that crosses into another slice as a stub.
3. **Assemble, one Opus agent,
   [assemble.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/assemble.md).**
   Reads every slice and the theory. Merges the slices into one fact
   base, connects the stubs, drafts one doc-type per kind, and lists
   the conflicts.

The Sonnet agents never read the doc-type theory or the earlier
examples: a builder stays on its slice. The two Opus agents carry the
theory in and out.

## Where each agent writes

Every write lands in one run directory,
`simulate-fact-base/runs/<run-id>/`, which git ignores:

| Path | Written by |
|---|---|
| `partition.json`, `briefs/<slice>.md` | Plan |
| `slices/<slice>/facts.json`, `kinds.md`, `boundary.md` | Build |
| `fact-base.json`, `doc-types.md`, `conflicts.md`, `residuals.md` | Assemble |

## Across the repo boundary

The agents launch in a dev-playbook checkout and read a different
repository, story-forge.

- **Absolute paths only.** The script passes story-forge's root and the
  run directory as absolute paths. No agent changes directory.
- **Writes stay inside the launch checkout.** The run directory is
  under the dev-playbook worktree, so no agent writes outside its own
  working tree.
- **story-forge is read-only.** Every prompt says so. The runner checks
  it: `git -C ~/workspace/story-forge status --porcelain` is empty
  before the run and after it.
- **story-forge's `CLAUDE.md` is not loaded.** An agent gets the
  instruction files of the repo it launches in, dev-playbook. The plan
  agent reads story-forge's `CLAUDE.md` itself and carries what
  matters into the briefs.

## Bounds

At most 2 Opus agents and `maxSlices` Sonnet agents, 8 in all at the
default of 6. The script fixes the count; no agent can add work.

## Privacy

A soft guardrail, not a gate: add no new private content. Use generic
terms where you can, and redact what looks personal, such as a
person's name, an employer, or a story's body text.

## How to run

In a Claude Code session in this worktree, ask for the workflow by
path, with a new run id:

```
Workflow scriptPath: workstreams/system/see/story-forge/simulate-fact-base/workflow.js
args: { "repo": "<absolute path of this checkout>",
        "storyForge": "/home/geoff/workspace/story-forge",
        "run": "<repo>/workstreams/system/see/story-forge/simulate-fact-base/runs/<run-id>",
        "maxSlices": 6 }
```

## Runs

- **2026-09-25-pilot, `maxSlices: 3`, story-forge `3a1d875`.** The plan
  made 3 slices of 105 to 128 files each, one expecting 19 kinds. Each
  Sonnet builder grew to about 220k to 230k tokens of context, too
  much to trust. The builders spent most of it typing one row per
  instance by hand: one `facts.json` reached 154 KB. Two first
  attempts ended as interrupted, not failed, and were retried from
  scratch. story-forge stayed clean.
  - **Lesson: agents describe kinds, a script lists instances.** A
    builder reads 2 or 3 sample files per kind and answers the seven
    questions; a script finds every instance from the encoding the
    builder reports. Listing instances is extractor work, and a
    hand-wave stands in for code.
  - **Lesson: small slices.** About 3 to 5 kinds per builder, not 8 to
    19; more builders, each small.

## After the run

- Check the receipts: every cited file exists and the cited line
  holds what the row claims. A script does this; it is not written
  yet.
- Render views from `fact-base.json`.
