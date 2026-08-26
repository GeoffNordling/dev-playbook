---
type: Standard
title: Skill Conventions
description: Skill-bundle format — frontmatter fields, SKILL.md structure, and directory organization
---

# Skill Conventions

Conventions for Claude Code skill bundles in this workspace. For the full
feature reference (subagent execution, shell injection, hooks, etc.), see the
[official skill documentation](https://code.claude.com/docs/en/skills).

This standard is binding, and [harness-files-lint](/scripts/harness-files-lint) enforces it at
the commit gate. The craft beside it is the installed `/writing-for-agents`
skill, which covers any document an agent consumes and discloses its
skill-specific half to `SKILL-MECHANICS.md`.
Invoke it when authoring or editing a skill. Where the two collide this
standard wins: it fixes workspace facts the skill has no view on — the closed
frontmatter vocabulary, the always-explicit `disable-model-invocation`, and
the model-invoked description form.

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
profile. See [the two file roles](/standards/knowledge-organization/file-roles.md).

```yaml
---
name: <skill-name>
description: <what it does. Use when …>
disable-model-invocation: <true|false>
model: <haiku|sonnet|opus|fable|inherit>
effort: <low|medium|high|xhigh>
allowed-tools: <tool spec>          # optional
disallowed-tools: <tool spec>       # optional
argument-hint: "<hint>"             # optional
---
```

### Required fields

Every skill must have:

| Field | Rules |
|-------|-------|
| `name` | Kebab-case. Must match the directory name. |
| `description` | Plain text, max 1024 chars, third person. **A model-invoked skill's description is exactly two sentences.** The first states what the skill does; the second `SHALL` begin with the literal words `Use when` and name the trigger keywords, contexts, or file types verbatim — it is the auto-invocation match surface, so be specific. Keep the wording minimal; nothing checks length. Sentences are counted dumbly: `.`, `!`, or `?` ends one when whitespace or the string's end follows, so `CANDIDATES.md` is safe mid-sentence but `e.g.` ends a sentence early. **Under `disable-model-invocation: true` it is exactly one sentence** — no model loads the description, so it is the one-line summary the user reads in the slash-command list, trigger list dropped. |
| `disable-model-invocation` | `false` is the standard — per the [dispatch model](/software-factory/factory-operations.md#dispatch), the dispatcher's slash commands arrive as agent text input and count as model invocation. Use `true` only for skills meant for direct user invocation outside the dispatcher. Always explicit — never rely on the default. |
| `model` | The model the skill runs under — `haiku`, `sonnet`, `opus`, or `fable` — or `inherit` to follow the session model. Mandatory. **The user decides `model` and `effort` explicitly**, never an agent and never a machinery default; `inherit` is a choice like any other. This governs the values persisted here, not a session's runtime pick of a subagent's model. One mechanical fact bears on the choice: **a pinned model only governs the turn that loads the skill** and reverts to the session model on the next prompt, so a pin binds a single-turn/batch skill but not an interactive, multi-turn one — for the latter, only `inherit` reflects what the interaction actually runs on. |
| `effort` | `low`, `medium`, `high`, or `xhigh`. No default — the user's decision, same as `model`. |

### Optional fields

| Field | When to include |
|-------|-----------------|
| `allowed-tools` | Restricts which tools the skill can use without prompting. Use for focused, mechanical skills. Format: space-separated tool specs, e.g., `Bash(git *) Bash(gh *)`. |
| `disallowed-tools` | Denies tools outright. Same format as `allowed-tools`. Use it where a read-only stance must be enforced rather than asked for — `issue-review-claims` and `issue-review-simulation` carry `Edit MultiEdit NotebookEdit Write(/**)`, so a write is refused, not merely discouraged. Don't restate a workspace-wide denial from the settings. |
| `argument-hint` | Short string shown during autocomplete. Brackets for optional args: `"[fast]"`, `"[issue-number-or-url]"`. |

### The vocabulary is closed

These eight fields are the whole vocabulary; a new one requires an edit here
before its first use.

- **`user-invocable`** — do not include this field. To make a skill
  user-invoked only, set `disable-model-invocation: true`; there is no field
  that hides a skill from the user, since model invocation always includes
  user reach.

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

- Start with an `# H1` title. Use the skill's readable name, not the
  kebab-case ID.
- Use `##` sections to organize instructions. The number and depth of
  sections should match the skill's complexity — no formula here, use
  judgment.
- Content decisions (what sections to include, what patterns to use) are
  made per skill, not prescribed by this standard.
- Keep SKILL.md under ~500 lines. When content exceeds that, has distinct
  sub-domains, or contains rarely-needed advanced material, spill into
  `references/` and link from SKILL.md so the agent loads it on demand.
- Avoid time-sensitive content (hardcoded version numbers, dates,
  release-specific paths) — it goes stale faster than the skill is updated.

## Cross-references

Skill bundles (`SKILL.md` and any reference files under `.claude/skills/<name>/` or `.agents/skills/<name>/`) are harness-owned, not concept documents, and they follow a **target-based** rule instead of the bundle Link/Citation split ([cross-references.md](/standards/knowledge-organization/cross-references.md)). The wrapper records intent: an inline link means "go open this"; inline code means "this file exists conceptually."

A skill has **no fixed repo root**. The same skill can be invoked from a session in any repo's checkout, so there is no stable bundle root for a `/`-absolute Link to resolve against. A skill therefore cites a workspace document by its full `~/workspace/<repo>/…` path even when that document lives in the same repo as the skill bundle. When that document is in the same repo, the citation resolves per [same-repo resolution](/standards/knowledge-organization/cross-references.md#same-repo-resolution) — against the reader's own checkout, worktree included, not the main checkout.

| Target | Style | Example |
|---|---|---|
| File inside the same skill bundle (sibling, `references/`, parent) | Inline link, relative path | `[UI.md](references/UI.md)` |
| File at a stable workspace location | Inline link, absolute `~/workspace/...` path | `[Prose conventions](~/workspace/dev-playbook/standards/prose/conventions.md)` |
| File in the user's repo whose location varies (e.g. `CLAUDE.md`, `specs/design.md`, `Makefile`) | Inline code | `` `CLAUDE.md` `` |
| Directory | Inline code | `` `docs/decisions/` `` |
| Slash-skill invocation | Bare — no markup | `/commit` |

When citing a section of a referenced document, prefer a stable named anchor over a positional `§x.x` / heading-number — name the concept and drop the number where the source exposes no stable anchor (see [Fragment anchors](/standards/knowledge-organization/cross-references.md#fragment-anchors)).

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
is governed elsewhere.

## Naming conventions

- **Skill names**: kebab-case, concise, verb-noun or noun when obvious.
  Good: `commit`, `ref-lint`. Bad: `do-the-commit-thing`.
- **Skill families**: prefix related skills with a shared namespace.
  Example: `issue-review-claims`, `issue-review-simulation`.
- **Descriptions**: see the [Required Fields](#required-fields) row for the
  rule. Good: `Write the failing tests for a change before any implementation
  lands. Use when starting the red phase of TDD, when a build leaf carries
  tests:yes, or when the user asks for test-first work.`
  Bad: `A helpful utility that assists with various testing-related tasks and
  workflows. Use when needed.` — the first sentence pads instead of naming
  the job, and the second names no trigger. Under
  `disable-model-invocation: true` that first sentence stands alone: `Write
  the failing tests for a change before any implementation lands.`

## Checklist

Before shipping a new skill:

- [ ] Directory name matches `name` field
- [ ] All required front matter fields present
- [ ] Description is exactly two sentences, the second beginning `Use when …`
      — or, under `disable-model-invocation: true`, exactly one sentence
- [ ] Body starts with an `# H1` title
- [ ] SKILL.md under ~500 lines (or content beyond that lives in `references/`)
- [ ] References are one level deep
- [ ] Arguments use `$ARGUMENTS` or `$0`/`$1` per the conventions above
- [ ] No time-sensitive content (versions, dates, release paths)
- [ ] Concrete examples included where the rule benefits from one
- [ ] Terminology consistent throughout the bundle
