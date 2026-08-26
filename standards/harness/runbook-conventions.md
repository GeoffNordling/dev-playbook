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
frontmatter, identity. For the full feature reference (subagent
execution, shell injection, hooks, etc.), see the official
[skill](https://code.claude.com/docs/en/skills) and
[subagent](https://code.claude.com/docs/en/sub-agents) documentation.

This standard is binding, and
[harness-files-lint](/scripts/harness-files-lint) enforces it at the
commit gate. The craft beside it is the installed `/writing-for-agents`
skill, which covers any document an agent consumes and discloses its
skill-specific half to `SKILL-MECHANICS.md`. Invoke it when authoring or
editing a runbook. Where the two collide this standard wins: it fixes
workspace facts the skill has no view on — the closed frontmatter
vocabularies, the always-explicit `disable-model-invocation`, and the
description form.

## Every runbook

A runbook is harness-owned — Claude Code loads it as configuration, not
as prose to learn from — so it is not an OKF concept document. Its front
matter is the harness schema for its kind, **not** the OKF
`type`/`title`/`description` profile. See
[the two file roles](/standards/knowledge-organization/file-roles.md).

Both kinds share four fields, and the rules are the same everywhere:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case, concise, verb-noun or noun when obvious — `commit`, `ref-lint`, never `do-the-commit-thing`. Related runbooks share a namespace prefix: `issue-review-claims`, `issue-review-simulation`. The name must match its identity anchor — a skill's directory name, an agent's file stem. |
| `description` | Plain text, max 1024 chars, third person, **exactly two sentences**. The first states what the runbook does; the second `SHALL` begin with the literal words `Use when` and name the trigger keywords, contexts, or file types verbatim — it is the invocation match surface, so be specific. Keep the wording minimal; nothing checks length. Sentences are counted dumbly: `.`, `!`, or `?` ends one when whitespace or the string's end follows, so `CANDIDATES.md` is safe mid-sentence but `e.g.` ends a sentence early. |
| `model` | The model the runbook runs under — `haiku`, `sonnet`, `opus`, or `fable` — or `inherit` to follow the session model. Mandatory. **The user decides `model` and `effort` explicitly**, never an agent and never a machinery default; `inherit` is a choice like any other. |
| `effort` | `low`, `medium`, `high`, or `xhigh`. No default — the user's decision, same as `model`. |

A good description names the job and the trigger: `Write the failing
tests for a change before any implementation lands. Use when starting
the red phase of TDD, when a build leaf carries tests:yes, or when the
user asks for test-first work.` A bad one pads and names no trigger:
`A helpful utility that assists with various testing-related tasks and
workflows. Use when needed.`

### Body

After the front matter, the body is Markdown.

- Start with an `# H1` title. Use the runbook's readable name, not the
  kebab-case ID.
- Use `##` sections to organize instructions. The number and depth of
  sections should match the runbook's complexity — no formula here, use
  judgment.
- Content decisions (what sections to include, what patterns to use) are
  made per runbook, not prescribed by this standard.
- Avoid time-sensitive content (hardcoded version numbers, dates,
  release-specific paths) — it goes stale faster than the runbook is
  updated.

### Cross-references

Runbooks follow a **target-based** rule instead of the bundle
Link/Citation split ([cross-references.md](/standards/knowledge-organization/cross-references.md)).
The wrapper records intent: an inline link means "go open this"; inline
code means "this file exists conceptually."

A runbook has **no fixed repo root**. The same skill or agent can run
from a session in any repo's checkout, so there is no stable root for a
`/`-absolute Link to resolve against. A runbook therefore cites a
workspace document by its full `~/workspace/<repo>/…` path even when
that document lives in the same repo as the runbook. When that document
is in the same repo, the citation resolves per
[same-repo resolution](/standards/knowledge-organization/cross-references.md#same-repo-resolution)
— against the reader's own checkout, worktree included, not the main
checkout.

| Target | Style | Example |
|---|---|---|
| File inside the same skill bundle (sibling, `references/`, parent) | Inline link, relative path | `[UI.md](references/UI.md)` |
| File at a stable workspace location | Inline link, absolute `~/workspace/...` path | `[Prose conventions](~/workspace/dev-playbook/standards/prose/conventions.md)` |
| File in the user's repo whose location varies (e.g. `CLAUDE.md`, `specs/design.md`, `Makefile`) | Inline code | `` `CLAUDE.md` `` |
| Directory | Inline code | `` `docs/decisions/` `` |
| Slash-skill invocation | Bare — no markup | `/commit` |

When citing a section of a referenced document, prefer a stable named
anchor over a positional `§x.x` / heading-number — name the concept and
drop the number where the source exposes no stable anchor (see
[Fragment anchors](/standards/knowledge-organization/cross-references.md#fragment-anchors)).

## Skills

A skill is a bundle:

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional — supplementary docs loaded on demand
  scripts/          # optional — helper scripts the skill invokes
```

The directory name must match the `name` field in the front matter.
Where skills live, and how third-party skills are installed, is
[skill-management.md](/standards/harness/skill-management.md)'s concern.

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
edit here before its first use.

- **`user-invocable`** — do not include this field. Upstream defines it
  (`false` hides a skill from the `/` menu, leaving it model-only), but
  `disable-model-invocation` is this workspace's single invocation
  switch, from the opposite angle.

Beyond the shared four:

| Field | Rules |
|-------|-------|
| `disable-model-invocation` | Required. `false` is the standard — per the [dispatch model](/software-factory/factory-operations.md#dispatch), the dispatcher's slash commands arrive as agent text input and count as model invocation. Use `true` only for skills meant for direct user invocation outside the dispatcher. Always explicit — never rely on the default. **Under `true` the description is exactly one sentence** — no model loads it, so it is the one-line summary the user reads in the slash-command list, trigger sentence dropped: `Write the failing tests for a change before any implementation lands.` |
| `allowed-tools` | Pre-approves the listed tools — they run without prompting, while every other tool stays reachable through the normal permission flow. Use for focused, mechanical skills. Format: space-separated tool specs, e.g., `Bash(git *) Bash(gh *)`. |
| `disallowed-tools` | Denies tools outright. Same format as `allowed-tools`. Use it where a read-only stance must be enforced rather than asked for — `issue-review-claims` and `issue-review-simulation` carry `Edit MultiEdit NotebookEdit Write(/**)`, so a write is refused, not merely discouraged. Don't restate a workspace-wide denial from the settings. |
| `arguments` | The skill takes input — one kebab-case name per input. See [Arguments](#arguments). |

One mechanical fact bears on a skill's `model`: **a pinned model only
governs the turn that loads the skill** and reverts to the session model
on the next prompt, so a pin binds a single-turn/batch skill but not an
interactive, multi-turn one — for the latter, only `inherit` reflects
what the interaction actually runs on.

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
Restart Claude Code after edits — the running session caches agent
definitions at startup.

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
edit here before its first use.

Beyond the shared four:

| Field | Rules |
|-------|-------|
| `tools` | A hard allowlist: comma-separated tool names, and the launched agent has exactly these tools. Omit the field and the agent has the full toolset. Not a cognate of a skill's `allowed-tools` — that pre-approves calls inside the caller's permission flow, while `tools` defines the toolset itself, so a tool absent from the list does not exist for the agent. |

### The body is the system prompt

An agent's body is the launched subagent's system prompt, set at
spawn — it addresses the agent that runs it, and nothing else reaches
that agent except the launching prompt. An agent therefore declares no
arguments: its input arrives in the launching prompt, and its report
travels back as the subagent's final message.
