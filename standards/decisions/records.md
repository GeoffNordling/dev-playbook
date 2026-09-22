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

## The bar

A Decision Record records a decision that is hard to reverse, surprising
without its context, and the outcome of a real trade-off, all three at
once: changing course later carries meaningful cost, a future reader
looking at the code would wonder why it was done this way, and there
were genuine alternatives with a specific reason for the choice.

`decisions.the-bar` · stochastic

> **Why.** Each criterion alone leaves nothing worth writing down: an
> easy-to-reverse decision is reversed, an unsurprising one raises no
> question, and one with no real alternative records the obvious. A
> record earns its place by stopping the next engineer from undoing a
> deliberate choice or re-proposing a rejected one.

## The directory

The `docs/decisions/` directory holding a Decision Record holds numbered
records, one `index.md`, and one `README.md`, and nothing else.

`decisions.the-directory` · deterministic

## Sequential numbering

A Decision Record's filename is `NNNN-slug.md`, where `NNNN` is the
record's number zero-padded to four digits. The number is `0001` or
higher, no other record in the directory carries it, and every number
from `0001` up to the highest number in the directory belongs to a
record.

`decisions.sequential-numbering` · deterministic

## Template

A Decision Record's frontmatter holds `type: Decision-Record`, a
`title`, a `description`, and a `date`; its body opens with an H1
repeating the `title`.

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

`decisions.template` · deterministic

## Context, decision, and reason

A Decision Record's body gives the context the decision was made in,
the decision itself, and the reason for it.

`decisions.context-decision-and-reason` · stochastic

## Date

A Decision Record's `date` frontmatter key holds a `YYYY-MM-DD` date or
`null`

`decisions.date` · deterministic

> **Why.** The date is the day the decision was made, not the writing
> day, and null where that day is unrecoverable.

## Status vocabulary

A Decision Record either carries no `status` frontmatter key or carries
one holding exactly one of `proposed`, `accepted`, `deprecated`, or
`superseded by NNNN`, where `NNNN` is four digits.

`decisions.status-vocabulary` · deterministic

## Supersession target

A Decision Record whose `status` is `superseded by NNNN` sits in a
directory that holds a record numbered `NNNN`.

`decisions.supersession-target` · deterministic

## External-convention evaluation

A Decision Record's decision is a verdict on something outside the
workspace: a skill, a skill collection, a framework, or a technique.

### What was examined

A Decision Record whose decision is a verdict on something outside the
workspace names the source and pins at least one of the repository SHA
and the release or version examined.

`decisions.what-was-examined` · stochastic

> **Why.** A verdict on something outside the workspace ages with its
> subject, so the pin is what lets a later reader tell whether the
> verdict holds against the version in front of them.
