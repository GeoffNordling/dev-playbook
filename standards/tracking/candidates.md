---
type: Standard
title: Candidate Conventions
description: The CANDIDATES.md register of uncommitted future work — entry shape, grouping and nesting, and promotion to an issue
---

# Candidate Conventions

A repo records the future work it has not committed to in one root file,
`CANDIDATES.md`. Committed work lives in GitHub issues
([issue-authoring.md](/standards/tracking/issue-authoring.md)); a **Candidate**
is work described but not yet decided. A unit of work has exactly one home —
never both.

## The commitment test

Commitment is a decision, not a capability. Deciding to state the current
behavior, desired behavior, and testable acceptance criteria is the act of
committing, and the work then belongs in an issue at whatever size fits — an
epic, an ordinary issue, or a one-line bug.

So a Candidate is not merely work too vague to specify. An entry may be
perfectly specifiable and stay a Candidate for as long as the decision to build
it has not been made; writing its brief is what ends that.

The author makes this call. No detector checks it.

## What a Candidate is

A Candidate is serious and repo-scoped: work this repo would genuinely
implement if the decision were made. It is not a passing thought — unfiltered
and cross-repo ideas belong in mission-control's capture path instead. A
Candidate is also work: material that is not work at all has no entry here.

## Presence

`CANDIDATES.md` is optional, one per repo, at the repo root. Its absence means
nothing has been recorded yet, per the presence-is-the-status-signal rule in
[skeleton.md](/standards/build/skeleton.md). It is the only future-work file a
repo carries: `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, and `IDEAS.md` are
forbidden anywhere in the tree.

## Entry shape

An entry is one list item — a bolded short name, an em dash, then one or two
sentences of intent:

```markdown
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.
```

The bolded name is the entry's handle: what promotion is pointed at, and what
gets deleted when it lands. The prose says what the work is, never how to do
it, since an approach decided this early goes stale before the work starts.

Entries carry no fields, no acceptance criteria, and no checkboxes. Brief
furniture on a Candidate is the signal that the brief could be written, and
therefore that the work belongs in an issue.

## Structure

Two kinds of structure, with distinct meanings:

- **`##` headings group.** Navigational only, free to invent, no semantics.
- **Nesting decomposes.** A parent is an outcome; its children are the work
  that achieves it. Depth is unbounded.

Order carries no meaning in either dimension, so every merge conflict in this
file resolves by keeping both sides.

## Example

```markdown
---
type: Candidate-List
title: Candidates
description: Uncommitted future work — described, not yet promoted to issues
---

# Candidates

## Export

- **Scheduled exports** — a user picks a cadence and the report reaches their
  inbox without them opening the app.
  - **Cadence picker** — daily, weekly, or monthly, with the timezone taken
    from the user's profile.
  - **Delivery retry** — a bounced send is retried before the run is marked
    failed.
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.

## Search

- **Fuzzy matching** — matching is exact-prefix only, so a typo returns
  nothing.
```

## Promotion

Promotion turns a Candidate into committed work: an issue is authored from the
entry, and the entry is deleted in the same change, so the work never sits in
both homes.

Promoting a parent promotes its subtree as **one** issue, not as an issue per
child: intake does not slice, so the subtree's decomposition is deferred to the
`design` node like any other multi-issue plan
([issue-authoring.md](/standards/tracking/issue-authoring.md)).

Deleting an entry without promoting it is ordinary editing. A Candidate that no
longer appeals is removed, and nothing records that it was once considered.
