---
type: Standard
title: Candidates
description: The register of a repo's uncommitted future work — one CANDIDATES.md at the root, one home per unit of work, the entry shape, and the headings and nesting
population: "a repo's CANDIDATES.md"
---

# Candidates

A repo's `CANDIDATES.md`, the register of the future work it has not
committed to: a **Candidate** is work described but not yet decided, and
committed work is a GitHub issue
([Issue Shapes](/standards/tracking/issue-shapes.md)). The file is
optional, one per repo, at the root
([Root-only files](/standards/build/skeleton.md#root-only-files)), typed
`Candidate-List`
([Document Types](/standards/knowledge-organization/document-types.md));
its absence means nothing has been recorded yet.

The reasoning behind the rules is the
[Tracking Explanation](/standards/tracking/explanation.md#candidates).

## One home

A unit of work is a Candidate or an issue, never both.

`tracking.one-home` · stochastic

## Entry shape

An entry is one list item: a bolded short name, an em dash, then one or
two sentences of intent, with no fields, no acceptance criteria, and no
checkboxes.

```markdown
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.
```

`tracking.entry-shape` · deterministic

## Structure

Every entry sits under a `##` heading, directly or nested under a parent
entry; a heading groups its entries and carries no other meaning, and a
nested entry is work that achieves its parent's outcome.

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

`tracking.structure` · stochastic
