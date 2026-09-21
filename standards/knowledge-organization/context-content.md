---
type: Standard
title: CONTEXT.md Content
description: The CONTEXT.md vocabulary center — Vocabulary frontmatter, the Language section, the entry shape, and the rules that keep a glossary tight
population: "a repo's CONTEXT.md"
---

# CONTEXT.md Content

A repo's `CONTEXT.md`, its vocabulary disambiguation center: when
several words compete for one concept, one is picked and the rest
retired. It appears at the root or not at all
([File Skeleton](/standards/build/skeleton.md#root-only-files)).

The reasoning behind the rules is the
[Knowledge Organization Explanation](/standards/knowledge-organization/explanation.md).

## Glossary only

A repo's `CONTEXT.md` holds a glossary and nothing else: no
implementation detail, no specification, and no scratch note.

`knowledge-organization.glossary-only` · stochastic

## Vocabulary type

A repo's `CONTEXT.md` declares `type: Vocabulary` in its frontmatter.

`knowledge-organization.vocabulary-type` · deterministic

## The Language section

A repo's `CONTEXT.md` has a `## Language` section.

`knowledge-organization.the-language-section` · deterministic

## Entry shape

An entry under `## Language` in a repo's `CONTEXT.md` is the term in
bold on its own line, its definition on the lines beneath, and, at
most, one final `_Avoid_:` line naming the words retired in the term's
favor.

````md
---
type: Vocabulary
title: {Context Name}
description: {One-line description of the vocabulary}
---

# {Context Name}

{One or two sentences on what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request
````

`knowledge-organization.entry-shape` · deterministic

## Tight definitions

An entry's definition in a repo's `CONTEXT.md` is one sentence that says
what the term is, and where a concept document defines the term the
definition links that document.

`knowledge-organization.tight-definitions` · stochastic

## Project terms only

Every term with an entry under `## Language` in a repo's `CONTEXT.md` is
specific to the project's context and is used beyond the documentation
set that defines it: a general programming concept, a timeout, an error
type, a utility pattern, has no entry however heavily the project uses
it, and nor has a term one documentation set defines and uses within
itself.

`knowledge-organization.project-terms-only` · stochastic
