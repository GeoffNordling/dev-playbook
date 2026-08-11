---
type: Standard
title: Doc Conventions
description: How Markdown docs are written — voice, structure, brevity, current-state-only, one concern per document
---

# Doc Conventions

How Markdown documents in workspace repos are written. Applies to every doc
in the repo documentation hierarchy.

## Current state and next steps only

Describe what exists and what's planned next. Don't reference removed things,
past state, or rejected alternatives.

Don't: "X is hand-maintained — there is no generator."
Do: "X is the source of truth."

Decision Records are the exception. A Decision Record in `docs/decisions/` is a
dated record of a past decision — the choice made, the alternatives rejected,
the context that forced it — and is never rewritten to match later state. This
rule binds every other doc.

## Voice

Declarative present tense. "The symlink is relative." Not "We make the
symlink relative."

State rules in the positive: what to do, where a thing lives. "Runnables
live in `scripts/`", not "don't put runnables elsewhere". A prohibition
appears only when the prohibition itself is the rule.

No second person in declarative docs. "You" belongs to agent-facing
instruction files — `CLAUDE.md` at every level, skills, and rules — that
direct an executor; a standard states facts.

## Spelling

House spelling is American English. Write `judgment`, not `judgement` — and
`judgments`, not `judgements`. `prose-lint` enforces this one deterministically,
because the British form slips back in through habit and voice dictation. Naming
the forbidden form in prose stays legible as long as it sits in backticks: the
detector checks only text outside code spans, so this section names it without
tripping itself.

## Heading casing

H1 uses Title Case. H2 and below use sentence case.
`# File Skeleton` at H1; `## Authored, not generated` at H2.

Proper nouns and code identifiers keep their native case at every level:
`# CLAUDE.md Content`, `## pyproject.toml`, `### Ask in prose, never AskUserQuestion`.

## Open with purpose

State what the document is for and what a reader should be able to do after
reading. Write for a cold-start reader who has no prior conversation context.

## One rule, one place

Each rule lives in the lead sentence of its section. If the lead carries the
rule, the section can stop there. Section size matches topic size.

State each rule once. Consolidate any duplicates.

## One concern per document

A document covers one concern. When a file accumulates several — distinct
questions a reader might arrive with — it splits into a directory of
single-concern documents with an `index.md`, per the
[OKF SPEC](/standards/references/okf-spec.md). A reader crawling for one
answer loads one small file, not a monolith that covers everything.

## Lead with the edge case when reach is surprising

If a rule has surprising scope, name the edge case in the lede: "These
conventions apply to every Python sub-project, including script-only ones
with no `src/`."

## Name concepts once, use consistently

Pick one name per concept and use it across the document. The repo's root
[`CONTEXT.md`](/CONTEXT.md) holds the established vocabulary; a doc uses its
terms where they apply, with no obligation to extend it.

## Terminology: the person is the user

One actor — the dispatcher, reviewer, and approver — carries one name
everywhere: the `user`. Agent-facing instruction text uses it because that is
what Claude Code calls the person (`AskUserQuestion`): `CLAUDE.md` at every
level — root, nested, and the global `dotfiles/dot-claude/CLAUDE.md` alike —
plus the skill and rule bodies under `dotfiles/dot-claude/skills/` and
`dotfiles/dot-claude/rules/`. Declarative documentation uses the same word
where it describes that actor in third person: `software-factory/`,
`standards/`, `docs/`, and `README.md`.

**One word, no synonyms.** The actor is `user` in every authored file — never
an alternative noun for the same person, in any case, plural, or hyphenated
compound. Where such a compound is the natural phrase, drop it rather than
translate it: "readable", not "readable by a person". Translate instead only
where the qualifier carries a distinction the reader needs — the system pauses
at many points and `software-factory/user-checkpoints.md` covers the subset
that are the user's, so dropping the word there would name the wrong set. The
test is whether removing it loses a distinction, not whether it reads well.

**Exemption is declared per repo in `.prose-lint-exempt`.** Text the rule does
not govern — captured external documents, prose authored for an outside
audience in that audience's vocabulary, a tool file that must name the word to
process it — is exempted by listing its path in a tracked `.prose-lint-exempt`
at the repo root: one repo-relative file or directory per line, a directory
covering its whole subtree, `#` opening a comment line. Any file is listable,
an `index.md` included — an index description that must carry the word exempts
its index the same way. This file is the one suppression surface, so every
exemption is a reviewable line, ideally under a comment saying why. Two
structural exemptions stand alongside it: skills vendored under an `.agents/`
path, and Markdown verbatim mirrors carrying `type: Reference` frontmatter,
which follows the document wherever it lives.

**Agent-facing instruction text never speaks in the first person.** No `I`, `me`,
or `my` in the files listed above: they are commands addressed *to* the agent,
so the only voices they carry are the imperative and `you`. A first-person
sentence puts the document in the agent's mouth, which inverts who is
instructing whom. `repo-lint` enforces this deterministically over the body of
every first-party skill and rule as well as `CLAUDE.md`.

The ban governs the document's own voice, so quoting someone else's is
untouched: a double-quoted utterance is exempt. Write the phrasing a user types
to trigger a skill, or the reaction a prototype exists to provoke, in their
words — `"Show me a few options before I commit."` — and reserve the
surrounding prose for the imperative. A skill's frontmatter is not exempt: its
`description` is prose the agent reads to choose the skill, so it answers to the
same voice as the body.

**Skills vendored verbatim are exempt.** A third-party skill under an `.agents/`
path is an external dependency, carried unmodified so it can be re-synced from
upstream; its voice is its author's to set. The ban governs what this workspace
writes and owns — the skills under `.claude/`.

## Choose each format by argument

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

## Point at canonical artifacts

When a real file IS the standard, the doc directs the reader to it.
The build standard's `canonical.md` names each canonical artifact and points
at the file instead of restating its contents.

## Trust the reader

Write for someone careful enough to follow a single sentence.

## Brevity

Choose brevity over completeness. A doc that's read beats a doc that's
complete. Trim further than instinct says.
