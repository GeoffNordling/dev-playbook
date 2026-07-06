---
type: Standard
title: Claude Code Files
description: The registry of repo files the Claude Code harness consumes — each member's role and its content standard
---

# Claude Code Files

The files in a workspace repo that exist for the Claude Code harness —
injected into agent context, read as configuration, or run as code. They
are not concept documents: no OKF frontmatter, exempt from the type-lint.
The concept/harness boundary rule is
[bundle.md](/standards/docs/bundle.md); its code encoding is `classify()`
in [md.py](/src/dev_playbook/md.py).

Claude Code is named deliberately: a different harness would consume a
different file set and would get its own standard.

| Member | Role | Content standard |
|---|---|---|
| `CLAUDE.md`, `<dir>/CLAUDE.md` | injected into every session at or below its directory | [claude-content.md](/standards/claude-code/claude-content.md) |
| skill bundles — `SKILL.md` + `references/`, `scripts/` | loaded when a skill is invoked | [skill-conventions.md](/standards/skill-conventions.md); placement per [skill-management.md](/standards/skill-management.md) |
| `rules/*.md` | injected into every session | none yet |
| `settings.json`, `settings.local.json` | read as configuration | none yet |
| `hooks/` | run as code around harness events | none yet |
| `.claude/workflows/*.js` | run as code by the Workflow tool | none yet |
