# Issue Management

How issues are tracked, triaged, and broken down into deliverable units.

## Purpose

Issues are the unit of *delivery*. Every actionable change — a bug to fix, a
feature to ship, a slice of a larger plan — flows through the issue tracker
under this standard. The standard prescribes:

- A canonical vocabulary for triage labels
- The state machine those labels drive
- The breakdown rules that turn a plan or spec into independently-grabbable
  issues
- Issue and agent-brief templates
- The per-repo configuration agent skills read to apply all of the above

This standard is paired with the agent skills `/triage`, `/to-issues`, and
`/setup-matt-pocock-skills`. The skills are the runtime workflow; this
document is the canonical *what*.

Distinct from:

- [SDD spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md)
  — formal requirements with traceability. Specs say what must be true;
  issues say what work delivers it.
- `CONTEXT.md` — domain glossary of terms and relationships.
- `ROADMAP.md` — strategic goals.
- `BUSINESS_CONTEXT.md` — business problem.

## Triage labels

Every triaged issue carries exactly one **category** label and exactly one
**state** label. Conflicting state labels `SHALL` be flagged with the
maintainer and resolved before any other action.

### Categories

| Label | Meaning |
|---|---|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |

### States

| Label | Meaning |
|---|---|
| `needs-triage` | Maintainer needs to evaluate |
| `needs-info` | Waiting on reporter for more information |
| `ready-for-agent` | Fully specified, ready for an AFK agent to pick up |
| `ready-for-human` | Requires human implementation (judgment, external access, manual testing) |
| `wontfix` | Will not be actioned |

These are the canonical names. A repo `MAY` use different label strings in
its tracker (e.g. `bug:triage` instead of `needs-triage`); the mapping is
recorded in that repo's `docs/agents/triage-labels.md` (see
[Per-repo configuration](#per-repo-configuration)).

## State machine

```
                        (new issue)
                             |
                             v
                       needs-triage <─┐
                             |        │
            ┌────────┬───────┼────────┤
            v        v       v        v
       needs-info  ready-  ready-   wontfix
                   for-    for-
                   agent   human
            │
            └─────(reporter replies)─┘
```

- An unlabeled issue normally enters `needs-triage`.
- From `needs-triage`, an issue moves to one of the four terminal-or-staged
  states.
- `needs-info` returns to `needs-triage` once the reporter replies.
- The maintainer can override any transition. Unusual transitions `SHALL`
  be flagged before applying.

## Vertical-slice breakdown

When a plan, spec, or PRD is broken into issues, each issue is a **tracer
bullet**: a thin slice that cuts through *every* integration layer
end-to-end (schema, API, UI, tests). Slices are not horizontal — "all the
schema work in one issue" is the wrong shape.

Rules:

- Each slice delivers a narrow but complete path through every layer.
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.
- Each slice is classified as **HITL** (human-in-the-loop, requires
  judgment such as architectural review) or **AFK** (away-from-keyboard,
  fully specified, an agent can complete it without human context). Prefer
  AFK where possible.
- Track `blocked-by` relationships explicitly between slices.

Slices enter the tracker with the `needs-triage` state label and proceed
through the standard state machine.

## Issue artifacts

### Issue body template

Used by `/to-issues` when publishing a new slice to the tracker:

```markdown
## Parent

[Reference to parent issue if this is part of a larger breakdown; omit otherwise.]

## What to build

A concise description of this vertical slice. Describe end-to-end
behavior, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

## Blocked by

- [Reference to blocking issue, or "None — can start immediately".]
```

The parent issue (if any) `SHALL NOT` be modified or closed when child
slices are published.

### Agent brief template

Posted as a comment when an issue moves to `ready-for-agent` or
`ready-for-human`. It is the authoritative specification an agent (or
human) implements against. The agent brief, not the original issue
discussion, is the contract.

Principles:

- **Durability over precision.** Describe interfaces, types, and
  behavioral contracts. Avoid file paths and line numbers — they go
  stale while the issue waits.
- **Behavioral, not procedural.** Say *what* the system should do, not
  *how* to implement it. The implementer explores fresh and decides
  the structure.
- **Complete acceptance criteria.** Each criterion is independently
  verifiable.
- **Explicit scope boundaries.** State what is out of scope to prevent
  gold-plating.

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** one-line description of what needs to happen

**Current behavior:**
What happens now. For bugs, the broken behavior. For enhancements, the
status quo this builds on.

**Desired behavior:**
What should happen after the work is complete. Be specific about edge
cases and error conditions.

**Key interfaces:**
- `TypeName` — what needs to change and why
- `functionName()` — current vs expected behavior
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Adjacent thing that should NOT be changed
```

A `ready-for-human` brief follows the same structure but adds a note
explaining why the work cannot be delegated to an AFK agent.

## .out-of-scope/ knowledge base

When an `enhancement` is rejected as `wontfix`, the decision `SHOULD` be
persisted to a per-concept file under `.out-of-scope/` in the repo. This
serves two purposes:

1. **Institutional memory.** The reasoning is preserved after the issue
   is closed.
2. **Deduplication.** Future similar requests can be matched against
   prior rejections instead of re-litigating them.

One file per concept, kebab-case (e.g. `dark-mode.md`, `plugin-system.md`).
Multiple issues requesting the same concept are grouped under one file.
Bug rejections do not go to `.out-of-scope/`; only enhancement rejections.

The file `SHOULD` capture the concept name, why it's out of scope (project
scope, technical constraint, strategic decision — not "we're too busy",
which is a deferral, not a rejection), and a list of prior issue
references.

When a rejected concept is reconsidered, the file is deleted. Old issues
are not reopened — the new issue triggering reconsideration proceeds
through normal triage.

## Per-repo configuration

`/setup-matt-pocock-skills` generates the configuration that `/triage`,
`/to-issues`, and other agent skills read at runtime:

| Artifact | Contents |
|---|---|
| `## Agent skills` block in `CLAUDE.md` | Pointers to the three docs/agents/ files below |
| `docs/agents/issue-tracker.md` | Where issues live (GitHub by default) and the CLI commands the skills use |
| `docs/agents/triage-labels.md` | Canonical-to-local label mapping |
| `docs/agents/domain.md` | Single-context vs multi-context layout, and the consumer rules for `CONTEXT.md` and `docs/adr/` |

Defaults:

- **Issue tracker:** GitHub Issues via the `gh` CLI.
- **Triage labels:** the canonical names above (no remapping).
- **Domain layout:** single-context (`CONTEXT.md` at repo root).

Repos `MAY` deviate from any default by editing the generated
`docs/agents/*.md` after running `/setup-matt-pocock-skills`. Editing the
generated files is the supported customisation path; the skills read from
those files, not from this standard.

## What this standard does not cover

| Concern | Where it lives |
|---|---|
| Strategic goals, aspirations | `ROADMAP.md` |
| Business problem and stakeholders | `BUSINESS_CONTEXT.md` |
| Domain glossary (terms, relationships) | `CONTEXT.md` |
| Formal requirements with traceability | `specs/` (see [SDD standards](~/workspace/dev-playbook/sdd-standards/README.md)) |
| File hierarchy and ADR conventions | [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md) |
| Testing rules | [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) |
