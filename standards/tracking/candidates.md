---
type: Standard
title: Candidates
description: The register of a repo's uncommitted future work — one CANDIDATES.md at the root, the entry shape, and the headings and nesting
population: "a repo's CANDIDATES.md"
---

# Candidates

A repo's `CANDIDATES.md`, the register of the future work it has not
committed to: a **Candidate** is work described but not yet decided, and
committed work is a GitHub issue
([Issue Shapes](/standards/tracking/issue-shapes.md)). The file is
optional, one per repo, at the root
([One at the root, or none](/standards/build/skeleton.md#one-at-the-root-or-none)), typed
`Candidate-List`
([Document Types](/standards/knowledge-organization/document-types.md));
its absence means nothing has been recorded yet.

> **Why.** Commitment is a decision, not a capability: an entry may be
> perfectly specifiable and stay a Candidate for as long as nobody has
> chosen to build it, and deciding to write its brief is what ends
> that.

## One list item per entry

Every list item in `CANDIDATES.md`, nested or not, starts
`**<name>** — `.

```markdown
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.
```

`tracking.one-list-item-per-entry` · deterministic

> **Why.** An approach decided this early goes stale before the work
> starts, and brief furniture — fields, acceptance criteria,
> checkboxes — is the signal that the brief could be written, and
> therefore that the work belongs in an issue.

## Every entry under a heading

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

`tracking.every-entry-under-a-heading` · stochastic

> **Why.** Neither the order of the headings nor the order of the
> entries carries meaning, so every merge conflict in this file
> resolves by keeping both sides.
