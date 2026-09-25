# workstreams/system/see/story-forge/simulate-fact-base/prompts/ — index

The three prompts the run's agents read: plan, build, and assemble.

Ordering: run order.

- [Plan Prompt](/workstreams/system/see/story-forge/simulate-fact-base/prompts/plan.md) — The prompt the Opus plan agent reads — learn what a fact base is, find the kinds of a target repository starting from the kinds it declares, group them into slices of 3 to 5 kinds, and write one short brief per slice for the Sonnet builders
- [Build Prompt](/workstreams/system/see/story-forge/simulate-fact-base/prompts/build.md) — The prompt every Sonnet builder reads — describe the kinds of one slice of a target repository from sample files, answer seven questions per kind with a receipt or UNDECLARED, give each kind a recognition rule a script can apply, and record the edges between kinds in a fixed list of relations
- [Assemble Prompt](/workstreams/system/see/story-forge/simulate-fact-base/prompts/assemble.md) — The prompt the Opus assembler reads — run the instance script, merge every slice's kinds into one graph of kinds, connect the stub edges, draft one doc-type per kind with receipts or UNDECLARED, list the conflicts and residuals, and rank the declarations the target could add
