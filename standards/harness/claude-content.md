---
type: Standard
title: CLAUDE.md Content
description: What a CLAUDE.md carries — no frontmatter, operational content at one scope, and the two sections and required rules of the global source in dev-playbook
population: "a CLAUDE.md: a repo's root file, a nested <dir>/CLAUDE.md, or in dev-playbook the global source dotfiles/dot-claude/CLAUDE.md"
---

# CLAUDE.md Content

A `CLAUDE.md` that Claude Code injects into a session as operating
configuration: a repo's root file, a nested `<dir>/CLAUDE.md` below it,
or the global source `dotfiles/dot-claude/CLAUDE.md` in dev-playbook,
which Stow links to `~/.claude/CLAUDE.md`. The harness loads the global
file into every session on the machine, then walks up the directory
tree from the session's cwd and stacks each `CLAUDE.md` it finds, so a
session inside `<repo>/<dir>/` receives the nested file, the root file,
and the global file at once. The registry of every file the harness
loads is [Claude Code Files](/standards/harness/files.md); the voice a
`CLAUDE.md` speaks in is Doc Conventions'
[Imperative and second person](/standards/prose/conventions.md#imperative-and-second-person).

## No frontmatter

The file opens on its content, with no YAML frontmatter block: it is
injected as operating configuration, and okf-lint never reads it.

## Operational scope

The file holds only how to operate: commands, rules, and pointers to
other docs.

What the project is, why it exists, and who develops it belong to the
documentation hierarchy, so a `CLAUDE.md` carries none of it. A root
file's content is its repo's own operating knowledge: its commands, its
gotchas, the traps that would cost an agent an hour.

## One scope

A rule sits at the widest scope where it is true, and at exactly one:
the global source carries what holds for every session on the machine,
a root file carries what holds for its repo alone, and a nested file
carries only the delta from the files above it.

A root file with nothing repo-specific to say is a title alone. A
nested file sits in a directory whose operating conventions diverge
from the root.

## Global file

`dotfiles/dot-claude/CLAUDE.md` in dev-playbook: the source Stow links
to `~/.claude/CLAUDE.md`. harness-files-lint checks the rules below
where the source lives, so in dev-playbook only.

### Two sections

The H2 headings are exactly `## Principles` then `## Behaviors`, in
that order, headings inside fenced blocks excluded
(`harness.global-claude-shape`).

`## Principles` holds dispositional stances, how the agent carries
itself; `## Behaviors` holds operating rules for named situations, what
the agent does.

### Required rules

The headings `### Read the standards` and `### Navigate docs by index`
are present (`harness.global-claude-rules`).

Both are Behaviors. Read the standards sends every agent to the
standards catalog at session start; Navigate docs by index states how
to walk OKF indexes without loading whole trees.

### One rule per heading

Each rule is one `###` heading under its bucket: a dispositional stance
under `## Principles`, an operating rule for a named situation under
`## Behaviors`.
