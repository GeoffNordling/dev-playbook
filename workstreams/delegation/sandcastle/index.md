# workstreams/delegation/sandcastle/ — index

The machinery that runs an unattended stint in a sealed container through
Sandcastle, with its survey of the tool, experiments, and code. Start at
the head file.

Ordering: the head file, then reading order.

- [Sandcastle Workstream](/workstreams/delegation/sandcastle/WORKSTREAM.md) — The head file of the sandcastle workstream inside delegation — the pipeline that runs an unattended stint in a sealed container, the hard bounds it runs under, how to report on it, its words, and its worklist
- [The Sandcastle Pipeline](/workstreams/delegation/sandcastle/pipeline.md) — The pipeline as built and proven — how a stint's run goes from open to close, how stints run in parallel, the layout inside a container, how a run is told what to do, what it guarantees, where each piece lives, and what it does not yet do
- [Sandcastle](/workstreams/delegation/sandcastle/survey.md) — What Sandcastle offers the delegation workstream — the driver primitives it supplies, what it leaves to the user, and what it does not cover
- [rig/](/workstreams/delegation/sandcastle/rig/index.md) — The code that runs the Sandcastle pipeline, kept here while the workstream is open
- [Experiment Log](/workstreams/delegation/sandcastle/experiment-log.md) — The historical record of the experiments that built the Sandcastle pipeline — for each, what was asked, what ran, and what it settled
