---
type: Standard
title: Skill Conventions
description: Skill-bundle format — frontmatter fields, SKILL.md structure, and directory organization
---

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

A skill bundle is harness-owned — Claude Code loads `SKILL.md` as configuration,
not as prose to learn from — so it is not an OKF concept document. Its front
matter is the Claude Code skill schema below, **not** the OKF `type`/`title`/`description`
profile. See [the OKF bundle boundary](/standards/docs/bundle.md).

```yaml
---
name: <skill-name>
description: <one-line summary>
disable-model-invocation: <true|false>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
allowed-tools: <tool spec>          # optional
argument-hint: "<hint>"             # optional
---
```

### Required fields

Every skill must have all five of these:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case. Must match the directory name. |
| `description` | Plain text, max 1024 chars, third person. First sentence states what the skill does. For skills with `disable-model-invocation: false`, the description `SHALL` include a second sentence beginning `Use when …` that lists the trigger keywords, contexts, or file types verbatim — this is the auto-invocation match surface, so be specific. For `disable-model-invocation: true`, a short label is enough. |
| `disable-model-invocation` | `false` is the standard — per the [dispatch model](/software-factory/software-factory.md#dispatch), the dispatcher's slash commands arrive as agent text input and count as model invocation. Use `true` only for skills meant for direct user invocation outside the dispatcher. Always explicit — never rely on the default. |
| `model` | The model the skill runs under — `haiku`, `sonnet`, `opus`, or `fable` — or `inherit` to follow the session model. Mandatory — always present, never omitted. Which value a skill takes is the author's choice; this standard sets no default. One mechanical fact bears on it: **a pinned model only governs the turn that loads the skill** and reverts to the session model on the next prompt, so a pin binds a single-turn/batch skill but not an interactive, multi-turn one — for the latter, only `inherit` reflects what the interaction actually runs on. |
| `effort` | `low`, `medium`, `high`, or `xhigh`. |

### Optional fields

| Field | When to include |
|-------|-----------------|
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

Skill bundles (`SKILL.md` and any reference files under `.claude/skills/<name>/` or `.agents/skills/<name>/`) are harness-owned, not concept documents, and they follow a **target-based** rule instead of the bundle Link/Citation split ([cross-references.md](/standards/docs/cross-references.md)). The wrapper records intent: an inline link means "go open this"; inline code means "this file exists conceptually."

A skill has **no fixed repo root**. The same skill can be invoked from a session in any repo's checkout, so there is no stable bundle root for a `/`-absolute Link to resolve against. A skill therefore cites a workspace document by its full `~/workspace/<repo>/…` path even when that document lives in the same repo as the skill bundle. When that document is in the same repo, the citation resolves per [same-repo resolution](/standards/docs/cross-references.md#same-repo-resolution) — against the reader's own checkout, worktree included, not the main checkout.

| Target | Style | Example |
|---|---|---|
| File inside the same skill bundle (sibling, `references/`, parent) | Inline link, relative path | `[UI.md](references/UI.md)` |
| File at a stable workspace location | Inline link, absolute `~/workspace/...` path | `[Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md)` |
| File in the human's repo whose location varies (e.g. `CLAUDE.md`, `specs/design.md`, `Makefile`) | Inline code | `` `CLAUDE.md` `` |
| Directory | Inline code | `` `docs/decisions/` `` |
| Slash-skill invocation | Bare — no markup | `/commit` |

When citing a section of a referenced document, prefer a stable named anchor over a positional `§x.x` / heading-number — name the concept and drop the number where the source exposes no stable anchor (see [Fragment anchors](/standards/docs/cross-references.md#fragment-anchors)).

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
  Good: `commit`, `ref-lint`. Bad: `do-the-commit-thing`.
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
- [ ] All five required front matter fields present
- [ ] Description follows the format rules (auto-invocable skills include `Use when …`)
- [ ] Body starts with an `# H1` title
- [ ] SKILL.md under ~100 lines (or content beyond that lives in `references/`)
- [ ] References are one level deep
- [ ] Arguments use `$ARGUMENTS` or `$0`/`$1` per the conventions above
- [ ] No time-sensitive content (versions, dates, release paths)
- [ ] Concrete examples included where the rule benefits from one
- [ ] Terminology consistent throughout the bundle
