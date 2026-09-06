---
type: Standard
title: Issue Shapes
description: The five species of GitHub issue and the shape of each — its labels and its body headings — the build leaf, the spike, the session leaf, the epic, and the wayfinder map or ticket, plus the rules every body obeys
population: "a GitHub issue in a governed repo"
---

# Issue Shapes

A GitHub issue in a governed repo is committed work, at any size. Work
not yet decided on is a Candidate in `CANDIDATES.md`
([Candidates](/standards/tracking/candidates.md)), and a unit of work
sits in one home, never both. An issue is one of five species, told from
its labels and its sub-issues, and each species fixes the labels the
issue carries and the headings its body carries. The labels are
[Label Scheme](/standards/tracking/label-scheme.md)'s; the calls that
link issues are [Linking Issues](/standards/tracking/linking-issues.md).

## Roles

Every issue is a **leaf**, an issue with no sub-issues, or an **epic**,
an issue with sub-issues; the role is read from the tracker and is never
a label. An epic is never built directly: its children carry the work.

## Relationships

Hierarchy and dependency are native GitHub relationships, never body
fields and never labels: a **sub-issue** is part of its parent, and an
issue **blocked-by** another waits for it to close. The two are
independent, so a parent says nothing about order and a blocker nothing
about parentage, and *blocked* is derived from open blockers, never a
label.

## Written for the user

A brief is readable unaided by the user, who sees only the issue and
never the author's context: a reference to existing file content quotes
the text it amends verbatim.

## Behavioural, not procedural

A brief describes what the system does after the work, as interfaces and
behavioural contracts, never the steps that get there.

## One goal

A brief serves one outcome: any part that could slip indefinitely with
the outcome still standing, and could ship later as its own issue
without reopening this one, is deferred to a stub minted at
`phase:intake` and named under `Out of scope`.

## Build leaf

A leaf carrying `mode:direct`: the software factory's path, an issue
that ends in merged code.

### Build labels

A build leaf carries one label from each of `category`, `mode`, `tests`,
and `phase`, each a scheme value, `phase:*` naming its current node; an
untriaged leaf carries `phase:intake` or no labels at all. workspace-lint
reports a leaf past intake whose set is incomplete, doubled, or
off-scheme (`tracking.tuple-valid`).

### Build headings

The body carries every heading below, `Key interfaces` and `Prohibited
surfaces` stating "none" rather than being omitted; workspace-lint
reports a missing heading (`tracking.issue-brief-shape`).

```markdown
**Summary:** one line

**User intent:**
Why the issue exists and which way to lean when goods collide, in the
user's own words, written fresh for this issue.

**Current behavior:**
What happens now.

**Desired behavior:**
What happens after the work, including edge cases and error conditions.

**Key interfaces:**
- `Name` — what changes and why

**Acceptance criteria:**
- [ ] One independently verifiable criterion per line

**Prohibited surfaces:**
- `path/or/module` — why this issue must not touch it

**Out of scope:**
- What this issue will not change
```

`User intent` is the user's words and never an agent's paraphrase; one
epic-level block copied into every child is the defect. `Prohibited
surfaces` names only the paths whose touching is a real hazard. A brief
whose deliverables include prose may carry it verbatim in a
`## Artifacts` section, each block in a code fence, four backticks when
the content has fences of its own; the section binds when present and
is never required.

## Spike

A leaf carrying `mode:spike`: a question whose deliverable is an answer
in the issue's closing comment; no PR opens.

### Spike labels

A spike carries the build leaf's four labels, with `mode:spike` paired
with `tests:no` (`tracking.tuple-valid`).

### Spike headings

The body carries `Summary`, `Question`, and `Deliverable`
(`tracking.issue-brief-shape`):

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question, narrow enough to resolve in one investigation.

**Deliverable:**
What a good answer looks like.
```

## Session leaf

A leaf carrying `mode:session`: work the user leads in a session, in a
worktree, with a pull request opened by hand; nothing dispatches it.

### Session labels

A session leaf carries exactly one `category:*` label and
`mode:session`, and no `tests:*` or `phase:*` label; workspace-lint
reports the rest (`tracking.session-shape`).

### Session headings

The body carries `Summary`, `User intent`, `Current behavior`, `Desired
behavior`, `Acceptance criteria`, and `Out of scope`, as the build leaf
states them (`tracking.issue-brief-shape`); `Out of scope` may read
"Unknown; dealt with when found."

### A stable body

The body is written once and stays the brief: the plan, the open
questions, and the decisions of the work live in a working documentation
set on the branch
([Working Documentation Sets](/standards/knowledge-organization/working-documentation-sets.md)),
and a worklist, an open question, or a running decision in the body is
the defect.

## Epic

An issue with sub-issues and no `wayfinder:*` label.

### Category only

An epic carries exactly one `category:*` label, a scheme value, and no
`phase:*`, `mode:*`, or `tests:*` label; workspace-lint reports the rest
(`tracking.epic-shape`).

### Epic headings

The body carries `Outcome` and `Decomposition rationale` and never
duplicates the native sub-issue list; `Out of scope` and `Standing
rulings` are added only when the epic accrues one, and `Standing
rulings` is numbered and appended to, never renumbered.

```markdown
**Outcome:**
The end state once every child has merged.

**Decomposition rationale:**
Why the work was sliced this way.
```

## Wayfinder map or ticket

An issue carrying a `wayfinder:*` label: a **map**, the planning epic the
`/wayfinder` skill drives, or a **decision ticket**, one of its children.
The skill owns the body shapes and workspace-lint mirrors them; this
Standard restates none of it.

### Wayfinder labels

A map carries `wayfinder:map` and no ticket type; a ticket carries
exactly one `wayfinder:<type>`, a scheme value, and is a sub-issue of its
map; neither carries a `category:*`, `mode:*`, `tests:*`, or `phase:*`
label (`tracking.wayfinder-shape`).
