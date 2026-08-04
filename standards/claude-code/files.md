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
| skill bundles — `SKILL.md` + `references/`, `scripts/` | loaded when a skill is invoked | [skill-conventions.md](/standards/claude-code/skill-conventions.md); placement per [skill-management.md](/standards/claude-code/skill-management.md) |
| `rules/*.md` | injected into every session | none yet |
| `settings.json`, `settings.local.json` | read as configuration | none yet |
| `hooks/` | run as code around harness events | none yet |
| `.claude/workflows/*.js` | run as code by the Workflow tool | none yet |
| `agents/*.md` | read at session start as the subagent spawn registry; each file a named agent definition (frontmatter identity + standing system prompt) | none yet |

## No file carries a command marker

The harness writes a `<command-name>` element into the transcript when the user
types a slash command. It is the harness's own record of who acted, and tooling
reads it as exactly that — the `git-authority` hook reads one to decide whether a
session may commit.

**No file in a repo may contain that element whole**, in any file type: prose,
fixtures, test data, configuration. A file that carries one is a forged record
the moment anything puts its contents into a turn — an `@`-mention, a paste, a
tool that reads the file back — because the reader sees the marker and not where
it came from. Where the element has to be written about, assemble it from
pieces (`"<command-" + "name>"`) so no single line holds it.

`repo-lint`'s `claude-code.command-marker` rule enforces this over every file in
the checkout. Vendored trees are exempt: their contents are carried verbatim
from upstream and cannot be edited, so a hit there would be a red gate on
something nobody can fix.
