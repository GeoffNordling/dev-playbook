---
type: Standard
title: CLAUDE.md Content
description: The CLAUDE.md content standard and the nested-file hierarchy — operational scope, deltas only
---

# CLAUDE.md Content

`CLAUDE.md` is harness-owned ([bundle.md](/standards/docs/bundle.md)) — an
agent's harness loads it as operating configuration, not as prose to learn
from — so it carries no OKF frontmatter.

The `## Build` section is universal — every repo has `make check` (see
[make.md](/standards/build/make.md)). Project-specific operating rules
accumulate under `## Rules` as the repo evolves.

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
