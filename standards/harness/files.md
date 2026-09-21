---
type: Standard-Ruleset
title: Claude Code Files
description: The registry of repo files the Claude Code harness consumes — each member's class, role, and content standard
population: "a file in a governed repo that the Claude Code harness consumes"
---

# Claude Code Files

A file in a governed repo that the Claude Code harness consumes: loaded
as configuration, run as code, or injected into agent context. It
carries no OKF frontmatter and sits outside okf-lint; the
concept/harness boundary is the population of
[Document Types](/standards/knowledge-organization/document-types.md),
and `classify()` in [md.py](/src/dev_playbook/md.py) encodes it. Claude
Code is the only harness in use.

The reasoning behind the rules is the
[Harness Explanation](/standards/harness/explanation.md#which-files-the-harness-consumes).

## Members

Every file the harness consumes is a member of the table below, with
the class the table gives it.

| Member | Class | Role | Content standard |
|---|---|---|---|
| `CLAUDE.md`, `<dir>/CLAUDE.md` | context | injected into every session at or below its directory | [claude-content.md](/standards/harness/claude-content.md) |
| skill bundles | runbook | loaded when a skill is invoked | [runbook-conventions.md](/standards/harness/runbook-conventions.md) |
| `agents/*.md` | runbook | loaded when a typed agent is launched | [runbook-conventions.md](/standards/harness/runbook-conventions.md) |
| `rules/*.md` | context | injected into every session | none yet |
| `settings.json`, `settings.local.json` | configuration | read as configuration | none yet |
| `hooks/` | code | run as code around harness events | none yet |
| `.claude/workflows/*.js` | code | run as code by the Workflow tool | none yet |

`harness.members` · deterministic
