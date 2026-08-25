---
name: grill-with-docs
description: Front door onto a /grilling session run with the /domain-modeling skill. Use when the user wants to stress-test a plan against their project's language and documented decisions, or when intake, design, or ralph-setup reaches its interview beat.
disable-model-invocation: false
model: inherit
effort: xhigh
---

# Grill with Docs

{Run [/grilling](~/.claude/skills/grilling/SKILL.md)}, then {Run [/domain-modeling](~/.claude/skills/domain-modeling/SKILL.md) throughout}. Everything else applies as written.

{Override [/domain-modeling](~/.claude/skills/domain-modeling/SKILL.md) on its `docs/adr/` and "ADR" clause with [Decision Record conventions](~/workspace/dev-playbook/standards/decisions/records.md); this workspace writes **Decision Records** to `docs/decisions/`}. Its `CONTEXT.md` format applies as written.
