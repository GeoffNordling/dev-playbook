---
type: Explanation
title: Prose Explanation
description: The thinking behind the prose rules — where a rule sits in a section, why history is cut, how a block's form is chosen, why the two voices differ, what the slop-tics catalog is, and the examples that show the casing and parallelism rules
---

# Prose Explanation

The reasoning behind [Doc Conventions](/standards/prose/conventions.md),
the ruleset that binds an authored document, with the examples.

## One rule, one place

Each rule lives in the lead sentence of its section, so a section can
stop there when the lead carries the whole rule; section size matches
topic size ([One rule, one place](/standards/prose/conventions.md#one-rule-one-place)).
Across documents the same discipline is
[one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home).

A rule with surprising scope names the edge case in its lead: "These
conventions apply to every Python sub-project, including script-only
ones with no `src/`." A reader who skims the lead then knows the reach.

## Why history is cut

A document describes what exists and what is planned next
([Current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)).
[Changelog residue](/guides/slop-tics.md#changelog-residue)
names the forms the residue takes. History earns a sentence only where
the present is unintelligible without it, a constraint that still
binds, a decision that still governs. A Decision Record is the
exception because it is a dated record of a past decision, frozen after
merge ([Decisions Explanation](/standards/decisions/explanation.md)).

When a real file is itself the standard, a document points at that file
in the form the cross-reference rules set instead of restating its
contents, because a restated copy drifts.

## How a block's form is chosen

Prose carries an argument; a list carries parallel items, and items
that are not genuinely parallel read better as prose. A callout earns
the break in flow only where the aside would derail the argument
inline. The same shape with the same fields three or more times is a
table; fewer or uneven is prose with bold leads. A quote goes where the
original wording is the point. Multi-line, runnable, or illustrative
code goes in a block; a single token or identifier stays inline
([Block form fits its content](/standards/prose/conventions.md#block-form-fits-its-content)).

## Present tense and the positive

"The symlink is relative." Not "We make the symlink relative." A
member of a working documentation set may write a guess as a guess;
that is the whole exemption
([Declarative present tense](/standards/prose/conventions.md#declarative-present-tense)).

A rule reads in the positive: "Runnables live in `scripts/`", not
"don't put runnables elsewhere". A prohibition appears only where the
prohibition itself is the rule
([Positive statement](/standards/prose/conventions.md#positive-statement)).

## The slop-tics catalog

[Slop Tics](/guides/slop-tics.md) is the content of the
[No slop tics](/standards/prose/conventions.md#no-slop-tics) rule: each
tic's definition, the action that removes it, and before-and-after
examples. The document-remove-tics skill rewrites a document against it
on demand.

## The two voices

A harness-loaded agent instruction, a `CLAUDE.md` or a file under
`skills/`, `rules/`, or `agents/`, is addressed to the executing agent,
so it speaks in the imperative and `you` and never in the first person.
A first-person sentence puts the document in the agent's mouth, which
inverts who is instructing whom
([No first person](/standards/prose/conventions.md#no-first-person)).
The ban governs the document's own voice, so a double-quoted utterance
is exempt: the phrasing a user types to trigger a skill, or the
reaction a prototype exists to provoke, appears in their words,
`"Show me a few options before I commit."`, while the surrounding
prose stays imperative. A runbook's frontmatter is not exempt: its
`description` is prose the agent reads to choose the runbook, so it
answers to the same voice as the body.

Every other authored document states facts to a reader, so it speaks in
the third person, with the same utterance exemption
([Third person](/standards/prose/conventions.md#third-person)).

## One name per concept

One name per concept holds across a document. The repo's root
`CONTEXT.md` holds the established vocabulary; a document uses its
terms where they apply, with no obligation to extend it. The one actor
who dispatches, reviews, and approves is the `user`, and prose-lint's
`banned-word` check refuses the commonest synonym everywhere in the
tree, code and config included, with no backtick escape
([Terminology: the person is the user](/standards/prose/conventions.md#terminology-the-person-is-the-user)).
The banned word is the workspace's layer of a vocabulary a repo extends
in its own `.prose-lint-vocabulary`: each entry is a word, the word that
replaces it, and the directories the ban covers, so a term one part of
a tree defines is held to there and left alone where it means something
else. dev-playbook bans `guard` under `doc-types/` and
`standards/doc-type/`, where the doc-type system's word is `condition`,
and not in code, where a guard clause is a guard clause
([The repo vocabulary](/standards/prose/conventions.md#the-repo-vocabulary)).
House spelling is American English, which is why `judgment` is the
one word prose-lint spells for the writer.

## Casing and parallelism

`# File Skeleton` at H1; `## Authored, not generated` at H2. Proper
nouns and code identifiers keep their native case at every level:
`# CLAUDE.md Content`, `## pyproject.toml`,
`### Ask in prose, never AskUserQuestion`
([Heading casing](/standards/prose/conventions.md#heading-casing)).

Items that sit together take the same grammatical shape, the headings
of a document, the bullets of a list, the clauses of a sentence. One
form holds throughout, so a break in the pattern marks a break in
meaning
([Grammatical parallelism](/standards/prose/conventions.md#grammatical-parallelism)).
