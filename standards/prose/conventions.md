---
type: Standard-Ruleset
title: Doc Conventions
description: How Markdown docs are written — the rules an authored document obeys on contents, opening, voice, naming, and mechanics
population: "an authored document, except type: Reference and the paths in .prose-lint-exempt"
---

# Doc Conventions

How Markdown documents in workspace repos are written. Every authored
document is bound, except one carrying `type: Reference` frontmatter — a
verbatim mirror of an external text, which keeps its author's words wherever
it lives. A repo exempts any further path by listing it in a tracked
`.prose-lint-exempt` at its root, under a comment saying why.

The reasoning behind the rules is the
[Prose Explanation](/standards/prose/explanation.md).

## One rule, one place

Each rule the document states lives in the lead sentence of its section.

`prose.one-rule-one-place` · stochastic

## Current state and next steps only

The document describes what exists and what is planned next, and does not
reference removed things, past state, or rejected alternatives. History earns
a sentence only where the present is unintelligible without it — a constraint
that still binds, a decision that still governs. A numbered Decision Record
is exempt.

`prose.current-state-and-next-steps-only` · stochastic

## Point at canonical artifacts

Where a file is itself the standard, the document references that file and
does not restate its contents.

`prose.point-at-canonical-artifacts` · stochastic

## Open with purpose

The opening states what the document is for and what a reader should be able
to do after reading. It says why that matters before the reader thinks to ask,
and addresses a reader with no prior conversation context.

`prose.open-with-purpose` · stochastic

## Declare before use

A concept is defined before the prose leans on it — the definition sits above
its first use.

`prose.declare-before-use` · stochastic

## Block form fits its content

A block's form fits what it holds: prose for an argument, a list for parallel
items, a table for repeated structure, a callout for an aside, a quote for
wording that is the point, and a code block for code that runs or spans lines.
The pairs:

- **Prose vs list.** Prose carries an argument; a list carries parallel items.
  Items that are not parallel are prose.
- **Inline vs callout.** A callout earns the break in flow where the aside
  would derail the argument inline.
- **Table vs repeated structure.** The same shape with the same fields three or
  more times is a table; anything fewer or uneven is prose with bold leads.
- **Quote vs paraphrase.** The quote goes where the original wording is the
  point; the paraphrase where only the idea is.
- **Code block vs inline code.** Multi-line, runnable, or illustrative code goes
  in a block; a single token or identifier stays inline.

`prose.block-form-fits-its-content` · stochastic

## Declarative present tense

Every sentence is in the present tense, except in a member of a
[working documentation set](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md),
which may write a guess as a guess.

`prose.declarative-present-tense` · stochastic

## Positive statement

A rule reads in the positive — what to do, where a thing lives — and a
prohibition appears only where the prohibition itself is the rule.

`prose.positive-statement` · stochastic

## No slop tics

The document commits none of the tics
[Slop Tics](/guides/slop-tics.md) names.

`prose.no-slop-tics` · stochastic

## Harness-loaded agent instructions

The document is a harness-loaded agent instruction: it is a `CLAUDE.md`, or
a segment of its path inside the repository is `skills`, `rules`, or
`agents`.

`prose.harness-loaded-agent-instructions` · deterministic

### No first person

A harness-loaded agent instruction never speaks in the first person: the
words `I`, `me`, and `my` appear nowhere in it, its frontmatter included,
except `I` in the abbreviation `I/O` and any of the three inside a
double-quoted utterance, an inline code span, or a fenced block.

`prose.no-first-person` · deterministic

## Declarative documents

The document is a declarative document: it is not a `CLAUDE.md`, and no
segment of its path inside the repository is `skills`, `rules`, or `agents`.

`prose.declarative-documents` · deterministic

### Third person

A declarative document speaks in the declarative mood and the third person,
and does not address the reader as `you`, except inside a double-quoted
utterance.

`prose.third-person` · stochastic

## Name concepts once, use consistently

One name per concept holds across the document.

`prose.name-concepts-once-use-consistently` · stochastic

## Terminology: the person is the user

One actor — the dispatcher, reviewer, and approver — is the `user`
throughout the document, its frontmatter, code spans, and fenced blocks
included, never a synonym, in any case, plural, or compound.

`prose.terminology-the-person-is-the-user` · stochastic

## The banned word

No tracked file of the repo, except a path `.prose-lint-exempt` lists,
contains the word `human`, bare or plural, in any case, alone or in a
compound, its frontmatter, code spans, and fenced blocks included.

`prose.the-banned-word` · deterministic

## Spelling

The document's prose spells `judgment`, never the British `judgement` or
`judgements`, in any case. Exempt: the frontmatter, an inline code span, and a
fenced block.

`prose.spelling` · deterministic

## Heading casing

The H1 is in Title Case and every heading below it is in sentence case, except
that a proper noun or a code identifier keeps its native case at any level.

`prose.heading-casing` · stochastic

## Grammatical parallelism

Items that sit together take the same grammatical shape: the headings of a
document, the bullets of a list, the clauses of a sentence.

`prose.grammatical-parallelism` · stochastic
