# workstreams/system/see/story-forge/simulate-fact-base/ — index

The repeatable run that simulates a fact base for a target
repository, story-forge first, with many agents: the process, the workflow script, and the prompts it
reads by path. Runs write to `runs/`, which git ignores. Start at the
process.

Ordering: the process, then the files it runs.

- [Simulate a Fact Base](/workstreams/system/see/story-forge/simulate-fact-base/process.md) — The repeatable run that simulates a fact base for a target repository, story-forge first, by throwing computation at it — one Opus agent finds the kinds and plans slices of 3 to 5, one Sonnet agent per slice describes its kinds from samples, a script lists the instances, one Opus agent assembles the whole — with the prompts it reads, where each agent writes, how runs are kept, and the cross-repo cautions
- `workflow.js` — the Workflow script: three phases, each agent pointed at its prompt by path
- `list_instances.py` — applies every kind's recognition rule to the target's tracked files and reports counts, overlaps, and orphans

## Directories

- [prompts/](/workstreams/system/see/story-forge/simulate-fact-base/prompts/index.md) — The three prompts the run's agents read: plan, build, and assemble
