# working-docs/delegation/sandcastle/ — index

The machinery that runs an unattended stint in a sealed container through
Sandcastle, with its survey of the tool, experiments, and code. Start at
the root.

Ordering: the root, then reading order.

- [Sandcastle Working Root](/working-docs/delegation/sandcastle/ROOT.md) — The root of the sandcastle set inside delegation — the pipeline that runs an unattended stint in a sealed container, the hard bounds it runs under, how to report on it, its words, and its worklist
- [The Sandcastle Pipeline](/working-docs/delegation/sandcastle/pipeline.md) — The pipeline as built and proven — how a front runs from open to close, how fronts run in parallel, the layout inside a container, how a run is told what to do, what it guarantees, where each piece lives, and what it does not yet do
- [Sandcastle](/working-docs/delegation/sandcastle/survey.md) — What Sandcastle offers the delegation set — the driver primitives it supplies, what it leaves to the user, and what it does not cover
- [rig/](/working-docs/delegation/sandcastle/rig/index.md) — The code that runs the Sandcastle pipeline, kept here while the set is open
- [Experiment Log](/working-docs/delegation/sandcastle/experiment-log.md) — The historical record of the experiments that built the Sandcastle pipeline — for each, what was asked, what ran, and what it settled
