---
type: Standard-Ruleset
title: CONTEXT.md Content
description: The CONTEXT.md vocabulary center — Vocabulary frontmatter, the Language section, the entry shape, and the rules that keep a glossary tight
population: "a repo's CONTEXT.md"
---

# CONTEXT.md Content

A repo's `CONTEXT.md`, its vocabulary disambiguation center: when
several words compete for one concept, one is picked and the rest
retired. It appears at the root or not at all
([File Skeleton](/standards/build/skeleton.md#root-only-files));
repo-lint checks its shape
([Knowledge Organization](/standards/knowledge-organization/card.md)).

## Glossary only

The file is a glossary and nothing else: no implementation details, no
spec, no scratch pad.

Implementation decisions live in Decision Records
([Decision Record Conventions](/standards/decisions/records.md)).

## OKF frontmatter

The file opens with `type: Vocabulary`, `title`, and `description`
([Document Types](/standards/knowledge-organization/document-types.md)).

## The Language section

`## Language` is present, the one required section.

## Entry shape

An entry is the term in bold on its own line, its definition beneath,
and an `_Avoid_` line listing the words retired in its favor where other
words compete.

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

## One word per concept

When several words exist for one concept, the entry picks the best one
and lists the others under `_Avoid_`.

## Tight definitions

A definition is one sentence that says what the term is; where a
concept document defines the term, the sentence links it, and that
document is the definition's home
([terms defined once](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-defined-once)).

## Project terms only

Every term is specific to the project's context; a general programming
concept, a timeout, an error type, a utility pattern, has no entry,
however heavily the project uses it; nor has a term one documentation
set defines and uses within itself. This file holds the term that
crosses sets.

The test before adding a term: is this a concept unique to this context,
and used beyond the set that defines it? Only then does it belong.
