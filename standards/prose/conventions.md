---
type: Standard
title: Doc Conventions
description: How Markdown docs are written — the rules an authored document obeys on contents, opening, voice, naming, and mechanics
population: "an authored document, except type: Mirror and the paths in .prose-lint-exempt"
---

# Doc Conventions

How Markdown documents in workspace repos are written. Every authored
document is bound, except one carrying `type: Mirror` frontmatter — a
verbatim mirror of an external text, which keeps its author's words wherever
it lives. A repo exempts any further path by listing it in a tracked
`.prose-lint-exempt` at its root, under a comment saying why, and bans
words of its own, in all or part of its tree, by declaring each with its
replacement in a tracked `.prose-lint-vocabulary` at its root.

## One rule, one place

Each rule the document states lives in the lead sentence of one section, and no other section of the document states it again; the section's own heading, which names that same rule, sits inside that one place. Exempt: a statement of the document's own scope, which sits in the section under the H1.

`prose.one-rule-one-place` · stochastic

> **Why.** A section can stop at its lead when the lead carries the
> whole rule, so section size matches topic size and a reader who skims
> the leads reads every rule. A heading compressing that same rule is
> the section's name for it, so a heading and a lead that say the same
> thing are one place, not two; the second place this bars is another
> section, or another document, where the copies drift apart.

## Current state and next steps only

The document describes what exists and what is planned next, and does not
reference removed things, past state, or rejected alternatives. History earns
a sentence only where the present is unintelligible without it — a constraint
that still binds, a decision that still governs. A numbered Decision Record
is exempt.

`prose.current-state-and-next-steps-only` · stochastic

> **Why.** A Decision Record is exempt because it is a dated record of
> a past decision, frozen after merge.

## The canonical file, linked not copied

Where a file is itself the standard, the document links that file rather than reproducing its contents; naming one entry as a worked example is not reproduction.

`prose.the-canonical-file-linked-not-copied` · stochastic

> **Why.** A restated copy drifts from the file it restates.

## The opening states the purpose

The opening states what the document is for and what a reader should be able to do after reading; an `index.md` and a `README.md` answer instead to the opening-sentence and purpose-sentence rules of the knowledge-organization Standard.

`prose.the-opening-states-the-purpose` · stochastic

## Definition before first use

A concept is defined before the prose leans on it — the definition sits above
its first use.

`prose.definition-before-first-use` · stochastic

## Block form fits its content

A block's form fits what it holds: prose for an argument, a list for parallel
items, a table for repeated structure, a callout for an aside, a quote for
wording that is the point, and a code block for code that runs or spans lines.
The pairs:

- **Prose vs list.** Prose carries an argument; a list carries parallel items.
  Items that are not parallel are prose.
- **Inline vs callout.** A callout earns the break in flow where the aside
  would derail the argument inline.
- **Table vs repeated structure.** The same shape with the same fields two or more times is a table; anything fewer or uneven is prose with bold leads.
- **Quote vs paraphrase.** The quote goes where the original wording is the
  point; the paraphrase where only the idea is.
- **Code block vs inline code.** Multi-line, runnable, or illustrative code goes
  in a block; a single token or identifier stays inline.

`prose.block-form-fits-its-content` · stochastic

## Every sentence in the present tense

Every sentence is in the present tense, except a sentence reporting a measurement or an incident that happened, and except in a member of a working documentation set, which may write a guess as a guess.

`prose.every-sentence-in-the-present-tense` · stochastic

## A rule reads in the positive

A rule reads in the positive — what to do, where a thing lives — and a
prohibition appears only where the prohibition itself is the rule.

`prose.a-rule-reads-in-the-positive` · stochastic

## No slop tics

The document commits none of the tics
[Slop Tics](/guides/slop-tics.md) names.

`prose.no-slop-tics` · stochastic

## Harness-loaded agent instructions

The document is a harness-loaded agent instruction: it is a `CLAUDE.md`, or
a segment of its path inside the repository is `skills`, `rules`, or
`agents`.

### No first person

A harness-loaded agent instruction never speaks in the first person: the
words `I`, `me`, and `my` appear nowhere in it, its frontmatter included,
except `I` in the abbreviation `I/O` and any of the three inside a
double-quoted utterance, an inline code span, or a fenced block.

`prose.no-first-person` · deterministic

> **Why.** A harness-loaded agent instruction is addressed to the
> executing agent, so a first-person sentence puts the document in the
> agent's mouth and inverts who is instructing whom. The ban governs
> the document's own voice: a quoted utterance is another speaker's,
> while a runbook's `description` is the document speaking.

## Declarative documents

The document is a declarative document: it is not a `CLAUDE.md`, and no
segment of its path inside the repository is `skills`, `rules`, or `agents`.

### The third person, never the second

A declarative document speaks in the declarative mood and the third
person, and does not address the reader as `you`. Exempt: a
double-quoted utterance, and a name an encoding reads from a body as
an action, such as a Guide step's bold run, which speaks in the
imperative.

`prose.the-third-person-never-the-second` · stochastic

> **Why.** A step names an action the reader performs, and the
> imperative is the mood that names an action; the encoding reads that
> name out of the body, so it is a name and not the prose around it.

## One name, one concept

One name per concept holds across the document.

`prose.one-name-one-concept` · stochastic

## The person is the user

One actor, the dispatcher, reviewer, and approver, is the `user` throughout the document, its frontmatter, code spans, and fenced blocks included, never a synonym, in any case, plural, or compound. A numbered Decision Record is exempt.

`prose.the-person-is-the-user` · stochastic

## No banned word

The file does not contain a word the workspace vocabulary bans, `WORKSPACE_VOCABULARY` in `src/dev_playbook/prose_lint.py`, bare or plural, in any case, alone or in a compound, its frontmatter, code spans, and fenced blocks included.

`prose.no-banned-word` · deterministic

## No word the repo bans

No tracked file under a directory the repo's `.prose-lint-vocabulary`
names for a word contains that word, bare or plural, in any case, its
frontmatter, code spans, and fenced blocks included; a word declared
with no directory is banned in every tracked file of the repo.

`prose.no-word-the-repo-bans` · deterministic

> **Why.** The directories an entry names hold a term to the part of
> the tree that defines it, and leave the word alone where it means
> something else.

## Judgment, not judgement

The document's prose spells `judgment`, never the British `judgement` or
`judgements`, in any case. Exempt: the frontmatter, an inline code span, and a
fenced block.

`prose.judgment-not-judgement` · deterministic

## Title Case H1, sentence case below

The H1 is in Title Case and every heading below it is in sentence case, except
that a proper noun or a code identifier keeps its native case at any level, and
the `Considered Options` heading of a Decision Record is exempt.

`prose.title-case-h1-sentence-case-below` · stochastic

## Headings are propositions

Each heading below the H1 is a proposition the section establishes,
in the third person; each name an encoding reads from a body as an
action, such as a Guide step's bold run, is the imperative that names
the action. Exempt: a heading that states no point of its own and only
scopes the sections under it, which names the case those sections bind.
Both are written in block language, the register of headlines, articles
and copulas dropped, in the fewest words that carry the point, which is
a noun phrase wherever one carries it. The heading forms, over one
rule:

| Heading | Verdict |
|---|---|
| `Judgment, not judgement` | passes: the proposition, its verb dropped |
| `The prose spells judgment` | passes: the proposition, third person |
| `Spelling` | fails: the topic named |
| `Write judgment, not judgement` | fails: the imperative, which addresses the reader |
| `The prose spells judgment and never the British judgement` | fails: the predicate restated |

`prose.headings-are-propositions` · stochastic

> **Why.** A parse shows the headings and nothing beneath them, so read
> alone and in order the propositions are the document's argument; a
> topic name is only its table of contents, and a restated predicate is
> a second body.

