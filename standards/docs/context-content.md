---
type: Standard
title: CONTEXT.md Content
description: The CONTEXT.md domain glossary — structure, authoring rules, and a brief worked example
---

# CONTEXT.md Content

## Structure

Frontmatter (`type: Vocabulary`, `title`, `description`), an H1 with a
short purpose statement, then four sections: `## Language`,
`## Relationships`, `## Example dialogue`, `## Flagged ambiguities`. A
brief worked example:

```markdown
---
type: Vocabulary
title: Billing
description: The billing domain's canonical terms
---

# Billing

Terms for the order-to-payment flow.

## Language

**Order**:
A customer's confirmed request for goods.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent after delivery.
_Avoid_: Bill, payment request

## Relationships

- An **Order** produces one or more **Invoices**

## Example dialogue

> **Dev:** "When a customer places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once delivery is confirmed."

## Flagged ambiguities

- "account" was used for both **Customer** and **User** — resolved: distinct concepts.
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick
  the best one and list the others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out
  in "Flagged ambiguities" with a clear resolution.
- **Keep definitions tight.** One sentence max. Define what it IS, not what
  it does.
- **Show relationships.** Use bold term names and express cardinality where
  obvious.
- **Only include terms specific to this project's context.** General
  programming concepts (timeouts, error types, utility patterns) don't
  belong even if the project uses them extensively. Before adding a term,
  ask: is this a concept unique to this context, or a general programming
  concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all
  terms belong to a single cohesive area, a flat list is fine.
- **Write an example dialogue.** A conversation between a dev and a domain
  expert that demonstrates how the terms interact naturally and clarifies
  boundaries between related concepts.

## Location

One `CONTEXT.md` at the repo root, created lazily as terminology ambiguity
surfaces — never pre-populated.
