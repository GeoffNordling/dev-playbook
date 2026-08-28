---
type: Standard
title: CONTEXT.md Content
description: The CONTEXT.md vocabulary center — one root file, the glossary entry shape, and the rules that keep definitions tight
---

# CONTEXT.md Content

CONTEXT.md is the repo's vocabulary disambiguation center: when several
words compete for one concept, pick one and retire the rest. It is a
glossary and nothing else — no implementation details, no spec, no scratch
pad. Implementation decisions belong in Decision Records
([records.md](/standards/decisions/records.md)).

One file, at the repo root; `repo-lint` reports a `CONTEXT.md` outside the
root as `build.forbidden`. Create it lazily — when the first term is
resolved.

## Shape

- **OKF frontmatter.** `type: Vocabulary`, `title`, and `description`, as
  every concept document carries
  ([document-types.md](/standards/knowledge-organization/document-types.md)).
- **`## Language`** is the one required section; `repo-lint` reports its
  absence as `knowledge-organization.doc-shape`.

````md
---
type: Vocabulary
title: {Context Name}
description: {One-line description of the vocabulary}
---

# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
````

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick
  the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS,
  not what it does.
- **Only include terms specific to this project's context.** General
  programming concepts (timeouts, error types, utility patterns) don't
  belong even if the project uses them extensively. Before adding a term,
  ask: is this a concept unique to this context, or a general programming
  concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all
  terms belong to a single cohesive area, a flat list is fine.
