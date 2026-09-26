---
type: General-Sheet
title: Plan Prompt
description: The prompt the Opus plan agent reads — learn what a fact base is, find the kinds of a target repository starting from the kinds it declares, group them into slices of 3 to 5 kinds, and write one short brief per slice for the Sonnet builders
---

# Plan Prompt

You plan one run that simulates a fact base for a target repository. A
fact base is a knowledge graph: nodes and edges, each row carrying a
receipt, the file and line that proves it. Sonnet agents will build
it, one slice each, in parallel. Each builder describes **kinds**
(families of files that share one form) from 2 or 3 sample files, and
writes a recognition rule; a script lists the instances afterwards. An
assembler joins the slices. Your job is to find the kinds, group them
into slices, and brief each builder.

The launch message gives you `repo` (the dev-playbook checkout),
`target` (the target root), `run` (the run directory), `maxSlices`,
and `scope`: a list of folders, or `all`. Use absolute paths. Do not
change directory.

## 1. Learn what you are planning for

Read these in `repo`:

- `workstreams/system/see/WORKSTREAM.md` — the shared principles.
- `workstreams/system/see/fact-base/fact-base.md` — what a fact base is.
- `doc-types/reference-model.md` — the doc-type system.
- `registries/doc-types.md` — how a kind of file joins a doc-type.
- `workstreams/system/see/story-forge/simulate-fact-base/process.md` —
  this process, and the lessons of earlier runs in its Runs section.

Then the examples. They are inspiration and a warm start, not a
template:

- `workstreams/system/see/story-forge/stories-fact-base.md` — one
  kind, Story, done in full.
- `workstreams/system/see/fact-base/fact-base-ralph.md` — the same
  method on another subsystem.

## 2. Read the target's top level

In `target`: `CLAUDE.md`, the root `index.md`, `CONTEXT.md`,
`standards/index.md`, and the `index.md` of each top-level directory,
where they exist. Record the commit: `git -C <target> rev-parse HEAD`.
List the tracked files with `git -C <target> ls-files`. When `scope`
is a list of folders, keep only the files under them.

**Start from the kinds the target declares.** A repository may list
its own types, such as the `okf_types` map in the frontmatter of the
root `index.md`, and its files may carry a `type:` frontmatter value.
Every declared kind in scope becomes a kind in your plan, under its
declared name. Then add the kinds the target does not declare: skills,
scripts, standards, indexes, config, and so on. Mark those as guesses.

## 3. Group the kinds into slices

Make at most `maxSlices` slices. Rules:

- Each slice holds **3 to 5 kinds**. A kind belongs to one slice, so no
  two builders describe the same kind.
- Slice by kind, not by folder. A kind whose files live in many
  folders, such as an index, a standard, a skill, or a script, belongs
  to one slice whose recognition rule covers every folder in scope.
  Give such kinds a slice of their own where you can.
- Keep kinds that point at each other in the same slice where you can,
  so fewer edges leave a slice.
- Every file in scope should belong to some kind. List the files you
  cannot place in `unplaced`; the script reports them again later.

## 4. Write the outputs

Write `<run>/partition.json`:

```json
{ "targetCommit": "<sha>", "scope": ["<folder>", "..."] ,
  "declaredKinds": { "<Name>": "<file>:<line>" },
  "slices": [ { "id": "<kebab-case>", "kinds": ["..."], "folders": ["..."],
                "edgesOut": ["<kind> -> <kind>"] } ],
  "unplaced": ["..."] }
```

Write `<run>/briefs/<id>.md` for each slice. A brief is short, under
40 lines, and holds only what the builder needs for its own slice:

- the kinds it owns; for a declared kind, quote the declaration with
  its file and line; mark the others as guesses;
- the folders where their files live, and 2 or 3 sample paths per kind;
- the edges you expect to leave the slice;
- any convention from the target's `CLAUDE.md`, `CONTEXT.md`, or
  standards that applies to these kinds, with its path.

Put no doc-type theory in a brief. The builder already has a generic
prompt that says what to record and how.

## Rules

- The target is read-only. Write nothing there.
- Write only inside `<run>`.
- Privacy is a soft guardrail: add no new private content, use generic
  terms, and redact what looks personal.

Return the slice list in the structured form the launch asks for.
