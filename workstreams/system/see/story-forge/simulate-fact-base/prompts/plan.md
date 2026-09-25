---
type: General-Sheet
title: Plan Prompt
description: The prompt the Opus plan agent reads — learn what a fact base is, split story-forge into slices with every file in exactly one, and write one short brief per slice for the Sonnet builders
---

# Plan Prompt

You plan one run that simulates a fact base for the story-forge
repository. A fact base is a knowledge graph: nodes and edges, each
row carrying a receipt, the file and line that proves it. Sonnet
agents will build it, one slice each, in parallel. An assembler joins
their slices afterwards. Your job is to split the repository into
slices and to brief each builder.

The launch message gives you `repo` (the dev-playbook checkout),
`storyForge` (the story-forge root), `run` (the run directory), and
`maxSlices`. Use absolute paths. Do not change directory.

## 1. Learn what you are planning for

Read these in `repo`:

- `workstreams/system/see/WORKSTREAM.md` — the shared principles.
- `workstreams/system/see/fact-base/fact-base.md` — what a fact base is.
- `doc-types/reference-model.md` — the doc-type system.
- `registries/doc-types.md` — how a kind of file joins a doc-type.
- `workstreams/system/see/story-forge/WORKSTREAM.md` — the rules for
  work on story-forge.

Then the examples. They are inspiration and a warm start, not a
template:

- `workstreams/system/see/story-forge/stories-fact-base.md` and the
  first rows of `stories-fact-base.json` — one story-forge kind, Story,
  done in full.
- `workstreams/system/see/fact-base/fact-base-ralph.md` — the same
  method on another subsystem.
- `workstreams/system/see/story-forge/story-forge-survey.md` — an
  earlier map of story-forge. Treat its claims as hypotheses.

## 2. Read story-forge's top level

In `storyForge`: `CLAUDE.md`, `index.md` (its `okf_types` frontmatter
declares the kinds), `CONTEXT.md`, `standards/index.md`, and the
`index.md` of each top-level directory. Record the commit:
`git -C <storyForge> rev-parse HEAD`. List every tracked file with
`git -C <storyForge> ls-files`.

## 3. Split into slices

Make between 3 and `maxSlices` slices. Rules:

- Every tracked file belongs to exactly one slice. Code, scripts,
  tests, and config belong to a slice too.
- A kind belongs to one slice, so no two builders describe the same
  kind.
- Balance the work: a slice with many files of one simple kind can be
  large; a slice of many different kinds stays small.

## 4. Write the outputs

Write `<run>/partition.json`:

```json
{ "storyForgeCommit": "<sha>",
  "slices": [ { "id": "<kebab-case>", "folders": ["..."], "files": ["..."],
                "kindsExpected": ["..."], "edgesOut": ["<kind> -> <kind>"] } ] }
```

Write `<run>/briefs/<id>.md` for each slice. A brief is short, under
40 lines, and holds only what the builder needs for its own slice:

- the folders and files it owns;
- the kinds you expect it to find, marked as guesses;
- the edges you expect to leave the slice;
- any convention from story-forge's `CLAUDE.md`, `CONTEXT.md`, or
  standards that applies to these files, with its path;
- optional: an existing data file it may start from, such as
  `stories-fact-base.json` for the slice that owns `stories/`.

Put no doc-type theory in a brief. The builder already has a generic
prompt that says what to record and how.

## Rules

- story-forge is read-only. Write nothing there.
- Write only inside `<run>`.
- Privacy is a soft guardrail: add no new private content, use generic
  terms, and redact what looks personal.

Return the slice list in the structured form the launch asks for.
