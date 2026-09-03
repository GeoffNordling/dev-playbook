---
type: Standard
title: Runbook Conventions
description: The format a runbook takes — location, front matter, the description, model and effort, the H1, completion criteria, the chain, and the rules a skill bundle and an agent definition each add
population: "a runbook: a skill bundle or an agent definition under a governed repo's .claude/ or dev-playbook's dotfiles/dot-claude/"
---

# Runbook Conventions

A runbook: a skill bundle or an agent definition under a governed
repo's `.claude/` or dev-playbook's `dotfiles/dot-claude/`, the harness
files that act. A bundle whose directory is a symlink belongs to
whatever manages its target, so it is outside the population and
harness-files-lint skips it. The
[Runbook doc-type](/doc-types/runbook/index.md) declares a runbook's
contract, the Reference chain; this Standard binds the file: where it
sits, its front matter, its body's shape, and what each kind adds. The
craft of the body, the two loads, the information hierarchy, and
pruning, is [Writing for Agents](/standards/harness/writing-for-agents.md),
read to write one; this Standard wins where the two collide. A rule
that names a `harness.*` id is checked by harness-files-lint.

## Location

A skill is `<skills root>/<name>/SKILL.md` and an agent is
`<agents root>/<name>.md`, the roots being `.claude/skills/` and
`.claude/agents/` in a governed repo and `dotfiles/dot-claude/skills/`
and `dotfiles/dot-claude/agents/` in dev-playbook.

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional: docs the skill loads on demand
  scripts/          # optional: helper scripts the skill invokes
.claude/agents/<agent-name>.md
```

dev-playbook's roots are Stow-linked into `~/.claude/`.
harness-files-lint discovers runbooks at these roots and stops on a
directory under a skills root with no `SKILL.md`.

## Front matter

The file opens with a YAML block between `---` lines holding exactly
its kind's vocabulary: a skill's `name`, `description`,
`disable-model-invocation`, `model`, and `effort`, with
`allowed-tools`, `disallowed-tools`, and `arguments` optional; an
agent's `name`, `description`, `model`, and `effort`, with `tools`
optional (`harness.parse`, `harness.front-matter`,
`harness.required-field`, `harness.unknown-field`).

A skill's block:

```yaml
---
name: <skill-name>
description: <what it does. Use when …>
disable-model-invocation: <true|false>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
allowed-tools: <tool spec>          # optional
disallowed-tools: <tool spec>       # optional
arguments: [<name>, ...]            # optional
---
```

An agent's block:

```yaml
---
name: <agent-name>
description: <what it does. Use when …>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
tools: <Tool, Tool, ...>            # optional
---
```

The two vocabularies are closed: the fields above are all of them.

## Name matches its home

`name` equals the bundle directory for a skill and the file stem for an
agent (`harness.name-match`).

## Kebab-case name

`name` is kebab-case (`harness.name-format`).

## Description

`description` is a string of at most 1024 characters; for an agent, or
a skill with `disable-model-invocation: false`, it is exactly two
sentences, the first stating what the runbook does and the second
opening with the literal words `Use when` and naming the trigger
keywords, contexts, or file types; for a skill with
`disable-model-invocation: true` it is exactly one sentence, the
summary the user reads in the slash-command list
(`harness.description-type`, `harness.description-length`,
`harness.description-sentences`, `harness.description-trigger`).

The two-sentence form is the invocation match surface, the context
pointer the agent reads to reach the runbook, so it is specific, and
every word of it costs on every turn:

- **Front-load the leading word.** The pointer is where it does its
  triggering work.
- **One trigger per branch.** Synonyms that rename a single branch are
  one branch written twice; collapse them and keep only genuinely
  distinct branches.
- **Cut identity the body already carries.**

[Writing for Agents](/standards/harness/writing-for-agents.md#context-pointers)
carries the pointer model behind the three.

## Model and effort

`model` is one of `haiku`, `sonnet`, `opus`, `fable`, or `inherit`, and
`effort` is one of `low`, `medium`, `high`, or `xhigh`
(`harness.model-value`, `harness.effort-value`).

## Body opens with an H1

The body's first non-blank line after the front matter is an H1
(`harness.body-h1`).

## Steps end on a completion criterion

Every step of the body ends on a completion criterion: the condition
that tells the agent the work is done.

The criterion's clarity, whether the agent can tell done from not-done,
and its demand, how much it requires, are the two levers
[Writing for Agents](/standards/harness/writing-for-agents.md#steps-and-completion-criteria)
explains.

## Carries its chain

Every edge of the runbook's contract is declared in the runbook's own
file: args by the front matter `arguments` list, and each read, write,
do, override, never, and report as a span in the body that the
[Reference Chain Encoding](/doc-types/runbook/encoding.md) parses; the
runbook's chain in `doc-types/runbook/chains.txt` is the one
`scripts/chaingen` writes from them.

A ban the span vocabulary cannot carry stays plain prose, recorded in
the [runbook residual ledger](/doc-types/runbook/residual-ledger.md).

## Skill

A bundle `<skills root>/<name>/` holding `SKILL.md`, and optionally
`references/` and `scripts/`.

### Bundle layout

`SKILL.md` sits at the bundle root; docs the skill loads on demand sit
in `references/`, linked from `SKILL.md`; helper scripts sit in
`scripts/`, invoked from `SKILL.md`.

A helper script holds a deterministic operation, repeated logic, or a
step where token cost or reliability matters. Distinct sub-domains and
rarely-needed material spill into `references/`, so the agent loads
each file on demand instead of paying the context cost up front.

### Model invocation flag

`disable-model-invocation` is present and boolean (`harness.dmi-type`).

Under `false` the agent fires the skill on its own and other skills
reach it; under `true` only the user typing its name invokes it.

### Interactive skills inherit

A skill that runs several turns with the user carries `model: inherit`.

A pinned model governs only the turn that loads the skill.

### Tool fields

`allowed-tools` and `disallowed-tools`, when present, are
space-separated tool specs, as in `Bash(git *) Bash(gh *)`, and
`disallowed-tools` restates no denial `settings.json` already makes.

`allowed-tools` pre-approves the listed calls to run without prompting,
the form for a focused, mechanical skill; `disallowed-tools` denies
outright, the form for a stance that must be enforced rather than asked
for.

### Arguments

`arguments`, when present, is a non-empty list of bare kebab-case names,
as in `arguments: [subject]`, and the body carries no `$ARGUMENTS` or
`$0` placeholder (`harness.arguments-format`, the list only).

The harness appends the input after the body as `ARGUMENTS: <text>`,
whole and unsplit, and the executing agent never sees the argument's
name. Every argument is a string, so the name alone carries the
meaning, for the user and for the
[Reference chain](/doc-types/runbook/contract-shape.md).

### References one level deep

No file in `references/` links to another file in `references/`
(`harness.references-depth`).

The lazy-load pattern assumes a flat tree: the agent loads each file on
demand from `SKILL.md`.

### SKILL.md under 500 lines

`SKILL.md` is under 500 lines.

harness-files-lint prints an advisory on a longer one, with no rule id.
Material past the bound spills into `references/` under
[Bundle layout](#bundle-layout).

## Agent

One flat file `<agents root>/<name>.md`.

### tools

`tools`, when present, is a non-empty comma-separated string of tool
names, and the launched agent's toolset is exactly that list
(`harness.tools-format`).

An agent without the field has the full toolset. `tools` is no cognate
of a skill's `allowed-tools`: that pre-approves calls inside the
caller's permission flow, while a tool absent from `tools` does not
exist for the agent.

### No arguments

The front matter declares no `arguments`; the agent's input is the
launching prompt, whole (`harness.unknown-field`).

An agent's body is the launched subagent's system prompt, set at spawn:
it addresses the agent that runs it, and nothing else reaches that
agent except the launching prompt. The report travels back as the
subagent's final message.
