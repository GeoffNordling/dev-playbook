---
type: Standard
title: CLAUDE.md Content
description: The CLAUDE.md content standard — operational scope, the canonical standards block, the nested-file hierarchy
---

# CLAUDE.md Content

Claude Code injects `CLAUDE.md` into every session as operating
configuration ([files.md](/standards/claude-code/files.md)), so it carries
no OKF frontmatter. Its scope is how to operate in the repo — commands,
rules, pointers to other docs. It `SHALL NOT` describe what the project is,
why it exists, or the developer: those belong to the documentation
hierarchy.

## The standards block

The universal content is the canonical block
[CLAUDE.md.standards](/standards/build/canonical/CLAUDE.md.standards),
present verbatim ([canonical.md](/standards/build/canonical.md)). It sends
every agent to the standards catalog at session start and states how to
navigate OKF indexes without loading whole trees — anything the repo's own
sections do not say, an agent finds by that crawl. The block's workspace
paths are backticked prose rather than live citations so the same bytes
serve every repo: a citation would be `wrong-form` inside dev-playbook
itself ([cross-references.md](/standards/docs/cross-references.md)).

Everything else in the file is the repo's own; operating rules accumulate
as the repo evolves.

## Hierarchy

Claude Code loads `CLAUDE.md` files by walking up the directory tree from
the session's cwd, stacking each file it finds. A session inside
`<repo>/<dir>/` therefore receives both the nested `CLAUDE.md` and the
repo-root `CLAUDE.md`.

A repository `MAY` add a nested `CLAUDE.md` in a directory whose operating
conventions diverge from the repo root (e.g. `dotfiles/` in dev-playbook).
The nested file holds **only the delta** — content already in the parent
`SHALL NOT` be repeated. A directory with nothing repo-divergent to say
doesn't need one.

Nested files follow the same scope as the root: operational instructions
for an agent operating inside that directory. They `SHALL NOT` contain
project description, architecture decisions, or roadmap — those belong
elsewhere in the documentation hierarchy.

## The global file

A user's `~/.claude/CLAUDE.md` is injected into every session regardless of
repo: it sits above the per-repo hierarchy and carries cross-repo operating
preferences, not project-specific rules. In this workspace it is not authored
in place — its source is `dotfiles/dot-claude/CLAUDE.md`, Stow-symlinked into
`~/.claude/`, so the governed artifact lives in dev-playbook and rides the
normal review path. As a `CLAUDE.md` it is already a registry member
([files.md](/standards/claude-code/files.md)) and already agent-facing
configuration, so it holds to the agent-facing voice — second person, the
human named as `user` ([conventions.md](/standards/prose/conventions.md)).

The global file `SHALL` be a **well-formed XML document** with exactly two
top-level elements:

- `<principles>` — dispositional stances, how to carry yourself. Each is a
  verb-first child element (`<be-direct>`, `<admit-uncertainty>`, …).
- `<behaviors>` — operating rules for named situations, what to do. Each is a
  verb-first child element (`<git-commit>`, `<sandbox>`, …).

Well-formedness and the
two-element shape are checked deterministically, but only in dev-playbook,
where the source file lives — other repos have no global file to check.
