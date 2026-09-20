---
type: Standard-Ruleset
title: Decision Record Conventions
description: How a Decision Record is written, from the bar that warrants one and the directory that holds it to its scope, template, date, numbering, status vocabulary, optional sections, and the pin on an external-convention evaluation
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

The reasoning behind the rules is the
[Decisions Guide](/docs/guides/decisions.md).

## The bar

A Decision Record records a decision that is hard to reverse, surprising
without its context, and the outcome of a real trade-off, all three at
once: changing course later carries meaningful cost, a future reader
looking at the code would wonder why it was done this way, and there
were genuine alternatives with a specific reason for the choice.

`decisions.the-bar` · stochastic

## Scope

A Decision Record sits in the `docs/decisions/` of the repo it governs,
and a decision that governs several repos sits in the repo that governs
them.

`decisions.scope` · stochastic

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

## Slug case

A Decision Record's slug, the part of its filename after `NNNN-` and
before `.md`, is kebab-case.

`decisions.slug-case` · deterministic

## Template

A Decision Record's frontmatter holds `type: Decision-Record`, a
`title`, a `description`, and a `date`; its body opens with an H1
repeating the `title`, followed by one to three sentences:

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

A Decision Record's opening sentences give the context the decision was
made in, the decision itself, and the reason for it.

`decisions.context-decision-and-reason` · stochastic

## Date

A Decision Record's `date` frontmatter key holds the day the decision
was made, written `YYYY-MM-DD`, or holds `null` where that day is
unrecoverable.

`decisions.date` · deterministic

## Immutable after merge

A Decision Record that `main` carries has its body, and every
frontmatter key other than `status`, byte-identical to the first
commit on `main` that carries the file.

`decisions.immutable-after-merge` · deterministic

## Status vocabulary

A Decision Record either carries no `status` frontmatter key or carries
one holding exactly one of `proposed`, `accepted`, `deprecated`, or
`superseded by NNNN`, where `NNNN` is four digits.

`decisions.status-vocabulary` · deterministic

## Supersession target

A Decision Record whose `status` is `superseded by NNNN` sits in a
directory that holds a record numbered `NNNN`.

`decisions.supersession-target` · deterministic

## Optional sections

A Decision Record's body carries no section beyond the H1 except
`Considered Options` and `Consequences`, and neither of those sections
is empty.

`decisions.optional-sections` · deterministic

## External-convention evaluation

A Decision Record's decision is a verdict on something outside the
workspace: a skill, a skill collection, a framework, or a technique.

`decisions.external-convention-evaluation` · stochastic

### What was examined

The Decision Record names the source and pins the exact state examined:
the repository SHA, the release or version, and the date it was read.

`decisions.what-was-examined` · stochastic
