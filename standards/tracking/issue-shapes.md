---
type: Standard
title: Issue Shapes
description: The five species of GitHub issue and the shape of each — its labels and its body headings — the build leaf, the spike, the session leaf, the epic, and the wayfinder map or ticket, plus the rules every body obeys
population: "a GitHub issue in a governed repo"
---

# Issue Shapes

A GitHub issue in a governed repo is committed work, at any size. Work
not yet decided on is a Candidate in `CANDIDATES.md`
([Candidates](/standards/tracking/candidates.md)), and a unit of
work sits in one home, never both. An issue is one of five species, told from
its labels and its sub-issues, and each species fixes the labels the
issue carries and the headings its body carries. The labels are
[Label Scheme](/standards/tracking/label-scheme.md)'s; the calls that
link issues are [Linking Issues](/guides/linking-issues.md).

## Written for the user

An issue's body is readable unaided by a user who sees only the issue and
never the author's context, and a reference to existing file content
quotes verbatim the text it amends.

`tracking.written-for-the-user` · stochastic

## Behavioural, not procedural

The body of an issue that carries `mode:direct` or `mode:session`
describes what the system does after the work, as interfaces and
behavioural contracts, never the steps that get there.

`tracking.behavioural-not-procedural` · stochastic

## One goal

An issue that carries `mode:direct` or `mode:session` serves one
outcome, and every part that could slip indefinitely
with the outcome still standing, and could ship later as its own issue
without reopening this one, is named under the issue's `Out of scope`
heading and carried by a separate issue that carries `phase:intake`.

`tracking.one-goal` · stochastic

## User intent

Where an issue's body carries a `User intent` heading, what stands under
it is the user's own words for this issue, never an agent's paraphrase.

`tracking.user-intent` · stochastic

> **Why.** The defect the rule catches is one epic-level block of
> intent copied into every child: the words are the user's, but they
> are not this issue's.

## Closed fences

A leaf that carries `mode:session`, or a leaf that carries a `phase:*`
label other than `phase:intake`, closes every code fence its body opens.

`tracking.closed-fences` · deterministic

## Build leaf

The issue has no sub-issues and carries `mode:direct`.

`tracking.build-leaf` · deterministic

### Build labels

A build leaf that carries a `phase:*` label other than `phase:intake`
carries exactly one label from each of `category`, `mode`, `tests`, and
`phase`, and each of those labels is a value of the label scheme.

`tracking.build-labels` · deterministic

### Build headings

A build leaf that carries a `phase:*` label other than `phase:intake`
carries every heading below in its body, each as a bold heading; a
heading shown inside a code fence is quoted, not carried.

```markdown
**Summary:** one line

**User intent:**
Why the issue exists and which way to lean when goods collide.

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

`tracking.build-headings` · deterministic

### Prohibited surfaces

A build leaf's `Prohibited surfaces` names only the paths whose touching
is a real hazard.

`tracking.prohibited-surfaces` · stochastic

### Artifacts

Where a build leaf's body carries an `Artifacts` section, each block
under it sits in a code fence, four backticks when the block has fences
of its own.

`tracking.artifacts` · deterministic

## Spike

The issue has no sub-issues and carries `mode:spike`.

`tracking.spike` · deterministic

### Spike labels

A spike that carries a `phase:*` label other than `phase:intake` carries
exactly one label from each of `category`, `mode`, `tests`, and `phase`,
each of those labels is a value of the label scheme, and its `tests:*`
label is `tests:no`.

`tracking.spike-labels` · deterministic

### Spike headings

A spike that carries a `phase:*` label other than `phase:intake` carries
`Summary`, `Question`, and `Deliverable` in its body, each as a bold
heading; a heading shown inside a code fence is quoted, not carried.

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question, narrow enough to resolve in one investigation.

**Deliverable:**
What a good answer looks like.
```

`tracking.spike-headings` · deterministic

## Session leaf

The issue has no sub-issues and carries `mode:session`.

`tracking.session-leaf` · deterministic

### Session labels

A session leaf carries exactly one `category:*` label, a value of the
label scheme, and carries no `mode:*` label other than `mode:session`, no
`tests:*` label, and no `phase:*` label.

`tracking.session-labels` · deterministic

### Session headings

A session leaf carries `Summary`, `User intent`, `Current behavior`,
`Desired behavior`, `Acceptance criteria`, and `Out of scope` in its
body, each as a bold heading; a heading shown inside a code fence is
quoted, not carried. Its `Out of scope` may read
`Unknown; dealt with when found.`

`tracking.session-headings` · deterministic

### A stable body

A session leaf's body holds no worklist, no open question, and no running
decision.

`tracking.a-stable-body` · stochastic

> **Why.** The plan, the open questions, and the decisions of the work
> live in a
> [working documentation set](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
> on the branch, so the body has nothing to accrue.

## Epic

The issue has sub-issues and carries no `wayfinder:*` label.

`tracking.epic` · deterministic

### Category only

An epic carries exactly one `category:*` label, a value of the label
scheme, and carries no `phase:*`, `mode:*`, or `tests:*` label.

`tracking.category-only` · deterministic

### Epic headings

An epic carries `Outcome` and `Decomposition rationale` in its body, each
as a bold heading.

```markdown
**Outcome:**
The end state once every child has merged.

**Decomposition rationale:**
Why the work was sliced this way.
```

`tracking.epic-headings` · deterministic

### No child list

An epic's body does not list its sub-issues.

`tracking.no-child-list` · stochastic

### Standing rulings

Where an epic's body carries a `Standing rulings` heading, the rulings
under it are a numbered list.

`tracking.standing-rulings` · deterministic

## Wayfinder map or ticket

The issue carries a `wayfinder:*` label: `wayfinder:map` makes it a
**map**, and any other `wayfinder:*` value makes it a **decision
ticket**.

`tracking.wayfinder-map-or-ticket` · deterministic

### Wayfinder labels

A map carries `wayfinder:map` and no other `wayfinder:*` value; a
decision ticket carries exactly one `wayfinder:*` value, a value of the
label scheme; and neither carries a `category:*`, `mode:*`, `tests:*`, or
`phase:*` label.

`tracking.wayfinder-labels` · deterministic

### Wayfinder body

A map's body carries a `Destination`, a `Notes`, a `Decisions so far`, a
`Not yet specified`, and an `Out of scope` section, and a decision
ticket's body carries a `Question` section, each as a markdown heading at
any level.

`tracking.wayfinder-body` · deterministic

> **Why.** The `/wayfinder` skill owns these body shapes; the rule
> mirrors them, so a change to the shapes the skill drives is what
> changes the rule.

### Ticket parentage

A decision ticket is a sub-issue of a map.

`tracking.ticket-parentage` · deterministic
