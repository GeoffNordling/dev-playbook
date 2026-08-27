---
type: Standard
title: Runbook Conventions
description: Runbook format conventions — skill and agent front matter, arguments, progressive disclosure, and the agent body
---

# Runbook Conventions

Format conventions for the **runbook** class — the harness files that
act: skills and agents.
[files.md](/standards/harness/files.md) registers the members and their
layout; the [Instruction Grammar](/standards/harness/grammar.md) governs
a runbook's body; this standard governs the rest — front matter,
identity, and the content of each part. Two sections follow, one per
kind.

## Skills

A skill is a bundle of `SKILL.md` plus optional `references/` and
`scripts/` directories; the tree and locations are in
[files.md](/standards/harness/files.md). The bundle's directory name
must match the front matter `name`.

### Front matter

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

These eight fields are the whole skill vocabulary; a new one requires an
edit here before its first use.

- `name` — kebab-case, matching the bundle directory. Related skills
  share a namespace prefix.
- `description` — plain text, max 1024 chars, third person, exactly two
  sentences. The first states what the skill does; the second begins
  with the literal words `Use when` and names the trigger keywords,
  contexts, or file types verbatim — it is the invocation match surface,
  so be specific.
- `disable-model-invocation` — always explicit, never left to the
  default. `false` is the standard; `true` only for skills meant for
  direct user invocation, and under `true` the description is exactly
  one sentence — the summary the user reads in the slash-command list,
  trigger sentence dropped.
- `model`, `effort` — mandatory; the user decides both explicitly, and
  `inherit` is a choice like any other. A pinned model governs only the
  turn that loads the skill, so an interactive, multi-turn skill takes
  `inherit`.
- `allowed-tools` — space-separated tool specs, e.g.
  `Bash(git *) Bash(gh *)`, pre-approved to run without prompting. For
  focused, mechanical skills.
- `disallowed-tools` — same format; denies outright. For a stance that
  must be enforced rather than asked for. Don't restate a workspace-wide
  denial from the settings.
- `arguments` — one kebab-case name per input; see
  [Arguments](#arguments).

### Arguments

Write each argument as a bare kebab-case name in the `arguments` list —
`arguments: [subject]` — and put no placeholder (`$ARGUMENTS`, `$0`) in
the body. The reason is how invocation behaves: the harness appends the
input after the body as `ARGUMENTS: <text>`, whole and unsplit, and the
executing agent never sees the argument's name. Every argument is a
string, so the name alone carries the meaning — for the user and for the
[Reference chain](/standards/harness/grammar.md).

### Progressive disclosure

Keep SKILL.md under ~500 lines. Spill distinct sub-domains and
rarely-needed material into `references/`, linked from SKILL.md; the
agent loads each file on demand instead of paying the context cost up
front. References stay one level deep — a file in `references/` does not
link to another — because the lazy-load pattern assumes a flat tree.

Helper scripts — deterministic operations, repeated logic, steps where
token cost or reliability matters — go in `scripts/`, invoked from
SKILL.md.

---

## Agents

An agent is one flat file; locations are in
[files.md](/standards/harness/files.md). The file stem must match the
front matter `name`.

### Front matter

```yaml
---
name: <agent-name>
description: <what it does. Use when …>
tools: <Tool, Tool, ...>            # optional
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
---
```

These five fields are the whole agent vocabulary; a new one requires an
edit here before its first use. `name`, `description`, `model`, and
`effort` follow the skill rules above. The one agent-only field:

- `tools` — a hard allowlist: comma-separated tool names, and the
  launched agent has exactly these tools; omit the field and the agent
  has the full toolset. Not a cognate of a skill's `allowed-tools` —
  that pre-approves calls inside the caller's permission flow, while a
  tool absent from `tools` does not exist for the agent.

### The body is the system prompt

An agent's body is the launched subagent's system prompt, set at spawn:
it addresses the agent that runs it, and nothing else reaches that agent
except the launching prompt. An agent therefore declares no arguments —
input arrives in the launching prompt, and the report travels back as
the subagent's final message.
