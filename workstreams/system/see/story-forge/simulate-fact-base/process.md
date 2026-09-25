---
type: Recipe-Description
resource: /workstreams/system/see/story-forge/simulate-fact-base/workflow.js
title: Simulate a Fact Base
description: The repeatable run that simulates a fact base for a target repository, story-forge first, by throwing computation at it — one Opus agent finds the kinds and plans slices of 3 to 5, one Sonnet agent per slice describes its kinds from samples, a script lists the instances, one Opus agent assembles the whole — with the prompts it reads, where each agent writes, how runs are kept, and the cross-repo cautions
---

# Simulate a Fact Base

## Goal

Build a fact base, a knowledge graph of nodes and edges with a receipt
on every row, for a whole target repository, without writing an
extractor first. The run throws computation at the problem: agents
read sample files and describe the repository's kinds by hand. The
result is the structure that views are drawn from, and a draft of the
doc-types the target would need to make that structure deterministic.

The process is written for any repository. story-forge is the first
target; the process lives in its workstream until a second target
uses it, then moves up to the fact base workstream.

## The run

`workflow.js` runs three phases. Each agent reads its prompt from
`prompts/` by file path; the script passes only the parameters.

1. **Plan, one Opus agent,
   [plan.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/plan.md).**
   Reads the theory, the examples, this process, and the target's top
   level. Starts from the kinds the target declares, such as
   story-forge's `okf_types` in its root `index.md`, adds the kinds it
   does not declare, groups them into slices of 3 to 5 kinds, and
   writes one short brief per slice.
2. **Build, one Sonnet agent per slice, in parallel,
   [build.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/build.md).**
   Reads its brief and 2 or 3 sample files per kind, nothing else.
   Answers the seven questions per kind, writes a recognition rule for
   each kind, and records the edges between kinds, including "form
   of". An edge that crosses into another slice is a stub.
3. **Assemble, one Opus agent,
   [assemble.md](/workstreams/system/see/story-forge/simulate-fact-base/prompts/assemble.md).**
   Runs `list_instances.py`, which applies every recognition rule to
   the target's tracked files. Merges the slices into one graph of
   kinds, connects the stubs, drafts one doc-type per kind, and lists
   the conflicts. Ranks the declarations the target could add to turn
   inferred rows into declared ones: the menu for side quests in the
   target.

The Sonnet agents never read the doc-type theory or the earlier
examples: a builder stays on its slice. The two Opus agents carry the
theory in and out. Agents describe kinds; the script lists instances,
per the principle that a hand-wave stands in for code, never for
magic.

## Where each agent writes

Every write lands in one run directory,
`simulate-fact-base/runs/<run-id>/`, which git ignores:

| Path | Written by |
|---|---|
| `partition.json`, `briefs/<slice>.md` | Plan |
| `slices/<slice>/facts.json`, `kinds.md` | Build |
| `instances.json` | `list_instances.py`, run by Assemble |
| `fact-base.json`, `doc-types.md`, `conflicts.md`, `residuals.md`, `declarations.md` | Assemble |
| `run.json` | The session that launched the run: its args and result |

## Keeping runs

Every run keeps its own directory, never overwritten, named
`<date>-<label>`. A run is deleted only when the user asks. The newest
run is the current fact base; older runs are the history to compare
against. The directories stay on disk and out of git, because they
carry the target's content; the Runs section below is the committed
log, one entry per run.

A run can grow: add slices to its directory and run Assemble again,
since Assemble reads every slice. That holds only while every slice
cites the same target commit.

## Across the repo boundary

The agents launch in a dev-playbook checkout and read a different
repository, the target.

- **Absolute paths only.** The script passes story-forge's root and the
  run directory as absolute paths. No agent changes directory.
- **Writes stay inside the launch checkout.** The run directory is
  under the dev-playbook worktree, so no agent writes outside its own
  working tree.
- **The target is read-only.** Every prompt says so. The runner checks
  it: `git -C <target> status --porcelain` is empty before the run and
  after it.
- **The target's `CLAUDE.md` is not loaded.** An agent gets the
  instruction files of the repo it launches in, dev-playbook. The plan
  agent reads the target's `CLAUDE.md` itself and carries what matters
  into the briefs.

## Bounds

At most 2 Opus agents and `maxSlices` Sonnet agents, 12 in all at the
default of 10. The script fixes the count; no agent can add work. The
script refuses a plan with more than 5 kinds in a slice. `scope`
limits a run to some folders, for a cheap check of a change to the
process before a whole-repo run.

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
        "target": "/home/geoff/workspace/story-forge",
        "run": "<repo>/workstreams/system/see/story-forge/simulate-fact-base/runs/<date>-<label>",
        "maxSlices": 10,
        "scope": "all" }
```

Before the run, check the target is clean. After it, check again,
and write the args and the result to `<run>/run.json`.

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
  - **Result.** 5 agents, 45 minutes, about 1.46M subagent tokens. 39
    kinds, 431 nodes, 900 edges, 9 dangling stubs, 22 conflicts. All
    796 cited lines exist; of 5 edges read by hand, 3 were right and 2
    cited a line that did not say what the edge claimed.
  - **Lesson: a line that exists is not a receipt.** The receipt check
    must test that the cited line holds the claim, not only that it
    exists.
  - **Lesson: kinds must be nodes.** The Projection test failed: the
    graph held files and tags, no kinds, so no row could say how
    Projection relates to Story. The relation was declared only in
    prose, in `okf_types` and in a folder index, and no builder turned
    it into a row.
  - **Lesson: the target's own declarations are the builders' first
    evidence.** story-forge declares 10 kinds in `okf_types`; the
    builders found 39. The prompts now point the agents at the
    declared kinds instead of hoping they find them.
  - **Change in the target.** After the pilot the user renamed the
    OKF type `Projection` to `Story-Projection` in story-forge
    (`84194f6`), with a description saying it produces a new,
    transformed Story. The next run tests whether the simulation reads
    that.
- **2026-09-25-kinds-stories, `maxSlices: 4`, story-forge `84194f6`,
  scope the pilot's first slice** (`stories/`, `resume/`, `career/`,
  `andrew-ng-ai-engineering-skills-map/`, `standards/stories/`,
  `standards/resume/`). The first run of the redesign: builders
  describe kinds, `list_instances.py` lists the files. 4 slices of 3 or
  4 kinds. 6 agents, 19 minutes, about 720k subagent tokens, about
  half the pilot's for about a third of its files.
  - **Result.** 13 kinds, 105 instances, 0 overlaps, 0 orphans: every
    file in scope has exactly one kind, by script. 57 edges between
    kinds, 3 dangling stubs (all to kinds out of scope), 15 conflicts.
    All 57 receipts point at real lines; 6 read by hand all hold what
    the edge claims.
  - **The Story-Projection test passes.** `form-of` is declared, from
    `index.md:12`, the `okf_types` entry the user rewrote. `reads` is
    only inferred, as `points-at` from the one instance's `sources:`
    key: no standard or check names Story-Projection, and no process
    in the target makes one.
  - **Lesson: a declaration moves a relation from inferred to
    declared.** The one-line rename in the target turned a failed test
    into a declared row. The gaps that remain are gaps in the target's
    declarations, which the simulation now reports by name.
  - **Lesson: a kind that spans folders fights the slice-by-folder
    plan.** Index lives in every folder; its slice's recognition rule
    covered only the folders in scope, and a whole-repo run must give
    such kinds one slice across all folders.
  - **Lesson: the relation words need one list.** Builders wrote
    `points-at` where the target meant "reads"; the build prompt's verbs
    are a suggestion, and the assembler can only merge what the
    builders named alike.
  - **Changes after this run.** The plan slices by kind, not folder, so
    a kind found in every folder gets one slice. The build prompt fixes
    eight relations, `derived-from` among them. The assembler writes
    `declarations.md`, a ranked list of what the target could declare
    to turn inferred rows into declared ones.

## After the run

- Check the receipts: every cited file exists and the cited line
  holds what the row claims. `list_instances.py` checks the
  recognition rules; the receipt check is not written yet.
- Render views from `fact-base.json`.
