---
type: Registry
title: Harness File Registry
description: Every kind of file the Claude Code harness consumes, each with its class, its role, and the Standard its content follows
---

# Harness File Registry

The files the Claude Code harness consumes, by path below a harness
root, `.claude/` or `dotfiles/dot-claude/`. They carry no frontmatter,
so no OKF type names them. The rule
[Every harness file is a registered member](/standards/harness/files.md#every-harness-file-is-a-registered-member)
holds each tracked file under a harness root to a row here. Which
members a doc-type covers is the
[Doc-Type Registry](/registries/doc-types.md).

## Members

| Member | Class | Role | Content standard |
|---|---|---|---|
| `CLAUDE.md`, `<dir>/CLAUDE.md` | context | injected into every session at or below its directory | [claude-content.md](/standards/harness/claude-content.md) |
| skill bundles | runbook | loaded when a skill is invoked | [Runbook Conventions](/standards/doc-type/runbook-conventions.md) |
| `agents/*.md` | runbook | loaded when a typed agent is launched | [Runbook Conventions](/standards/doc-type/runbook-conventions.md) |
| `rules/*.md` | context | injected into every session | none yet |
| `settings.json`, `settings.local.json` | configuration | read as configuration | none yet |
| `hooks/` | code | run as code around harness events | none yet |
| `workflows/*.js` | code | run as code by the Workflow tool | none yet |
| `statusline.sh` | code | run as code to draw the status line | none yet |
