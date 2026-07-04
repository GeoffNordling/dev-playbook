---
type: Standard
title: ADR Conventions
description: When to write an ADR, its template, sequential numbering, and the hard-to-reverse-or-surprising bar that justifies one
---

# ADR Conventions

ADRs live in `docs/adr/` and use sequential 4-digit numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the `docs/adr/` directory lazily — only when the first ADR is needed.

## Index

The ADR listing lives in `docs/adr/index.md` — one line per ADR, carrying the ADR's `description` — so a reader or skill can find the relevant ADRs without opening every file. It follows the [indexes.md](/standards/docs/indexes.md) rules, and the staleness checker fails any commit that adds, renames, or removes an ADR without updating the index in the same change. Create it lazily alongside the first ADR.

`docs/adr/README.md` is a short narrative orientation for the directory, not the listing.

## When to offer an ADR

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

## Template

```md
---
type: ADR
title: {Short title of the decision}
description: {One-line summary of the decision, for triage and the index}
---

# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

An ADR is a concept document, so it carries the standard `type` + `title` + `description` frontmatter (see [document-types.md](/standards/document-types.md)). The `description` is the ADR's triage line and feeds `docs/adr/index.md`; on a one-sentence ADR it will echo the body — that's fine, the description is the triage surface and the body is the record.

## Optional sections

Only include these when they add genuine value. Most ADRs won't need them.

- **`status`** — an optional extra frontmatter key beyond the required three (`proposed | accepted | deprecated | superseded by ADR-NNNN`). Useful when decisions are revisited.
- **Considered Options** — only when the rejected alternatives are worth remembering.
- **Consequences** — only when non-obvious downstream effects need to be called out.

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one.
