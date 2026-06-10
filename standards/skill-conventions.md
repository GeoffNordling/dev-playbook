# Skill Conventions

Conventions for Claude Code skill bundles in this workspace. For the full
feature reference (subagent execution, shell injection, hooks, etc.), see the
[official skill documentation](https://code.claude.com/docs/en/skills).

## File structure

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional — supplementary docs loaded on demand
  scripts/          # optional — helper scripts the skill invokes
```

The directory name must match the `name` field in the front matter.

## Front matter

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

### Required fields

Every skill must have all four of these:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case. Must match the directory name. |
| `description` | Plain text, max 1024 chars, third person. First sentence states what the skill does. For skills with `disable-model-invocation: false`, the description `SHALL` include a second sentence beginning `Use when …` that lists the trigger keywords, contexts, or file types verbatim — this is the auto-invocation match surface, so be specific. For `disable-model-invocation: true`, a short label is enough. |
| `disable-model-invocation` | `false` is the standard — per the [dispatch model](~/workspace/dev-playbook/workflow/workflow.md#dispatch), the dispatcher's slash commands arrive as agent text input and count as model invocation. Use `true` only for skills meant for direct user invocation outside the dispatcher. Always explicit — never rely on the default. |
| `effort` | `low`, `medium`, `high`, or `xhigh`. |

### Optional fields

| Field | When to include |
|-------|-----------------|
| `model` | Pin the skill to a specific model (`haiku`, `sonnet`, or `opus`). Optional — without the pin, the session model wins. Pin `sonnet`/`haiku` where a cheaper, faster model fits the work. The `opus` pins are deliberately absent *for now*: omitting them lets sessions default to Fable while Anthropic still allows it under subscription billing. That's temporary, not the long-term posture — when Fable leaves subscription usage, the `opus` pins come back (dev-playbook#90). |
| `allowed-tools` | Restricts which tools the skill can use without prompting. Use for focused, mechanical skills. Format: space-separated tool specs, e.g., `Bash(git *) Bash(gh *)`. |
| `argument-hint` | Short string shown during autocomplete. Brackets for optional args: `"[fast]"`, `"[issue-number-or-url]"`. |

### Fields we do not use

- **`user-invocable`** — do not include this field. If a skill should not be
  user-invoked, use `disable-model-invocation: true` and rely on the skill's
  description to communicate its purpose.

## Arguments

Skills receive user input via `$ARGUMENTS` (the full string) or `$0`, `$1`,
etc. (positional access). `$N` is shorthand for `$ARGUMENTS[N]`.

- Use `$ARGUMENTS` when the skill takes a single free-form input.
- Use `$0`, `$1`, etc. when the skill takes distinct positional arguments.

Reference the variable in the body where the skill consumes it:

```markdown
## Feedback: $ARGUMENTS
```

## Body format

After the front matter, the body is Markdown.

- Start with an `# H1` title. Use the skill's human-readable name, not the
  kebab-case ID.
- Use `##` sections to organize instructions. The number and depth of
  sections should match the skill's complexity — no formula here, use
  judgment.
- Content decisions (what sections to include, what patterns to use) are
  made per skill, not prescribed by this standard.
- Keep SKILL.md under ~100 lines. When content exceeds that, has distinct
  sub-domains, or contains rarely-needed advanced material, spill into
  `references/` and link from SKILL.md so the agent loads it on demand.
- Avoid time-sensitive content (hardcoded version numbers, dates,
  release-specific paths) — it goes stale faster than the skill is updated.

## Cross-references

Skill bodies follow the workspace cross-reference standard. See the [skill-bundles section](~/workspace/dev-playbook/standards/repo-documentation.md#in-skill-bundles) for the target-based rules: inline links for files the reader should open, inline code for files mentioned by name, and bare invocations for slash-skills.

## References directory

For skills that need extensive reference material, place supplementary
files in a `references/` subdirectory. Reference them from SKILL.md per
the cross-reference rule above:

```markdown
See [UI.md](references/UI.md) for UI element details.
```

The agent loads these on demand rather than paying the context cost upfront.

References are one level deep: files in `references/` `SHALL NOT` link to
other reference files in the same skill bundle. The lazy-load pattern
assumes a flat tree; nested references defeat the savings and confuse the
loading agent.

## Scripts directory

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
is governed elsewhere. The two may coexist in the same repo without
conflict; they are different paths and different concerns.

## Naming conventions

- **Skill names**: kebab-case, concise, verb-noun or noun when obvious.
  Good: `commit`, `ref-check`. Bad: `do-the-commit-thing`.
- **Skill families**: prefix related skills with a shared namespace.
  Example: `sdd-func-reqs`, `sdd-design`, `sdd-red`, `sdd-green`.
- **Descriptions**: see the [Required Fields](#required-fields) row for
  format. Examples — good (auto-invocable):
  `Write tests from a spec item before any implementation lands. Use when
  starting the red phase of TDD, when a spec~* item has no covering tests,
  or when the user asks for "spec-first" tests.` Good (user-only):
  `Author a new Claude Code skill following workspace conventions`.
  Bad (no triggers, generic): `Helps with tests`.

## Checklist

Before shipping a new skill:

- [ ] Directory name matches `name` field
- [ ] All four required front matter fields present
- [ ] Description follows the format rules (auto-invocable skills include `Use when …`)
- [ ] Body starts with an `# H1` title
- [ ] SKILL.md under ~100 lines (or content beyond that lives in `references/`)
- [ ] References are one level deep
- [ ] Arguments use `$ARGUMENTS` or `$0`/`$1` per the conventions above
- [ ] No time-sensitive content (versions, dates, release paths)
- [ ] Concrete examples included where the rule benefits from one
- [ ] Terminology consistent throughout the bundle
