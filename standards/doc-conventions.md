# Doc Conventions

How Markdown documents in workspace repos are written. Applies to every doc
in the repo documentation hierarchy — `README.md`, `CLAUDE.md`, files under
`standards/`, `specs/`, `docs/`.

## Voice

Declarative present tense. "The symlink is relative." Not "We make the
symlink relative."

## Heading casing

H1 uses Title Case. H2 and below use sentence case.
`# Repo Documentation Standard` at H1; `## Audience and presence` at H2.

Proper nouns and code identifiers keep their native case at every level:
`## CLAUDE.md baseline`, `## .gitignore baseline`, `### SSH-bound git operations`.

## Open with purpose

State what the document is for and what a reader should be able to do after
reading. Write for a cold-start reader who has no prior conversation context.

## One rule, one place

Each rule lives in the lead sentence of its section. If the lead carries the
rule, the section can stop there. Section size matches topic size.

State each rule once. Consolidate any duplicates.

## Lead with the edge case when reach is surprising

If a rule has surprising scope, name the edge case in the lede: "These
conventions apply to every Python sub-project, including script-only ones
with no `src/`."

## Name concepts once, use consistently

Pick one name per concept and use it across the document.

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

## Current state and next steps only

Describe what exists and what's planned next. Don't reference removed things,
past state, or rejected alternatives.

Don't: "X is hand-maintained — there is no generator."
Do: "X is the source of truth."

## Point at canonical artifacts

When a real file IS the standard, the doc directs the reader to it.
`build-conventions.md` notes that the canonical pre-commit hook set is
`.pre-commit-config.yaml` and points there.

## Trust the reader

Write for someone careful enough to follow a single sentence.

## Brevity

Choose brevity over completeness. A doc that's read beats a doc that's
complete. Trim further than your instinct says.
