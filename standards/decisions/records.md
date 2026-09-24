---
type: Standard
title: Decision Record Conventions
description: How a Decision Record is written, from the bar that warrants one and the directory that holds it to its template, date, numbering, status vocabulary, and the pin on an external-convention evaluation
population: "a Decision Record: a numbered NNNN-slug.md file under a repo's docs/decisions/, except that directory's index.md and README.md"
---

# Decision Record Conventions

A Decision Record is a numbered `NNNN-slug.md` file under a repo's
`docs/decisions/`. Two files share that directory and are excluded.
`index.md` is the record listing, one line per record carrying the
record's `description`, and follows the
[Indexes](/standards/knowledge-organization/indexes.md) rules.
`README.md` is a short narrative orientation for the directory.

> An **ADR** (Architecture Decision Record) is the industry term for the
> architectural subset of this kind. A Decision Record generalizes the
> same artifact past architecture to any hard-to-reverse decision.

## Hard to reverse, surprising, a real trade-off

A Decision Record records a decision that is hard to reverse, surprising
without its context, and the outcome of a real trade-off, all three at
once: changing course later carries meaningful cost, a future reader
looking at the code would wonder why it was done this way, and there
were genuine alternatives with a specific reason for the choice.

`decisions.hard-to-reverse-surprising-a-real-trade-off` · stochastic

> **Why.** Each criterion alone leaves nothing worth writing down: an
> easy-to-reverse decision is reversed, an unsurprising one raises no
> question, and one with no real alternative records the obvious. A
> record earns its place by stopping the next engineer from undoing a
> deliberate choice or re-proposing a rejected one.

## Numbered records, index, README, nothing else

When `docs/decisions/` has a record, it also has `index.md` and
`README.md`, and every other entry in it is a file named
`<digits>-<slug>.md`. It has no other file and no subdirectory.

`decisions.numbered-records-index-readme-nothing-else` · deterministic

## Four digits from 0001, no gaps or repeats

A record's filename is `NNNN-slug.md`, where `NNNN` is its number
in exactly four digits. Sorted, the numbers in `docs/decisions/`
are `0001`, `0002`, and on up by one to the highest, each once.

`decisions.four-digits-from-0001-no-gaps-or-repeats` · deterministic

## Four frontmatter keys, title repeated as H1

A record's frontmatter has `type: Decision-Record` and the keys
`title`, `description`, and `date`. The first non-blank line after
the frontmatter is `# ` followed by the `title` value exactly.

```md
---
type: Decision-Record
title: {Short title of the decision}
description: {One-line summary of the decision, for triage and the index}
date: {YYYY-MM-DD}
---

# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

`decisions.four-frontmatter-keys-title-repeated-as-h1` · deterministic

## Context, decision, and reason

A Decision Record's body gives the context the decision was made in,
the decision itself, and the reason for it.

`decisions.context-decision-and-reason` · stochastic

## YYYY-MM-DD date or null

A record's `date` is a `YYYY-MM-DD` date or `null`.

`decisions.yyyy-mm-dd-date-or-null` · deterministic

> **Why.** The date is the day the decision was made, not the writing
> day, and null where that day is unrecoverable.

## Proposed, accepted, deprecated, superseded, or absent

A record's `status`, if it has one, is `proposed`, `accepted`,
`deprecated`, or `superseded by NNNN` with `NNNN` four digits.

`decisions.proposed-accepted-deprecated-superseded-or-absent` · deterministic

## Superseded by a record that exists

If a record's `status` is `superseded by NNNN`, `docs/decisions/`
has a record whose filename starts `NNNN-`.

`decisions.superseded-by-a-record-that-exists` · deterministic

## External-convention evaluation

A Decision Record's decision is a verdict on something outside the
workspace: a skill, a skill collection, a framework, or a technique.

### Source named, SHA or version pinned

A Decision Record whose decision is a verdict on something outside the
workspace names the source and pins at least one of the repository SHA
and the release or version examined.

`decisions.source-named-sha-or-version-pinned` · stochastic

> **Why.** A verdict on something outside the workspace ages with its
> subject, so the pin is what lets a later reader tell whether the
> verdict holds against the version in front of them.
