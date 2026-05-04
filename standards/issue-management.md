# Issue Management

How issues are tracked, triaged, and broken down into deliverable units.

## Source of truth

The operational rules live in three Matt Pocock skill bundles. The skills are
the source of truth; this file exists only to point at them and to position
issues against the other artifacts in the workspace.

- /triage — triage state machine, agent brief format, `.out-of-scope/`
  knowledge base.
- /to-issues — vertical-slice breakdown rules and issue body template.
- /setup-matt-pocock-skills — per-repo configuration scaffolding
  (`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`,
  `docs/agents/domain.md`).

## Scope

Issues are the unit of *delivery*. Every actionable change flows through the
issue tracker.

Distinct from:

- [SDD spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md)
  — formal requirements with traceability. Specs say what must be true;
  issues say what work delivers it.
- `CONTEXT.md` — domain glossary.
- `ROADMAP.md` — strategic goals.
- `BUSINESS_CONTEXT.md` — business problem.

## What this standard does not cover

| Concern | Where it lives |
|---|---|
| Strategic goals, aspirations | `ROADMAP.md` |
| Business problem and stakeholders | `BUSINESS_CONTEXT.md` |
| Domain glossary (terms, relationships) | `CONTEXT.md` |
| Formal requirements with traceability | `specs/` (see [SDD standards](~/workspace/dev-playbook/sdd-standards/README.md)) |
| File hierarchy and ADR conventions | [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md) |
| Testing rules | [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) |
