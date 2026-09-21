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
[No first person](/standards/prose/conventions.md#no-first-person).

The reasoning behind the rules is the
[Harness Explanation](/standards/harness/explanation.md).

## No frontmatter

A `CLAUDE.md` opens on its content, with no YAML frontmatter block.

`harness.no-frontmatter` · deterministic

## Operational scope

A `CLAUDE.md` holds only how to operate — commands, rules, and pointers
to other docs — and carries nothing of what the project is, why it
exists, or who develops it.

`harness.operational-scope` · stochastic

## One scope

Every rule in a `CLAUDE.md` sits at the widest scope where it is true,
and at exactly one: the global source carries what holds for every
session on the machine, a root file carries what holds for its repo
alone, and a nested `<dir>/CLAUDE.md` carries only the delta from the
files above it.

`harness.one-scope` · stochastic

## Global file

The `CLAUDE.md` sits at `dotfiles/dot-claude/CLAUDE.md`, the global
source linked to `~/.claude/CLAUDE.md`.

`harness.global-file` · deterministic

### Two sections

The global source's H2 headings outside fenced code blocks are exactly
`## Behaviors` then `## Principles`, in that order.

`harness.two-sections` · deterministic

### Required rules

The global source carries the headings `### Read the standards` and
`### Navigate docs by index`, both outside fenced code blocks.

`harness.required-rules` · deterministic

### One rule per heading

Each rule of the global source is one `###` heading under its bucket: a
dispositional stance under `## Principles`, an operating rule for a
named situation under `## Behaviors`.

`harness.one-rule-per-heading` · stochastic
