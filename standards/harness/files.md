---
type: Standard
title: Claude Code Files
description: The registry of repo files the Claude Code harness consumes — each member's class, role, layout, and content standard
---

# Claude Code Files

The files in a workspace repo that exist for the Claude Code harness.
They carry no OKF frontmatter and sit outside the type-lint. The
concept/harness boundary rule is [file-roles.md](/standards/knowledge-organization/file-roles.md);
its code encoding is `classify()` in [md.py](/src/dev_playbook/md.py).

Claude Code is named deliberately as the only harness currently in use.

Every member has a **class**, naming what the harness does with it:

- **runbook** — documentation that acts, invoked by name; its body is
  governed by the [Instruction Grammar](/standards/harness/grammar.md).
- **context** — prose injected into agent context; read, never invoked.
- **configuration** — data the harness reads.
- **code** — deterministic programs the harness runs.

| Member | Class | Role | Content standard |
|---|---|---|---|
| `CLAUDE.md`, `<dir>/CLAUDE.md` | context | injected into every session at or below its directory | [claude-content.md](/standards/harness/claude-content.md) |
| skill bundles | runbook | loaded when a skill is invoked | [runbook-conventions.md](/standards/harness/runbook-conventions.md) |
| `agents/*.md` | runbook | loaded when a typed agent is launched | [runbook-conventions.md](/standards/harness/runbook-conventions.md) |
| `rules/*.md` | context | injected into every session | none yet |
| `settings.json`, `settings.local.json` | configuration | read as configuration | none yet |
| `hooks/` | code | run as code around harness events | none yet |
| `.claude/workflows/*.js` | code | run as code by the Workflow tool | none yet |

## Runbook layout

A skill is a bundle; an agent is one flat file:

```
.claude/skills/<skill-name>/
  SKILL.md          # required
  references/       # optional — docs the skill loads on demand
  scripts/          # optional — helper scripts the skill invokes
.claude/agents/<agent-name>.md
```

Global runbooks live in `dotfiles/dot-claude/skills/` and
`dotfiles/dot-claude/agents/`, stow-linked into `~/.claude/`; repo
runbooks live in the repo's own `.claude/skills/` and `.claude/agents/`.
