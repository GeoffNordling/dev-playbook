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

## Choosing between user and human

When a clause involves a person, pick the word by what sits opposite them. If
`agent` — or a workflow node or role — is the other half of the sentence, write
`human`; if the sentence is simply a skill serving the person in front of it,
write `user`. A `user` is always a `human`; the two are a register split, not
synonyms.

Workflow node, label, and mode names are fixed and always use `human`, even in
prose: `human-review`, `phase:human-code-review`, `(human, work)`, HITL.

See [CONTEXT.md](~/workspace/dev-playbook/CONTEXT.md) for the definitions of
`human`, `user`, and `agent`, and for the homonyms the rule leaves untouched
(the "User" settings tier, fixed Claude Code tokens, downstream end-users,
`human-readable`).

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
