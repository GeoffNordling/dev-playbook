---
type: Standard
title: Candidates
description: The CANDIDATES.md register of uncommitted future work — the only future-work file, entry shape, structure, and promotion to an issue
population: "a repo's CANDIDATES.md"
---

# Candidates

A repo's `CANDIDATES.md`, the register of the future work it has not
committed to. Committed work lives in GitHub issues
([Issue Authoring](/standards/tracking/issue-authoring.md)); a
**Candidate** is work described but not yet decided, and a unit of work
has exactly one home. The file is optional, one per repo, at the root
([File Skeleton](/standards/build/skeleton.md#root-only-files)); its
absence means nothing has been recorded yet. It carries `Candidate-List`
frontmatter and an index entry like any concept document
([Document Types](/standards/knowledge-organization/document-types.md)).

## Uncommitted work

Every entry is work this repo would implement once the decision is made,
and that decision has not been made. Commitment is a decision, not a
capability: an entry may be perfectly specifiable and stay a Candidate for
as long as nobody has chosen to build it, and deciding to write its brief
is what ends that. The author makes this call; no detector checks it.

A Candidate is serious and repo-scoped: not the unfiltered, cross-repo
ideas that belong in mission-control's capture path, and never material
that is not work at all. Once committed, the work belongs in an issue at
whatever size fits — an epic, an ordinary issue, or a one-line bug.

## The only future-work file

No `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or `IDEAS.md` exists anywhere in
the tree; `CANDIDATES.md` is the one future-work file a repo carries.
repo-lint reports a rogue file (`tracking.rogue-future-work-file`).

## Entry shape

An entry is one list item — a bolded short name, an em dash, then one or
two sentences of intent — and carries no fields, no acceptance criteria,
and no checkboxes.

```markdown
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.
```

The bolded name is the entry's handle: what promotion is pointed at, and
what gets deleted when it lands. The prose says what the work is, never
how to do it, since an approach decided this early goes stale before the
work starts. Brief furniture on a Candidate is the signal that the brief
could be written, and therefore that the work belongs in an issue.

## Structure

A `##` heading groups entries and carries no other meaning; nesting
decomposes, a parent being an outcome and its children the work that
achieves it, to any depth; and order carries no meaning in either
dimension.

Headings are navigational only, free to invent. Since order is
meaningless, every merge conflict in this file resolves by keeping both
sides. A register in full:

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

An entry whose issue has been authored is deleted in the same change, so
the work never sits in both homes; a parent promotes with its whole
subtree as one issue, never as an issue per child.

Intake does not slice, so the subtree's decomposition is deferred to the
`design` node like any other multi-issue plan
([Issue Authoring](/standards/tracking/issue-authoring.md)). Deleting an
entry without promoting it is ordinary editing: a Candidate that no longer
appeals is removed, and nothing records that it was once considered.
