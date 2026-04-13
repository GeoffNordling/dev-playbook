---
name: skill-creator
description: Author a new Claude Code skill following workspace conventions
disable-model-invocation: true
model: opus
effort: high
---

# Skill Creator

Create a new Claude Code skill. The user describes what the skill should do via `$ARGUMENTS`.

## Instructions

Read the [skill authoring standard](~/workspace/dev-playbook/standards/skill-authoring.md) and follow it exactly. That standard defines front matter fields, file structure, naming conventions, model/effort selection, and the checklist to satisfy before shipping.

## Workflow

1. Read the skill authoring standard.
2. Discuss the skill's purpose with the user. Clarify: what does the skill do, who invokes it (user or model), what judgment level is required, and whether it needs arguments or references.
3. Create the skill directory and `SKILL.md` under the appropriate `.claude/skills/` location. If the skill belongs to a specific project, place it there; otherwise use `~/workspace/dev-playbook/dotfiles/.claude/skills/`.
4. Walk the checklist from the standard and confirm each item passes.
5. Run `~/workspace/dev-playbook/dotfiles/bin/sync-dotfiles.sh` if the skill was added to dotfiles.
