---
type: Standard
title: CLAUDE.md Content
description: What a CLAUDE.md carries — no frontmatter, operational content at one scope, and the two sections, the required rules, and the first rule of the global source in dev-playbook
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

> **Why.** `## Behaviors` leads because `### Read the standards` must
> be the first `###` heading in the file. That rule sends every agent to the
> standards catalog at session start; its sibling `### Navigate docs
> by index` states how to walk OKF indexes without loading whole
> trees.

## No frontmatter

The first line of a `CLAUDE.md` is not `---`.

`harness.no-frontmatter` · deterministic

> **Why.** A `CLAUDE.md` is injected into the session as operating
> configuration, and okf-lint never reads it.

## Operational content only

A `CLAUDE.md` holds only how to operate — commands, rules, and pointers
to other docs — and carries nothing of what the project is, why it
exists, or who develops it.

`harness.operational-content-only` · stochastic

## One rule, one scope

A nested `<dir>/CLAUDE.md` states no rule already stated in the root
file above it.

`harness.one-rule-one-scope` · stochastic

> **Why.** A rule sits at the widest scope where it is true:
> machine-wide in the global source, repo-wide in the root file, only
> the delta in a nested file. A repo can check one part of that, the
> nested file against its root.

## Global file

The `CLAUDE.md` sits at `dotfiles/dot-claude/CLAUDE.md`, the global
source linked to `~/.claude/CLAUDE.md`.

### Behaviors, then Principles

The global source's H2 headings outside fenced code blocks are exactly
`## Behaviors` then `## Principles`, in that order.

`harness.behaviors-then-principles` · deterministic

### Two required rules

The global source has the headings `### Read the standards` and
`### Navigate docs by index`, both outside fenced code blocks.

`harness.two-required-rules` · deterministic

### Read the standards first

`### Read the standards` is the first `###` heading of the global
source, outside fenced code blocks.

`harness.read-the-standards-first` · deterministic

### One rule per heading

Each rule of the global source is one `###` heading under its bucket: a
dispositional stance under `## Principles`, an operating rule for a
named situation under `## Behaviors`.

`harness.one-rule-per-heading` · stochastic
