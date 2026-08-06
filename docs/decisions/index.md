# docs/decisions/ — index

The workspace's decisions and the reasoning that produced them — a record is
superseded by a later one, never rewritten.

Ordering: Decision Record number order.

- [Decision Records](/docs/decisions/README.md) — The decision records directory — numbered, immutable records of decisions and their rationale
- [Adopt Matt Pocock's Conventions](/docs/decisions/0001-adopt-matt-pocock-conventions.md) — Adopt Matt Pocock's repository conventions wholesale — 4-digit Decision Records, per-repo agent config, triage vocabulary, vertical-slice discipline — rejecting only his PRD format
- [Compounding Workflow with AI](/docs/decisions/0002-compounding-with-ai.md) — Establish tiered instruction loading — a global behavioral CLAUDE.md, nested per-project variants, and edit-time Python linting via project-local ruff
- [Decline Superpowers, Catalog Techniques](/docs/decisions/0003-decline-superpowers.md) — Decline the Superpowers framework wholesale, cataloguing its techniques for later harvest into authored workspace skills
- [Remove Pocock Direct Dependency, Absorb Conventions, Lift Engineering Skills](/docs/decisions/0004-remove-pocock-direct-dependency.md) — Cut the Pocock direct dependency — absorb load-bearing conventions into standards, lift four engineering skills into bundles, keep two utilities
- [Issue Workflow Reorganization](/docs/decisions/0005-issue-workflow-reorganization.md) — Reorganize the issue workflow around phase-on-issue labels, merging triage and creation into `/intake` and adding an `/sdd` dispatcher
- [Harvest Pocock's `prototype` and `handoff` Skills](/docs/decisions/0006-harvest-pocock-prototype-and-handoff.md) — Harvest Pocock's prototype and handoff skills into authored bundles rather than taking a direct dependency
- [Merge SDD Spec Authoring into One Phase](/docs/decisions/0007-merge-sdd-spec-authoring-phase.md) — Merge sdd-requirements and sdd-design into a single sdd-specs phase authoring the whole feat/req/dsn hierarchy in one interview
- [Retire the Edit-Time ruff Hook for a Single Pre-commit Gate](/docs/decisions/0008-retire-edit-time-ruff-hook.md) — Remove the edit-time PostToolUse ruff hook so pre-commit is the single ruff gate over every authored .py
- [Same-Repo Resolution — Keep the Written Form, Resolve Reader-Side](/docs/decisions/0009-same-repo-resolution.md) — Resolve intra-repo workspace citations against the reader's own checkout via a reader-side rule, keeping the written path form unchanged
- [Specs Join OKF — Reversing the specs/ Carve-Out](/docs/decisions/0010-specs-join-okf.md) — Reverse the planned specs/ carve-out from the OKF bundle — SDD spec items gain OKF frontmatter and per-folder indexes instead of being exempted
- [One Registry for Content the Repo Doesn't Author](/docs/decisions/0011-one-registry-for-non-authored-content.md) — Exclude non-authored content from the authored-content detectors through one shared registry — vendored trees by root, verbatim mirrors by OKF type — never a per-detector path-skip
- [One Published Hook — Enrollment Rides the Pin](/docs/decisions/0012-one-published-hook.md) — Collapse the published per-detector hook ids into one playbook-lint aggregate whose in-clone roster enrolls every consumer at pin bump
- [Uncommitted Work Lives in CANDIDATES.md, Not GitHub](/docs/decisions/0013-candidates-file-over-github-backlog.md) — Record uncommitted future work in a per-repo CANDIDATES.md rather than as open GitHub issues, reserving issues for work already committed to
- [The Workspace Spans Machines — Differences Live in Two Files](/docs/decisions/0014-workspace-spans-machines.md) — Confine every machine difference to two files named by machine key, and allow a check to be skipped only where its input is machine-local rather than held in the repository
- [Tooling Verdicts from the 2026-05 Third-Party Audit](/docs/decisions/0015-tooling-verdicts-2026-05-audit.md) — Preserve the 2026-05-08 tooling audit's verdicts and revisit conditions — claude-code-transcripts, roborev, Superset, and two Superpowers watch-threads — from the retired third-party survey
- [Matt Pocock Skills Sweep — Verdicts at the 2026-07 Pin](/docs/decisions/0016-pocock-skills-sweep-2026-07.md) — Per-skill verdicts from the sweep of mattpocock/skills at pin 2ab9580 — five installed verbatim, eleven harvested, twenty-four rejected — with the reversals the sweep produced
- [Remove SDD Support Entirely](/docs/decisions/0017-remove-sdd-support.md) — Remove both SDD systems — the factory's ratified retention with its label values, and the specs/ build layer with its Makefile.sdd validate gate — leaving no trace of the methodology outside the Decision Records
