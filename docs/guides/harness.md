---
type: Guide
title: Harness Guide
description: The thinking behind the harness rules — where a runbook lives and what its front matter holds, what each skill and agent field does, how arguments reach a skill, what an agent's body is, and why a CLAUDE.md has no frontmatter and one scope
---

# Harness Guide

The guide behind the two harness rulesets,
[Runbook Conventions](/standards/harness/runbook-conventions.md) for a
skill bundle or an agent definition, and
[CLAUDE.md Content](/standards/harness/claude-content.md) for a
`CLAUDE.md`. This guide carries the templates, the field semantics, and
the reasoning; nothing here is enforced.

## Where a runbook lives

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional: docs the skill loads on demand
  scripts/          # optional: helper scripts the skill invokes
.claude/agents/<agent-name>.md
```

A governed repo carries these under `.claude/`; dev-playbook carries
the workspace-global set under `dotfiles/dot-claude/`, which Stow links
into `~/.claude/`. harness-files-lint discovers runbooks at these roots
and stops on a directory under a skills root with no `SKILL.md`.

A helper script holds a deterministic operation, repeated logic, or a
step where token cost or reliability matters. Distinct sub-domains and
rarely needed material spill into `references/`, which is also where
material past the 500-line bound on `SKILL.md` goes; harness-files-lint
prints an advisory on a longer file, with no rule id
([Bundle layout](/standards/harness/runbook-conventions.md#bundle-layout)).

## The front matter

A skill's block:

```yaml
name: <skill-name>
description: <what it does. Use when …>
disable-model-invocation: <true|false>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
allowed-tools: <tool spec>          # optional
disallowed-tools: <tool spec>       # optional
arguments: [<name>, ...]            # optional
```

An agent's block:

```yaml
name: <agent-name>
description: <what it does. Use when …>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
tools: <Tool, Tool, ...>            # optional
```

The vocabulary is exact
([Front matter](/standards/harness/runbook-conventions.md#front-matter)):
an agent declares no `arguments`, since its input is the launching
prompt, whole.

## What the fields do

**`description`.** For an agent, or a skill the model may invoke, the
first sentence states what the runbook does and the second, opening
`Use when`, names the keywords, contexts, or file types under which it
is invoked; that second sentence is what the model matches on. For a
skill only the user invokes, the description is the one-sentence
summary the user reads in the slash-command list
([Description](/standards/harness/runbook-conventions.md#description)).

**`disable-model-invocation`.** Under `false` the agent fires the skill
on its own and other skills reach it; under `true` only the user typing
its name invokes it
([Model invocation flag](/standards/harness/runbook-conventions.md#model-invocation-flag)).

**`model`.** A pinned model governs only the turn that loads the skill.
A skill that runs several turns with the user carries `inherit`.

**`allowed-tools` and `disallowed-tools`.** `allowed-tools`
pre-approves the listed calls to run without prompting;
`disallowed-tools` denies outright, and restates no denial a
`settings.json` already makes
([Tool fields](/standards/harness/runbook-conventions.md#tool-fields)).

**An agent's `tools`.** The launched agent's toolset is exactly that
list, and an agent without the field has the full toolset
([tools](/standards/harness/runbook-conventions.md#tools)). `tools` is
no cognate of a skill's `allowed-tools`: that pre-approves calls inside
the caller's permission flow, while a tool absent from `tools` does not
exist for the agent.

## How arguments reach a skill

The harness appends the input after the body as `ARGUMENTS: <text>`,
whole and unsplit, and the executing agent never sees the argument's
name. Every argument is a string. This is why the body carries no
`$ARGUMENTS` or `$0` placeholder: there is nothing for one to expand to
([Arguments](/standards/harness/runbook-conventions.md#arguments)).

## An agent's body is its system prompt

An agent's body is the launched subagent's system prompt, set at spawn:
it addresses the agent that runs it, and nothing else reaches that
agent except the launching prompt. The report travels back as the
subagent's final message. A runbook's steps therefore end on a
completion criterion, the condition that tells the agent the work is
done, because nothing else will.

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
