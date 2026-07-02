# docs/adr/ — index

- [Architecture Decision Records](/docs/adr/README.md) — The architecture decision records directory — numbered, immutable records of decisions and their rationale
- [Adopt Matt Pocock's Conventions](/docs/adr/0001-adopt-matt-pocock-conventions.md) — Adopt Matt Pocock's repository conventions wholesale — 4-digit ADRs, per-repo agent config, triage vocabulary, vertical-slice discipline — rejecting only his PRD format
- [Compounding Workflow with AI](/docs/adr/0002-compounding-with-ai.md) — Establish tiered instruction loading — a global behavioral CLAUDE.md, nested per-project variants, and edit-time Python linting via project-local ruff
- [Decline Superpowers, Catalog Techniques](/docs/adr/0003-decline-superpowers.md) — Decline the Superpowers framework wholesale, cataloguing its techniques for later harvest into authored workspace skills
- [Remove Pocock Direct Dependency, Absorb Conventions, Lift Engineering Skills](/docs/adr/0004-remove-pocock-direct-dependency.md) — Cut the Pocock direct dependency — absorb load-bearing conventions into standards, lift four engineering skills into bundles, keep two utilities
- [Issue Workflow Reorganization](/docs/adr/0005-issue-workflow-reorganization.md) — Reorganize the issue workflow around phase-on-issue labels, merging triage and creation into `/intake` and adding an `/sdd` dispatcher
- [Harvest Pocock's `prototype` and `handoff` Skills](/docs/adr/0006-harvest-pocock-prototype-and-handoff.md) — Harvest Pocock's prototype and handoff skills into authored bundles rather than taking a direct dependency
- [Merge SDD Spec Authoring into One Phase](/docs/adr/0007-merge-sdd-spec-authoring-phase.md) — Merge sdd-requirements and sdd-design into a single sdd-specs phase authoring the whole feat/req/dsn hierarchy in one interview
- [Retire the Edit-Time ruff Hook for a Single Pre-commit Gate](/docs/adr/0008-retire-edit-time-ruff-hook.md) — Remove the edit-time PostToolUse ruff hook so pre-commit is the single ruff gate over every authored .py
