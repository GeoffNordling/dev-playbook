---
type: Standard
title: Runbook Conventions
description: Runbook format — the shared frontmatter core, skill-bundle structure, and agent-definition rules
---

# Runbook Conventions

Format conventions for the **runbook** class — the harness files that
act: skill bundles and agent definitions, per
[the harness-file registry](/standards/harness/files.md). The
[Instruction Grammar](/standards/harness/grammar.md) governs a runbook's
body; this standard governs everything around it — file layout,
frontmatter, identity.

## Every runbook

Both kinds share four fields, and the rules are the same everywhere:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case, concise, verb-noun or noun when obvious. Related runbooks share a namespace prefix. The name must match its identity anchor — a skill's directory name, an agent's file stem. |
| `description` | Plain text, max 1024 chars, third person, **exactly two sentences**. The first states what the runbook does; the second `SHALL` begin with the literal words `Use when` and name the trigger keywords, contexts, or file types verbatim — it is the invocation match surface, so be specific. Keep the wording minimal.|
| `model` | The model the runbook runs under, or `inherit` to follow the session model. Mandatory. **The user decides `model` and `effort` explicitly**. |
| `effort` | Mandatory, no default — the user's decision, same as `model`. |

### Cross-references

A runbook has no fixed repo root; it cites other files per
[cross-references.md — Runbooks](/standards/knowledge-organization/cross-references.md#runbooks).

## Skills

A skill is a bundle:

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional — supplementary docs loaded on demand
  scripts/          # optional — helper scripts the skill invokes
```

The directory name must match the `name` field in the front matter.
Global skills live in `dotfiles/dot-claude/skills/`, stow-linked into
`~/.claude/skills/`; repo skills live in that repo's `.claude/skills/`.

### Skill front matter

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
edit here before its first use. Where a skill adds to the shared rules:

| Field | Rules |
|-------|-------|
| `disable-model-invocation` | Always explicit — never left to the default (`false`). Use `true` only for skills meant for direct user invocation. Under `true` the description is exactly one sentence — the one-line summary the user reads in the slash-command list, trigger sentence dropped. |
| `model` | A pinned model governs only the turn that loads the skill, so an interactive, multi-turn skill takes `inherit`. |
| `allowed-tools` | Space-separated tool specs, e.g. `Bash(git *) Bash(gh *)`, pre-approved to run without prompting. Use for focused, mechanical skills. |
| `disallowed-tools` | Same format; denies outright. Use where a stance must be enforced rather than asked for. Don't restate a workspace-wide denial from the settings. |
| `arguments` | One kebab-case name per input. See [Arguments](#arguments). |

### Arguments

A skill that takes input declares each argument by name in the
`arguments` frontmatter list — `arguments: [subject]`, one kebab-case
name per input. Names only: invocation input is text substitution, so
every argument is a string and a type would distinguish nothing — the
name must carry the meaning. The body carries no placeholder
(`$ARGUMENTS`, `$0`): the harness appends the invocation input after
the body as `ARGUMENTS: <text>`, whole and unsplit, and the executing
agent never sees the argument's name — the name carries meaning for the
user and the [Reference chain](/standards/harness/grammar.md).

### References directory

Keep SKILL.md under ~500 lines. When content exceeds that, has distinct
sub-domains, or contains rarely-needed advanced material, spill into a
`references/` subdirectory and link from SKILL.md per the
cross-reference rule above:

```markdown
See [UI.md](references/UI.md) for UI element details.
```

The agent loads these on demand rather than paying the context cost
upfront.

References are one level deep: files in `references/` `SHALL NOT` link to
other reference files in the same skill bundle. The lazy-load pattern
assumes a flat tree; nested references defeat the savings and confuse the
loading agent.

### Scripts directory

For skills that invoke helper scripts — deterministic operations, repeated
logic, or steps where token cost or reliability matters — place them in
a `scripts/` subdirectory. Reference them from SKILL.md per the
cross-reference rule above:

```markdown
Run [check.py](scripts/check.py) to validate the result.
```

A skill-bundle `scripts/` directory is not the same as a project-root
`scripts/`. The bundle's `scripts/` lives under
`.claude/skills/<skill-name>/scripts/` and holds skill-internal helpers
the agent invokes while running the skill. A repo's project-root
`scripts/`, where it exists, holds project-level workspace scripts and
is governed elsewhere.

## Agents

An agent definition is one flat file, `<name>.md` — no bundle. Global
agents live in `dotfiles/dot-claude/agents/`, stow-linked into
`~/.claude/agents/`; repo agents live in that repo's `.claude/agents/`.

### Agent front matter

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
edit here before its first use. Where an agent adds to the shared rules:

| Field | Rules |
|-------|-------|
| `tools` | A hard allowlist: comma-separated tool names, and the launched agent has exactly these tools. Omit the field and the agent has the full toolset. Not a cognate of a skill's `allowed-tools` — that pre-approves calls inside the caller's permission flow, while `tools` defines the toolset itself, so a tool absent from the list does not exist for the agent. |

### The body is the system prompt

An agent's body is the launched subagent's system prompt, set at
spawn — it addresses the agent that runs it, and nothing else reaches
that agent except the launching prompt. An agent therefore declares no
arguments: its input arrives in the launching prompt, and its report
travels back as the subagent's final message.
