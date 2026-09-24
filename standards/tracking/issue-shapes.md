---
type: Standard
title: Issue Shapes
description: The five species of GitHub issue and the shape of each — its labels and its body headings — the build leaf, the spike, the session leaf, the epic, and the wayfinder map or ticket, plus the rules every body obeys
population: "a GitHub issue in a governed repo"
---

# Issue Shapes

A GitHub issue in a governed repo is committed work, at any size. Work
not yet decided on is a Candidate in `CANDIDATES.md`
([Candidates](/standards/tracking/candidates.md)). An issue is one of
five species, told from
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

## User intent in the user's voice

An issue's `User intent` section is written in the user's voice, not an
agent's paraphrase.

`tracking.user-intent-in-the-users-voice` · stochastic

> **Why.** Only the user can vouch for what they meant. A paraphrase
> is an agent's reading of the intent, and the reading is what drifts,
> so the section keeps the user's words and the agent's reading goes
> elsewhere in the issue.

## Closed fences

The body of a leaf that has `mode:session`, or that has a `phase:*`
label other than `phase:intake`, closes every code fence it opens.

`tracking.closed-fences` · deterministic

## Build leaf

The issue has no sub-issues and has `mode:direct`.

### One label from each prefix

A build leaf with a `phase:*` label other than `phase:intake` has
exactly one `category:*`, one `mode:*`, one `tests:*`, and one
`phase:*` label, and each of the four is a label in
`src/dev_playbook/label_scheme.json`.

`tracking.one-label-from-each-prefix` · deterministic

### Every build heading, in bold

The body of a build leaf with a `phase:*` label other than
`phase:intake` has each of the eight headings below as bold text
followed by a colon, `**Summary:**` or `**Summary**:`, outside any
code fence.

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

`tracking.every-build-heading-in-bold` · deterministic

### Every artifact block in a fence

Where a build leaf's body carries an `Artifacts` section, each block
under it sits in a code fence, four backticks when the block has fences
of its own.

`tracking.every-artifact-block-in-a-fence` · stochastic

## Spike

The issue has no sub-issues and has `mode:spike`.

### One label from each prefix, tests fixed at no

A spike with a `phase:*` label other than `phase:intake` has
exactly one `category:*`, one `mode:*`, one `tests:*`, and one
`phase:*` label, each a label in
`src/dev_playbook/label_scheme.json`, and its `tests:*` label is
`tests:no`.

`tracking.one-label-from-each-prefix-tests-fixed-at-no` · deterministic

### Summary, Question, and Deliverable

The body of a spike with a `phase:*` label other than
`phase:intake` has `Summary`, `Question`, and `Deliverable` as bold
text followed by a colon, outside any code fence.

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question, narrow enough to resolve in one investigation.

**Deliverable:**
What a good answer looks like.
```

`tracking.summary-question-and-deliverable` · deterministic

## Session leaf

The issue has no sub-issues and has `mode:session`.

### One category label, no phase or tests

A session leaf has exactly one `category:*` label, a label in
`src/dev_playbook/label_scheme.json`, no `mode:*` label other than
`mode:session`, and no `tests:*` or `phase:*` label.

`tracking.one-category-label-no-phase-or-tests` · deterministic

### Every session heading, in bold

The body of a session leaf has `Summary`, `User intent`,
`Current behavior`, `Desired behavior`, `Acceptance criteria`, and
`Out of scope` as bold text followed by a colon, outside any code
fence. `Out of scope` may read `Unknown; dealt with when found.`

`tracking.every-session-heading-in-bold` · deterministic

### A stable body

A session leaf's body holds no worklist, no open question, and no running
decision.

`tracking.a-stable-body` · stochastic

> **Why.** The plan, the open questions, and the decisions of the work
> live in a
> [workstream](/standards/knowledge-organization/documentation-sets/workstream-files.md)
> on the branch, so the body has nothing to accrue.

## Epic

The issue has sub-issues and has no `wayfinder:*` label.

### Category only

An epic has exactly one `category:*` label, a label in
`src/dev_playbook/label_scheme.json`, and no `phase:*`, `mode:*`, or
`tests:*` label.

`tracking.category-only` · deterministic

### No child list

An epic's body does not list its sub-issues.

`tracking.no-child-list` · stochastic

## Wayfinder map or ticket

The issue has a `wayfinder:*` label: `wayfinder:map` makes it a
**map**, and any other `wayfinder:*` value makes it a **decision
ticket**.

### One wayfinder label and nothing else

A map has `wayfinder:map` and no other `wayfinder:*` label. A
decision ticket has exactly one `wayfinder:*` label, a label in
`src/dev_playbook/label_scheme.json`. Neither has a `category:*`,
`mode:*`, `tests:*`, or `phase:*` label.

`tracking.one-wayfinder-label-and-nothing-else` · deterministic

### Map sections, ticket Question

A map's body has a markdown heading, at any level, for each of
`Destination`, `Notes`, `Decisions so far`, `Not yet specified`,
and `Out of scope`. A decision ticket's body has a markdown heading
`Question`, at any level.

`tracking.map-sections-ticket-question` · deterministic

> **Why.** The `/wayfinder` skill owns these body shapes; the rule
> mirrors them, so a change to the shapes the skill drives is what
> changes the rule.
