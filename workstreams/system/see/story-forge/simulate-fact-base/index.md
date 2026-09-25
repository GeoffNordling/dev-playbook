# workstreams/system/see/story-forge/simulate-fact-base/ — index

The repeatable run that simulates a fact base for story-forge with
many agents: the process, the workflow script, and the prompts it
reads by path. Runs write to `runs/`, which git ignores. Start at the
process.

Ordering: the process, then the files it runs.

- [Simulate a Fact Base](/workstreams/system/see/story-forge/simulate-fact-base/process.md) — The repeatable run that simulates a fact base for story-forge by throwing computation at it — one Opus agent plans the slices, one Sonnet agent per slice builds its part of the graph, one Opus agent assembles the whole — with the prompts it reads, where each agent writes, and the cross-repo cautions
- `workflow.js` — the Workflow script: three phases, each agent pointed at its prompt by path

## Directories

- [prompts/](/workstreams/system/see/story-forge/simulate-fact-base/prompts/index.md) — The three prompts the run's agents read: plan, build, and assemble
