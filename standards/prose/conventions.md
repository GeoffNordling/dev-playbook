---
type: Standard
title: Doc Conventions
description: How Markdown docs are written — contents, opening, section formats, voice, naming, and mechanics
---

# Doc Conventions

How Markdown documents in workspace repos are written. Applies to every
authored document, except one carrying `type: Reference` frontmatter — a
verbatim mirror of an external text, which keeps its author's words wherever
it lives. A repo exempts any further path by listing it in a tracked
`.prose-lint-exempt` at its root, under a comment saying why. Named tics to
remove are cataloged in [Slop Tics](/standards/prose/slop-tics.md).

## Contents

### One concern per document

A document covers one concern. When a file accumulates several — distinct
questions a reader might arrive with — it splits into a directory of
single-concern documents with an `index.md`, per the
[OKF SPEC](/standards/references/okf-spec.md). A reader crawling for one
answer loads one small file.

### One rule, one place

Each rule lives in the lead sentence of its section. If the lead carries the
rule, the section can stop there. Section size matches topic size.

### Current state and next steps only

Describe what exists and what's planned next. Don't reference removed things,
past state, or rejected alternatives.
[Changelog residue](/standards/prose/slop-tics.md) names the forms this takes.
History earns a sentence only when the present is unintelligible without
it — a constraint that still binds, a decision that still governs.

Decision Records are the exception. A Decision Record in `docs/decisions/` is a
dated record of a past decision — the choice made, the alternatives rejected,
the context that forced it — and is never rewritten to match later state.

### Point at canonical artifacts

When a real file IS the standard, the doc references that file instead of
restating its contents, in the form
[Cross-References](/standards/knowledge-organization/cross-references.md)
sets.

## Opening

### Open with purpose

State what the document is for and what a reader should be able to do after
reading. Say why that matters before the reader thinks to ask. Write for a
reader with no prior conversation context.

### Declare before use

Define a concept before the prose leans on it — the definition sits above its
first use. A concept another document defines is linked at first use.

### Lead with the edge case when reach is surprising

If a rule has surprising scope, name the edge case in the lede: "These
conventions apply to every Python sub-project, including script-only ones
with no `src/`."

## How to decide between section formats

Every block's form is a decision with a reason behind it. The arguments that
recur:

- **Prose vs list.** Prose carries an argument; a list carries parallel items.
  Items that aren't genuinely parallel read better as prose.
- **Inline vs callout.** A callout earns the break in flow when the aside would
  derail the argument inline.
- **Table vs repeated structure.** The same shape with the same fields three or
  more times is a table; anything fewer or uneven is prose with bold leads.
- **Quote vs paraphrase.** Quote where the original wording is the point;
  paraphrase where only the idea is.
- **Code block vs inline code.** Multi-line, runnable, or illustrative goes in a
  block; a single token or identifier stays inline.

## Voice

### Declarative present tense

"The symlink is relative." Not "We make the symlink relative."

### Positive statement

State rules in the positive: what to do, where a thing lives. "Runnables
live in `scripts/`", not "don't put runnables elsewhere". A prohibition
appears only when the prohibition itself is the rule.

### Person of address

Two kinds of document, two persons. **Harness-loaded agent instructions** — the
runbook and context members of the Claude Code file registry
([files.md](/standards/harness/files.md)) — are addressed *to* the executing
agent, so they speak in the imperative and `you`, and never in the first
person: no `I`, `me`, or `my`. A first-person sentence puts the document in the
agent's mouth, which inverts who is instructing whom. **A declarative
document** states facts to a reader instead: third person, no `you`.

The ban governs the document's own voice: a double-quoted utterance is exempt.
Write the phrasing a user types to trigger a skill, or the reaction a
prototype exists to provoke, in their words — `"Show me a few options before
I commit."` — and reserve the surrounding prose for the imperative. A
runbook's frontmatter is not exempt: its `description` is prose the agent
reads to choose the runbook, so it answers to the same voice as the body.

## Naming

### Name concepts once, use consistently

Pick one name per concept and use it across the document. The repo's root
[`CONTEXT.md`](/CONTEXT.md) holds the established vocabulary; a doc uses its
terms where they apply, with no obligation to extend it.

### Terminology: the person is the user

One actor — the dispatcher, reviewer, and approver — is the `user` in every
authored file, never a synonym, in any case, plural, or compound.

## Mechanics

### Spelling

House spelling is American English. Write `judgment`, not `judgement` — and
`judgments`, not `judgements`.

### Heading casing

H1 uses Title Case. H2 and below use sentence case.
`# File Skeleton` at H1; `## Authored, not generated` at H2.

Proper nouns and code identifiers keep their native case at every level:
`# CLAUDE.md Content`, `## pyproject.toml`, `### Ask in prose, never AskUserQuestion`.

### Grammatical parallelism

Items that sit together take the same grammatical shape: the headings of a
document, the bullets of a list, the clauses of a sentence. One form holds
throughout, so a break in the pattern marks a break in meaning.
