---
type: Standard
title: Issue Authoring
description: How a GitHub issue is authored — epic and leaf roles, readiness, the three brief formats, vertical slices, and native relationships
---

# Issue Authoring

How GitHub Issues are authored in workspace repos. An issue plays one of two
**roles** and, as a leaf, moves through a **readiness** lifecycle; its body is
the agent **brief**, in one of three formats. Applies at intake — when an idea,
or a rushed stub, becomes one or many tracked issues. Driving the tracker
itself — the commands that create, link, and close issues — is
[tracker-operations.md](/standards/tracking/tracker-operations.md).

An issue is **committed work**, at any size — an epic, an ordinary issue, or a
one-line bug. Work not yet decided on is a Candidate in `CANDIDATES.md`
([candidates.md](/standards/tracking/candidates.md)), and the two are
exclusive: a unit of work sits in one home, never both. Deciding to write the
brief below is the act of committing, so a specifiable idea nobody has chosen
to build stays a Candidate — and promoting it deletes its entry as the issue is
authored.

## Roles: epic and leaf

Every issue carrying build work through the software factory is exactly one of
two roles. The role is **derived**, never a label — the same principle as
*blocked* (a derived dependency state, never minted as a label).

- **Leaf** — the unit of work. A leaf is dispatched through the
  [software factory graph](/software-factory/software-factory.md) and carries the full four-tuple
  `(category:*, mode:*, tests:*, phase:*)`. Its body is a build-leaf brief or a
  spike brief (below).
- **Epic** — an issue decomposed into sub-issues. An epic is **never built
  directly**: no branch, no PR, no dispatch. It carries a **category label
  only** — no phase, mode, or tests label — and its epic role is derived purely
  from having sub-issues, so there is no `epic` label to mint. Its body is the
  epic body (below): the outcome and the decomposition rationale, never a
  restatement of the native sub-issue list GitHub already shows.

**A design session produces an epic.** The common way an epic is born is the
`design` node concluding the work is too big for one leaf: the session
decomposes it in place, turning the issue into an epic and minting its children
as ready leaves (see [software-factory.md's decompose exit](/software-factory/software-factory.md)).

### Two species of epic

The two roles are the whole model for factory-tracked build work, but an epic
comes in two species, told apart by what its children are *for*:

- **Build epic** — children are build leaves, each a vertical slice of the
  outcome. This is the default species, and the one the epic body below
  describes.
- **Wayfinder map** — a **planning** epic whose children are decision tickets:
  research, prototype, grilling, and task tickets that resolve open questions
  rather than ship slices. A map is driven by the `/wayfinder` skill, which owns
  its body shape, its labels, and its working loop; the skill is the definition,
  and this standard restates none of it. Its tracker moves are in
  [tracker-operations.md](/standards/tracking/tracker-operations.md).

A decision ticket is **not a factory leaf** and carries none of a leaf's
obligations: no four-tuple labels, no dispatch through the software factory
graph, no build-leaf or spike brief. What a ticket does carry is the
`/wayfinder` skill's to define.

## Readiness

Readiness is a **lifecycle position, not a kind of issue** — the industry's
*Definition of Ready*. Work is dispatched into an implementation node only on a
leaf whose body meets the brief standard below; an under-specified leaf is not
yet ready. The refinement interview — intake, or the `design` node — is the
**refinement step** that carries a leaf to ready by authoring its brief. A
leaf's role never changes as it readies; only its body and phase advance.
(**Promotion** is a different move, reserved for Candidate → issue.)

## The body is the brief

The issue body IS the agent brief. There are **three brief formats**, one per
role-and-mode. Each format's required headings are stated explicitly below, and
are exactly the lists the [`tracking.issue-brief-shape` audit](/scripts/workspace-lint)
checks on live leaves — so this document and the rule cannot disagree.

Dependencies and hierarchy are **not** body fields — they are native GitHub
relationships; see [Relationships](#relationships).

### The build-leaf brief (`mode:sdd`, `mode:direct`)

A build leaf carries **all six** headings — none optional. `Key interfaces`
states "none" when there are none, rather than being omitted.

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

A brief reporting broken behavior may add a `Steps to reproduce` heading; it is
optional, unenforced, and changes none of the six.

### The spike brief (`mode:spike`)

A spike is a **question** whose deliverable is an **answer**, not
merged code — the findings land in the issue's closing comment, and no PR opens
(see [software-factory.md's spike path](/software-factory/software-factory.md)). The spike brief carries
these headings:

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question the spike answers — narrow enough to resolve in one focused investigation.

**Deliverable:**
What a good answer looks like. The answer itself lands in the closing comment
(plus a Decision Record if a one-way door was crossed).
```

### The epic body

An epic's body is not a brief for work — nothing dispatches on it. It states the
**outcome** and the **decomposition rationale**, and never duplicates the native
sub-issue list.

```markdown
**Outcome:**
The end state once every child has merged.

**Decomposition rationale:**
Why the work was sliced this way — the ordering constraints and shared surfaces
that shaped the slices.
```

#### Optional sections

A long-running epic accumulates two things the required sections have no home
for: a boundary that keeps getting re-asked, and a ruling made after the
decomposition that binds more than one child. Each gets an **optional** section,
added when — and only when — the epic actually accrues one. A fresh epic carries
neither, and most never grow them; an empty heading is boilerplate, not
structure.

```markdown
**Out of scope:**
- What this epic will not do, and why. Link the child, where one was closed as mis-scoped.

**Standing rulings:**
1. The ruling in one line, stated as the constraint it puts on children.
```

**Out of scope** is the epic's scope boundary: work consciously ruled outside
the outcome, which will never become a child and does not come back as the epic
progresses. A boundary earns a line exactly when a reader could reasonably have
assumed the opposite. Work that is inside the outcome but not yet sliced is a
different thing — a child not created yet, and the decomposition rationale's
business. So is a leaf's `Out of scope` heading, which rules out gold-plating
*within* one slice, usually deferring it to a sibling; an epic rules out work no
sibling will ever pick up.

**Standing rulings** holds the rulings that still point **forward** — decisions
taken after the epic was written that constrain children not yet built. A ruling
earns its place by governing unbuilt work, which is what makes this neither an
index of closed children nor a changelog of every decision the epic ever took. A
numbered list, appended to and never renumbered, since the number is how a child
issue or a later session cites a ruling. A decision binding exactly one child
belongs in that child's brief instead, and a hard-to-reverse decision meeting the
Decision Record bar gets a record under `docs/decisions/`
([records.md](/standards/decisions/records.md)) that outlives the epic.

## Brief principles

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. File paths and line numbers go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

**The prototype snippet is the exception.** A brief may carry a concrete,
verbatim snippet produced by a prototype session — the answer that prototype was
built to yield, written to lift into real code unchanged. Durability is not at
risk, because the snippet is the durable artifact: it is what survived the
prototype, and the issue exists to spend it. Nor is it procedural, because it
states the settled shape rather than the steps to reach it. The test is
provenance — a snippet a prototype answered for, not an implementation the brief
guessed at on the author's behalf.

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
- **Hierarchy — sub-issues.** The "part of" relationship: a parent issue and its children. Use it to group the slices of a large feature under a tracking **epic** — which is exactly what derives the epic role (see [Roles](#roles-epic-and-leaf)). Decomposition only — it implies no ordering, and a sub-issue is not blocked by its siblings unless a blocked-by edge says so.

Example — epic "User CSV export" (#10) sliced into schema (#11), API (#12), UI (#13), docs (#14):

- Hierarchy: #11–#14 are sub-issues of #10.
- Dependency: #12 blocked-by #11; #13 blocked-by #12; #11 and #14 blocked by nothing.

The two graphs need not align: #14 is a sibling of #12 with no dependency between them, and a blocker can cross epics (#12 could be blocked-by an issue under a different parent).
