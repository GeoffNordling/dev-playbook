---
type: Explanation
title: Harness Explanation
description: The thinking behind the harness rules — which files the harness consumes, where a runbook lives, and why a CLAUDE.md has no frontmatter and one scope
---

# Harness Explanation

The reasoning behind the harness rulesets,
[Claude Code Files](/standards/harness/files.md) for which files the
harness consumes and where a runbook sits, and
[CLAUDE.md Content](/standards/harness/claude-content.md) for a
`CLAUDE.md`. The form of a runbook is
[Runbook Conventions](/standards/doc-type/runbook-conventions.md), and
its reasons are
[Doc-Type Explanation](/standards/doc-type/explanation.md#a-runbooks-file).

## Which files the harness consumes

Every member of [Claude Code Files](/standards/harness/files.md) has a
**class**, naming what the harness does with it: a **runbook** is
documentation that acts, invoked by name, its body governed by the
[Runbook doc-type](/doc-types/runbook/index.md); **context** is prose
injected into agent context, read and never invoked; **configuration**
is data the harness reads; **code** is a deterministic program the
harness runs. Claude Code is named deliberately as the only harness
currently in use.

## Where a runbook lives

A governed repo carries its runbooks under `.claude/`
([Location](/standards/harness/files.md#location)); dev-playbook carries
the workspace-global set under `dotfiles/dot-claude/`, which Stow links
into `~/.claude/`. harness-files-lint discovers runbooks at these roots
and stops on a directory under a skills root with no `SKILL.md`.

A helper script holds a deterministic operation, repeated logic, or a
step where token cost or reliability matters. Distinct sub-domains and
rarely needed material spill into `references/`, which is also where
material past the 500-line bound on `SKILL.md` goes; harness-files-lint
prints an advisory on a longer file, with no rule id
([Bundle layout](/standards/doc-type/runbook-conventions.md#bundle-layout)).

## Why a CLAUDE.md has no frontmatter

A `CLAUDE.md` is injected into the session as operating configuration,
and okf-lint never reads it, so it opens on its content
([No frontmatter](/standards/harness/claude-content.md#no-frontmatter)).
It holds only how to operate: commands, rules, and pointers to other
docs. What the project is, why it exists, and who develops it belong to
the documentation hierarchy. A root file's content is its repo's own
operating knowledge: its commands, its gotchas, the traps that would
cost an agent an hour.

## One scope

A rule sits at the widest scope where it is true, and at exactly one
([One scope](/standards/harness/claude-content.md#one-scope)). The
global source, `dotfiles/dot-claude/CLAUDE.md` in dev-playbook, carries
what holds for every session on the machine; a root file carries what
holds for its repo alone; a nested `<dir>/CLAUDE.md` carries only the
delta from the files above it. A root file with nothing repo-specific
to say is a title alone. A nested file sits in a directory whose
operating conventions diverge from the root.

The global source has two sections
([Two sections](/standards/harness/claude-content.md#two-sections)):
`## Principles` holds dispositional stances, how the agent carries
itself, and `## Behaviors` holds operating rules for named situations,
what the agent does. Behaviors leads because `### Read the standards`
must be the first heading in the file. That rule sends every agent to
the standards catalog at session start; its sibling
`### Navigate docs by index` states how to walk OKF indexes without
loading whole trees
([Required rules](/standards/harness/claude-content.md#required-rules)).
