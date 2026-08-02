# docs/ — index

What the repo has decided and what it has observed — surveys of outside
tooling, notes on the workspace's own machinery, and the Decision Records.
Nothing here governs; the standards do that.

- [Abstraction Calibration](/docs/abstraction-calibration.md) — Where the human should live in an AI-written repo — the slop trench, the pandas standard, and the bet on invented, deterministically-enforced primitives
- [Machines](/docs/machines.md) — The machines the workspace runs on — one Fedora primary and two Windows/WSL secondaries — and what differs between them
- [Measurement Derivation](/docs/measurement-derivation.md) — How raw captured hook events become measurements — the store, the assertions every report runs first, event semantics, filters, and metric formulas
- [Sandboxing Claude agents](/docs/sandboxing.md) — Comparing sandbox solutions for isolating a Claude agent's filesystem, network, and processes
- [Workflow-runtime primitives and agent definitions](/docs/workflow-runtime-primitives.md) — The Workflow runtime's scripting primitives and the custom agent-definition frontmatter surface, each claim traced to a primary source

## Directories

- [decisions/](/docs/decisions/index.md) — The Decision Records directory — numbered, immutable records of decisions and their rationale
