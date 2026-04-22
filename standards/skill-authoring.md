# Skill Authoring

Conventions for writing Claude Code skills in this workspace. For the full
feature reference (subagent execution, shell injection, hooks, etc.), see the
[official skill documentation](https://code.claude.com/docs/en/skills).

## File Structure

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional — supplementary docs loaded on demand
```

The directory name must match the `name` field in the front matter.

## Front Matter

```yaml
---
name: <skill-name>
description: <one-line summary>
disable-model-invocation: <true|false>
model: <haiku|sonnet|opus>
effort: <low|medium|high|xhigh>
allowed-tools: <tool spec>          # optional
argument-hint: "<hint>"             # optional
---
```

### Required Fields

Every skill must have all four of these:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case. Must match the directory name. |
| `description` | One-line plain text, under 80 chars. Starts with a verb or noun phrase, no trailing period. |
| `disable-model-invocation` | `true` for skills invoked only by the user. `false` for skills Claude should auto-invoke when relevant. Always explicit — never rely on the default. |
| `effort` | `low`, `medium`, `high`, or `xhigh`. See [Effort Selection](#effort-selection). |

### Optional Fields

| Field | When to include |
|-------|-----------------|
| `model` | Pin the skill to a specific model (`haiku`, `sonnet`, or `opus`). Include when the task's cognitive demand diverges from the session default. Omit to let the skill inherit the session model. See [Model Selection](#model-selection). |
| `allowed-tools` | Restricts which tools the skill can use without prompting. Use for focused, mechanical skills. Format: space-separated tool specs, e.g., `Bash(git *) Bash(gh *)`. |
| `argument-hint` | Short string shown during autocomplete. Brackets for optional args: `"[fast]"`, `"[issue-number-or-url]"`. |

### Fields We Do Not Use

- **`user-invocable`** — do not include this field. If a skill should not be
  user-invoked, use `disable-model-invocation: true` and rely on the skill's
  description to communicate its purpose.

## Model Selection

When authoring a skill, ask the user which model to pin. If the user says
none, omit the `model` field entirely — the skill will inherit the session
model.

## Effort Selection

When authoring a skill, ask the user which effort level to set. Valid values are `low`, `medium`, `high`, or `xhigh`.

## Arguments

Skills receive user input via `$ARGUMENTS` (the full string) or `$0`, `$1`,
etc. (positional access). `$N` is shorthand for `$ARGUMENTS[N]`.

- Use `$ARGUMENTS` when the skill takes a single free-form input.
- Use `$0`, `$1`, etc. when the skill takes distinct positional arguments.

Reference the variable in the body where the skill consumes it:

```markdown
## Feedback: $ARGUMENTS
```

For mode selection:

```markdown
## Mode: $0

### Normal (default)
...

### Fast
...
```

## Body Format

After the front matter, the body is Markdown.

- Start with an `# H1` title. Use the skill's human-readable name, not the
  kebab-case ID.
- Use `##` sections to organize instructions. The number and depth of
  sections should match the skill's complexity — no formula here, use
  judgment.
- Content decisions (what sections to include, what patterns to use) are
  made when authoring each skill, not prescribed by this standard.

## References Directory

For skills that need extensive reference material, place supplementary
files in a `references/` subdirectory. Reference them from SKILL.md:

```markdown
See [UI.md](references/UI.md) for UI element details.
```

The agent loads these on demand rather than paying the context cost upfront.

## Naming Conventions

- **Skill names**: kebab-case, concise, verb-noun or noun when obvious.
  Good: `commit-push`, `ref-check`. Bad: `do-the-commit-and-push-thing`.
- **Skill families**: prefix related skills with a shared namespace.
  Example: `sdd-func-reqs`, `sdd-design`, `sdd-red`, `sdd-green`.
- **Descriptions**: start with a verb or noun phrase, no trailing period.
  Good: `Write tests from spec (red phase)`.

## Checklist

Before shipping a new skill:

- [ ] Directory name matches `name` field
- [ ] All four required front matter fields present
- [ ] Body starts with an `# H1` title
- [ ] Arguments use `$ARGUMENTS` or `$0`/`$1` per the conventions above
