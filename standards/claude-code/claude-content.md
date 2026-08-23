---
type: Standard
title: CLAUDE.md Content
description: The CLAUDE.md content standard — operational scope, the global and repo files, the nested-file hierarchy
---

# CLAUDE.md Content

Claude Code injects `CLAUDE.md` into every session as operating
configuration ([files.md](/standards/claude-code/files.md)), so it carries
no OKF frontmatter. Its scope is how to operate — commands, rules, pointers
to other docs. It `SHALL NOT` describe what the project is, why it exists,
or the developer: those belong to the documentation hierarchy.

**Scope is the only thing that separates them**: the global file carries
what holds for every session on the machine, a repo's file carries what
holds for that repo alone. A rule `SHALL` live at the widest scope where it
is true, and at exactly one.

## The repo file

A repo's `CLAUDE.md` carries its own operating knowledge and nothing else —
its commands, its gotchas, the traps that would cost an agent an hour. No
content is mandated: the workspace-wide instructions live in the global
file, and a repo with nothing repo-specific to say writes nothing but a
title. Structure is the repo's own; it is checked for form, never for
content.

## The global file

A user's `~/.claude/CLAUDE.md` is injected into every session regardless of
repo: it sits above the per-repo hierarchy and carries what is true of every
repo on the machine. In this workspace it is not authored in place — its
source is `dotfiles/dot-claude/CLAUDE.md`, Stow-symlinked into `~/.claude/`,
so the governed artifact lives in dev-playbook and rides the normal review
path. As a `CLAUDE.md` it is a registry member
([files.md](/standards/claude-code/files.md)) and agent-facing
configuration, so it holds to the agent-facing voice — second person, never
first ([conventions.md](/standards/prose/conventions.md)).

The file `SHALL` bucket its rules under exactly two H2 sections, in order:

- `## Principles` — dispositional stances, how to carry yourself.
- `## Behaviors` — operating rules for named situations, what to do.

Each rule is one `###` heading under its bucket. Behaviors are `REQUIRED`,
because no repo file restates them and this is the only place they can be
placed: **Read the standards**, which sends every agent to the standards
catalog at session start, and **Navigate docs by index**, which states how
to walk OKF indexes without loading whole trees. Their workspace paths are
backticked prose rather than live citations, since a citation would be
`wrong-form` inside dev-playbook itself
([cross-references.md](/standards/docs/cross-references.md)).

The section shape and the two required rules are checked deterministically,
but only in dev-playbook, where the source file lives — other repos have no
global file to check.

## Hierarchy

Claude Code loads `CLAUDE.md` files by walking up the directory tree from
the session's cwd, stacking each file it finds. A session inside
`<repo>/<dir>/` therefore receives both the nested `CLAUDE.md` and the
repo-root `CLAUDE.md`.

A repository `MAY` add a nested `CLAUDE.md` in a directory whose operating
conventions diverge from the repo root. The nested file holds **only the
delta** — content in the parent `SHALL NOT` be repeated, which is the same
one-scope rule that empties the repo file of workspace-wide content. A
directory with nothing repo-divergent to say doesn't need one.

Nested files follow the same scope as the root: operational instructions
for an agent operating inside that directory. They `SHALL NOT` contain
project description, architecture decisions, or roadmap — those belong
elsewhere in the documentation hierarchy.
