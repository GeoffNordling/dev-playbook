---
type: Standard
title: Decision Record Conventions
description: When to write a Decision Record, its template, sequential numbering, immutability, status vocabulary, scope, and the hard-to-reverse-or-surprising bar that justifies one
---

# Decision Record Conventions

Decision Records live in `docs/decisions/` and use sequential 4-digit numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the `docs/decisions/` directory lazily — only when the first record is needed.

> An **ADR** (Architecture Decision Record) is the industry term for the architectural subset of this kind. A Decision Record is the same artifact generalized past architecture to any hard-to-reverse decision; where a decision is architectural, "ADR" and "Decision Record" name the same thing.

## Scope

A decision lives with the thing it governs: a decision about one repo is recorded in that repo's `docs/decisions/`; a decision about the workspace — a standard, a cross-repo convention, the software factory — is recorded in dev-playbook.

## Index

The record listing lives in `docs/decisions/index.md` — one line per record, carrying the record's `description` — so a reader or skill can find the relevant records without opening every file. It follows the [indexes.md](/standards/docs/indexes.md) rules, and the staleness checker fails any commit that adds, renames, or removes a record without updating the index in the same change. Create it lazily alongside the first record.

`docs/decisions/README.md` is a short narrative orientation for the directory, not the listing.

## When to offer a Decision Record

All three must be true:

1. **Hard to reverse** — changing course later carries meaningful cost.
2. **Surprising without context** — a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and a specific reason for the choice.

An easy-to-reverse decision is simply reversed, not recorded. An unsurprising one raises no questions. One with no real alternative leaves nothing to record beyond "we did the obvious thing."

## What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library — just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** When GraphQL was considered and REST won for subtle reasons, record it — otherwise GraphQL gets proposed again in six months.
- **External-convention evaluations.** A deliberate look at something outside the workspace — a skill, a skill collection, a framework, a technique — ends in a record, pinning exactly what was examined (repo SHA, version, date). Adopting nothing is still a decision; the record is what stops the same source being re-evaluated from scratch in six months.

## Template

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

That's it. A Decision Record can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

A Decision Record is a concept document, so it carries the standard `type` + `title` + `description` frontmatter (see [document-types.md](/standards/docs/document-types.md)). The `description` is the record's triage line and feeds `docs/decisions/index.md`; on a one-sentence record it will echo the body — that's fine, the description is the triage surface and the body is the record.

## Date

Every record carries a `date` frontmatter key: the day the decision was made, `YYYY-MM-DD`. A record written after the fact carries the decision's date, not the writing date. Where the day is genuinely unrecoverable, `date: null` — never a guess. Records predating this key (introduced 2026-08-01) were backfilled from the dates their own text or git history could prove, null otherwise.

## Immutability

A record's body is frozen once its introducing pull request merges. Before merge, the record is ordinary development-branch work and is edited freely. After merge, the body is never rewritten — not to match later state, not to fix a decision that was reversed. Only the `status` key may change thereafter. To reverse or replace a decision, write a **new** record and set the old one's `status` to `superseded by NNNN`. There is deliberately no deterministic check for immutability; it is a rule the reviewer upholds.

## Status vocabulary

`status` is an optional extra frontmatter key beyond the required three. When present, it holds exactly one of:

- `proposed`
- `accepted`
- `deprecated`
- `superseded by NNNN` — where `NNNN` is the 4-digit, zero-padded number of the record that replaces this one.

`decisions-lint` matches this vocabulary exactly. Omit `status` entirely when a record needs none.

## Optional sections

Only include these when they add genuine value. Most records won't need them.

- **Considered Options** — only when the rejected alternatives are worth remembering.
- **Consequences** — only when non-obvious downstream effects need to be called out.

## Numbering

Scan `docs/decisions/` for the highest existing number and increment by one.
