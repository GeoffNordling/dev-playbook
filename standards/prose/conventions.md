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
instruction files — skills — that direct an executor; a
standard states facts.

## Heading casing

H1 uses Title Case. H2 and below use sentence case.
`# File Skeleton` at H1; `## Authored, not generated` at H2.

Proper nouns and code identifiers keep their native case at every level:
`# CLAUDE.md Content`, `## pyproject.toml`, `### SSH-bound git operations`.

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

## Terminology: human vs user

One actor — the dispatcher, reviewer, and approver — wears two names, chosen by
voice. **Agent-facing instruction text says `user`**: the skill and rule bodies
under `dotfiles/dot-claude/skills/` and `dotfiles/dot-claude/rules/`, read by the
executing agent, name that person the way Claude Code does (`AskUserQuestion`).
**Declarative documentation says `human`**: `workflow/`, `standards/`, `docs/`,
`README.md`, and `CLAUDE.md` describe the system in third person, where the actor
is the human dispatcher.

One override applies on top, wherever the token appears:

- **Platform tokens stay `user`** — the `~/.claude/` "User" settings tier, a
  "user message", `user-invocable`. These are Claude Code's own names, not ours
  to translate.

## Point at canonical artifacts

When a real file IS the standard, the doc directs the reader to it.
The build standard's `canonical.md` names each canonical artifact and points
at the file instead of restating its contents.

## Trust the reader

Write for someone careful enough to follow a single sentence.

## Brevity

Choose brevity over completeness. A doc that's read beats a doc that's
complete. Trim further than instinct says.
