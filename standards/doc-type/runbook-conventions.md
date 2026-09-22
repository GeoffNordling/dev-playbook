---
type: Standard
title: Runbook Conventions
description: The format a runbook takes — front matter, the description, model and effort, the H1, the chain, and the rules a skill bundle and an agent definition each add
population: "a runbook: a skill bundle or an agent definition under a governed repo's .claude/ or dev-playbook's dotfiles/dot-claude/"
---

# Runbook Conventions

A runbook: a skill bundle or an agent definition under a governed
repo's `.claude/` or dev-playbook's `dotfiles/dot-claude/`, the harness
files that act. A bundle whose directory is a symlink belongs to
whatever manages its target, so it is outside the population and
harness-files-lint skips it. The
[Runbook doc-type](/doc-types/runbook/index.md) declares a runbook's
contract, the chain; this Standard binds the file: its front matter,
its body's shape, and what each kind adds; where it sits is
[Every runbook at a fixed path](/standards/harness/files.md#every-runbook-at-a-fixed-path). The
craft of the body, the two loads, the information hierarchy, and
pruning, is [Writing for Agents](/guides/writing-for-agents.md),
read to write one; this Standard wins where the two collide.

> **Why.** A runbook is read by a program, the Claude Code harness,
> before it is read by a model, so each rule below is about what a part
> of the file means to the program that loads it. The rules sit here
> and not under Harness Files because the Runbook doc-type's contract
> shape claims the keys, `name`, `description`, `model`, `effort`, and
> a skill's `disable-model-invocation` and `arguments`: what the file
> declares is the doc-type's, and where the harness finds it is the
> harness's.

## Front matter holds its kind's vocabulary

A runbook opens with a YAML block between `---` lines holding exactly
its kind's vocabulary: a skill's `name`, `description`,
`disable-model-invocation`, `model`, and `effort`, with
`allowed-tools`, `disallowed-tools`, and `arguments` optional; an
agent's `name`, `description`, `model`, and `effort`, with `tools`
optional.

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

`doc-type.front-matter-holds-its-kinds-vocabulary` · deterministic

> **Why.** The harness reads a closed set of keys, so a key outside the
> vocabulary is read by nothing. An agent's input is the launching
> prompt, whole, which is why the vocabulary gives an agent no
> `arguments`.

## Name matches its home

A runbook's `name` equals the bundle directory for a skill and the file
stem for an agent.

`doc-type.name-matches-its-home` · deterministic

## Kebab-case name

A runbook's `name` is kebab-case.

`doc-type.kebab-case-name` · deterministic

## Description, two sentences or one

A runbook's `description` is a string of at most 1024 characters. For
an agent, or a skill whose `disable-model-invocation` is not `true`, it
is exactly two sentences and the second opens with the literal words
`Use when`. For a skill with `disable-model-invocation: true` it is
exactly one sentence.

`doc-type.description-two-sentences-or-one` · deterministic

> **Why.** The second sentence is what the model matches a runbook
> against. A skill only the user invokes is matched by nobody: its one
> sentence is the summary the user reads in the slash-command list.

## Description states what and when

The first sentence of a runbook's `description` states what the runbook
does. Where that `description` has a second sentence, the second
sentence names the keywords, contexts, or file types under which the
runbook is invoked.

`doc-type.description-states-what-and-when` · stochastic

## Model and effort from closed sets

A runbook's `model` is one of `haiku`, `sonnet`, `opus`, `fable`, or
`inherit`, and its `effort` is one of `low`, `medium`, `high`, or
`xhigh`.

`doc-type.model-and-effort-from-closed-sets` · deterministic

## Body opens with an H1

The first non-blank line of a runbook's body, after the front matter,
is an H1.

`doc-type.body-opens-with-an-h1` · deterministic

## Carries its chain

Every edge of a runbook's contract is declared in the runbook's own
file: what it accepts by the front matter `arguments` list, and each
read, write, banned write, do, override, and report as a span in the body that
[encoding.md](/doc-types/runbook/encoding.md) parses, except an edge the
span vocabulary cannot carry, which stays plain prose in the body and
is listed in
[residual-ledger.md](/doc-types/runbook/residual-ledger.md).

`doc-type.carries-its-chain` · stochastic

## Skill

The runbook is a skill.

### Every bundle file reached from SKILL.md

Every file in a skill's `references/` is linked from its `SKILL.md`,
and every file in its `scripts/` is invoked from its `SKILL.md`.

`doc-type.every-bundle-file-reached-from-skillmd` · deterministic

### Boolean disable-model-invocation

A skill's `disable-model-invocation` is boolean.

`doc-type.boolean-disable-model-invocation` · deterministic

### Interactive skills inherit

A skill that runs several turns with the user carries `model: inherit`.

`doc-type.interactive-skills-inherit` · stochastic

> **Why.** A pinned model governs only the turn that loads the skill.

### Tool fields, space-separated specs

A skill's `allowed-tools` and `disallowed-tools`, when present, are
space-separated tool specs, as in `Bash(git *) Bash(gh *)`.

`doc-type.tool-fields-space-separated-specs` · deterministic

### Arguments, bare kebab-case names

A skill's `arguments`, when present, is a non-empty list of bare
kebab-case names, as in `arguments: [subject]`.

`doc-type.arguments-bare-kebab-case-names` · deterministic

### No argument placeholder

A skill's body carries no `$ARGUMENTS` placeholder and no `$0`
placeholder.

`doc-type.no-argument-placeholder` · deterministic

> **Why.** The harness appends the input after the body as
> `ARGUMENTS: <text>`, whole and unsplit, and the executing agent never
> sees the argument's name, so a placeholder has nothing to expand to.

### References one level deep

No `.md` file in a skill's `references/` links to another `.md` file
in that `references/`.

`doc-type.references-one-level-deep` · deterministic

### SKILL.md at most 500 lines

A skill's `SKILL.md` body is at most 500 lines.

`doc-type.skillmd-at-most-500-lines` · deterministic

## Agent

The runbook is an agent.

### Tools, comma-separated tool names

An agent's `tools`, when present, is a non-empty comma-separated string
of tool names.

`doc-type.tools-comma-separated-tool-names` · deterministic

> **Why.** `tools` is no cognate of a skill's `allowed-tools`: that
> pre-approves calls inside the caller's permission flow, while a tool
> absent from `tools` does not exist for the agent.
