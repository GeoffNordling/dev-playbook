---
type: Guide
title: Claude Code Files
description: The registry of repo files the Claude Code harness consumes — each member's class, role, and content standard
---

# Claude Code Files

The files in a workspace repo that exist for the Claude Code harness.
They carry no OKF frontmatter and sit outside okf-lint. The
concept/harness boundary is the population of
[Document Types](/standards/knowledge-organization/document-types.md);
its code encoding is `classify()` in [md.py](/src/dev_playbook/md.py).

Claude Code is named deliberately as the only harness currently in use.

Every member has a **class**, naming what the harness does with it:

- **runbook** — documentation that acts, invoked by name; its body is
  governed by the
  [Runbook doc-type](/doc-types/runbook/index.md).
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

Global runbooks live in `dotfiles/dot-claude/skills/` and
`dotfiles/dot-claude/agents/`, stow-linked into `~/.claude/`; repo
runbooks live in the repo's own `.claude/skills/` and `.claude/agents/`.
The layout a runbook takes under those roots is Runbook Conventions'
[Location](/standards/harness/runbook-conventions.md#location).
