---
type: Standard
title: Decision Record Conventions
description: How a Decision Record is written, from the bar that warrants one and the directory that holds it to its scope, template, date, numbering, immutability, status vocabulary, optional sections, and the pin on an external-convention evaluation
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

A record records a decision that is hard to reverse, surprising without
its context, and the outcome of a real trade-off, all three at once:
changing course later carries meaningful cost, a future reader looking
at the code would wonder why it was done this way, and there were
genuine alternatives with a specific reason for the choice.

An easy-to-reverse decision is simply reversed, not recorded. An
unsurprising one raises no questions. One with no real alternative
leaves nothing to record beyond "we did the obvious thing."

Decisions that clear the bar:

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library — just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** When GraphQL was considered and REST won for subtle reasons, record it — otherwise GraphQL gets proposed again in six months.

## Scope

A record sits in the repo of the thing it governs: a decision about one
repo is recorded in that repo's `docs/decisions/`, and a decision about
the workspace, a standard, a cross-repo convention, or the software
factory, is recorded in dev-playbook.

## The directory

A repo's `docs/decisions/` holds numbered records, one `index.md`, and
one `README.md`, and nothing else. It is created lazily, with the first
record.

ref-lint classifies every file it finds there. A numbered record is
exempt as a reference source, since an immutable record goes stale as
its referents move; `index.md` and `README.md` are validated like any
other document; and any other file stops the run rather than being
silently exempted.

## Sequential numbering

A record's filename is `NNNN-slug.md`: a number zero-padded to four
digits, a hyphen, then a kebab-case slug. The number is unique in the
directory and one higher than the highest number already there, so the
sequence has no gaps.

A writer numbering a new record scans `docs/decisions/` for the highest
existing number and increments by one. `decisions-lint` reports a
number that is not zero-padded to four digits, a duplicate, and a gap in
the sequence (`decisions.sequential-numbering`).

## Template

A record's frontmatter and body match the template below: the three
standard keys `type`, `title`, and `description`, plus `date`; then an
H1 repeating the title; then one to three sentences giving the context,
the decision, and the reason.

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

A Decision Record can be a single paragraph: the value is in recording
that a decision was made and why, not in filling out sections.

A Decision Record is a concept document, so it carries the standard
`type` + `title` + `description` frontmatter (see
[Document Types](/standards/knowledge-organization/document-types.md)).
The `description` is the record's triage line and feeds
`docs/decisions/index.md`; on a one-sentence record it echoes the body,
since the description serves triage and the body is the record.

## Date

A record carries a `date` frontmatter key holding the day the decision
was made, `YYYY-MM-DD`. A record written after the fact carries the
decision's date, not the writing date, and where that day is genuinely
unrecoverable the key holds `null` rather than a guess.

## Immutability

A record's body is frozen once its introducing pull request merges:
thereafter only the `status` key changes, and a reversal or a
replacement is a new record that sets the old one's `status` to
`superseded by NNNN`.

Before merge, the record is ordinary development-branch work and is
edited freely. After merge, the body is never rewritten, neither to
match later state nor to correct a decision that was reversed.

## Status vocabulary

`status` is an optional frontmatter key beyond the required three, and
when present it holds exactly one of `proposed`, `accepted`,
`deprecated`, or `superseded by NNNN`, where `NNNN` is the 4-digit,
zero-padded number of the record that replaces this one.

`decisions-lint` matches this vocabulary exactly
(`decisions.status-vocabulary`). A record that needs no status omits the
key.

## Optional sections

Beyond the template a record carries at most two further sections,
`Considered Options` and `Consequences`, and neither appears empty.

- **Considered Options** — the rejected alternatives, when they are
  worth remembering.
- **Consequences** — the non-obvious downstream effects, when they need
  to be called out.

Most records carry neither.

## External-convention evaluation

A record whose decision is a verdict on something outside the
workspace: a skill, a skill collection, a framework, or a technique.

### What was examined

The record names the source and pins the exact state examined: the
repository SHA, the release or version, and the date it was read. A
record that adopted nothing is a record all the same.
