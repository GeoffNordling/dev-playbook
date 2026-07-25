---
name: skill-creator
description: Author a new Claude Code skill following workspace conventions
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Skill Creator

Create a new Claude Code skill. The user describes what the skill should do via `$ARGUMENTS`.

## 1. Read the standard

Read [skill-conventions.md](~/workspace/dev-playbook/standards/claude-code/skill-conventions.md) before drafting. The standard is the source of truth for what a valid skill looks like — front matter, file structure, length, naming, references, checklist. This skill is the workflow over those conventions; the conventions live there, not here.

## 2. Gather requirements

Discuss with the user. Ask the questions the standard leaves to choice:

- **Purpose** — what does this skill do? What problem does it solve? What's the success criterion?
- **Use cases** — what specific scenarios should it handle? Any edge cases worth calling out?
- **Invocation mode** — `disable-model-invocation: true` (user-only, slash-command) or `false` (Claude auto-invokes when relevant)?
- **Triggers** (auto-invocable only) — what keywords, contexts, or file types should make Claude reach for it? These go into the description.
- **Model** — ask the user which model the skill runs under (`haiku` / `sonnet` / `opus` / `fable`, or `inherit` to follow the session model); it's their call, not a default you set. The one mechanic to surface when they decide: a pin only governs the turn that loads the skill, so for an interactive, multi-turn skill `inherit` is what honestly reflects the rest of the interaction.
- **Effort** — default to `xhigh` unless the user says otherwise (`low` / `medium` / `high` / `xhigh`).
- **Arguments** — none, single free-form (`$ARGUMENTS`), or positional (`$0`/`$1`/...)?
- **References** — does the body need supporting files under `references/`?
- **Scripts** — does the skill invoke helper scripts that should live under `scripts/` (deterministic ops, repeated logic, places where reliability matters)?
- **Tools** — does this skill need an `allowed-tools` restriction?

## 3. Write the description

The description is the only metadata the model sees when deciding to load an auto-invocable skill. It is the matcher's input, not a comment for humans.

For `disable-model-invocation: false`, both sentences are required:

- First sentence: what the skill does, third person.
- Second sentence: `SHALL` start with `Use when …` and name trigger keywords, contexts, and file types verbatim. Be specific — generic descriptions get matched poorly. The lint (`scripts/skill-lint`) hard-fails on missing `Use when …`.

For `disable-model-invocation: true`, a short third-person label is enough; no triggers needed since the user invokes by name.

See [skill-conventions.md — Required Fields](~/workspace/dev-playbook/standards/claude-code/skill-conventions.md#required-fields) for the format rules and worked examples.

## 4. Decide on bundle layout

Keep `SKILL.md` under ~100 lines. If the body would exceed that, has distinct sub-domains, or contains rarely-needed advanced material, spill into `references/`. References are one level deep — reference files do not link to other reference files.

If the skill needs helper scripts, put them in `scripts/` and reference them with relative links from SKILL.md (`[check.py](scripts/check.py)`). The skill-bundle `scripts/` is distinct from any project-root `scripts/`; both may coexist.

Place the skill bundle in the project's `.claude/skills/` if it's project-local, or in the dotfiles repo's `dotfiles/dot-claude/skills/` for cross-project skills.

## 5. Draft

Write `SKILL.md` and any reference files. Match the workspace conventions exactly. Concrete examples in the body land better than abstract rules — include one wherever it earns its keep.

## 6. Review with the user

Show the draft. Ask:

- Does this cover the use cases you described?
- Anything missing or unclear?
- Should any section be more or less detailed?
- Does the description's `Use when …` clause cover the contexts where you'd want the skill to fire?

Revise based on feedback. Iterate until the user is satisfied.

## 7. Walk the checklist

Walk the checklist in [skill-conventions.md — Checklist](~/workspace/dev-playbook/standards/claude-code/skill-conventions.md#checklist) and confirm each item passes. Fix any failures before considering the skill done.
