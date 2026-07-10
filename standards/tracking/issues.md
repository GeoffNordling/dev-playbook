---
type: Standard
title: Issue Conventions
description: GitHub issue body format — the body as agent brief, vertical-slice decomposition, blocked-by and sub-issue relationships
---

# Issue Conventions

How GitHub Issues are authored in workspace repos. Applies at intake — when
an idea, or a rushed stub, becomes one or many ready, tracked issues.

## The body is the brief

The issue body IS the agent brief. Use this format:

```markdown
**Summary:** one-line description

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate
```

Dependencies and hierarchy are **not** body fields — they are native GitHub relationships; see [Relationships](#relationships).

## Brief principles

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. File paths and line numbers go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

## Vertical-slice rules

When one idea becomes many issues, break the plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, not a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.
- **Size to the context budget.** Slice thin enough that building one issue keeps the agent well under ~30% of its context window. Split anything bigger.

Create slices in dependency order, then wire the native relationships (see [Relationships](#relationships)): mark each ordered slice **blocked-by** its predecessor. Creating in order means the blocker exists before the dependent links to it.

## Relationships

Two independent relationships connect issues. Both are **native GitHub relationships** — not body fields, not labels — set at intake. They are orthogonal: a parent says nothing about order, and a blocker says nothing about parentage.

- **Dependency — blocked-by.** The "must finish first" relationship, and the workhorse for sequencing slices. An issue is *blocked* while any issue it is blocked-by is still open, and *ready* once they all close. Blocked is a derived state, never a label — don't mint one.
- **Hierarchy — sub-issues.** The "part of" relationship: a parent issue and its children. Use it to group the slices of a large feature under a tracking **epic**. Decomposition only — it implies no ordering, and a sub-issue is not blocked by its siblings unless a blocked-by edge says so.

Example — epic "User CSV export" (#10) sliced into schema (#11), API (#12), UI (#13), docs (#14):

- Hierarchy: #11–#14 are sub-issues of #10.
- Dependency: #12 blocked-by #11; #13 blocked-by #12; #11 and #14 blocked by nothing.

The two graphs need not align: #14 is a sibling of #12 with no dependency between them, and a blocker can cross epics (#12 could be blocked-by an issue under a different parent).
