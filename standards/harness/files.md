---
type: Standard
title: Claude Code Files
description: The registry of repo files the Claude Code harness consumes — each member's class, role, and content standard, and where a runbook sits
population: "a file in a governed repo that the Claude Code harness consumes"
---

# Claude Code Files

A file in a governed repo that the Claude Code harness consumes: loaded
as configuration, run as code, or injected into agent context. It
carries no OKF frontmatter and sits outside the document-type checks; the
concept/harness boundary is the population of
[Document Types](/standards/knowledge-organization/document-types.md),
and `classify()` in [md.py](/src/dev_playbook/md.py) encodes it. Claude
Code is the only harness in use.

## Every harness file matches a member row

Every tracked file under `.claude/` or `dotfiles/dot-claude/` has
one of these paths below that directory: `CLAUDE.md`,
`skills/<name>/` and any file under it, `agents/<name>.md`,
`rules/<name>.md`, `settings.json`, `settings.local.json`,
`hooks/` and any file under it, `workflows/<name>.js`,
`statusline.sh`.

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

`harness.every-harness-file-matches-a-member-row` · deterministic

> **Why.** Claude Code fixes which files it reads; the table is the
> workspace's record of that set, and the predicate holds the repo to
> the table.

## Every runbook at a fixed path

Every directory directly under `.claude/skills/` or
`dotfiles/dot-claude/skills/` has a `SKILL.md`, and has nothing
else in it but `references/`, `scripts/`, and `agents/`. Every
file under `.claude/agents/` or `dotfiles/dot-claude/agents/` is
a `.md` file directly in that directory.

```
<skills root>/<skill-name>/
  SKILL.md          # required
  references/       # optional: docs the skill loads on demand
  scripts/          # optional: helper scripts the skill invokes
  agents/           # optional: agent definitions the skill launches
<agents root>/<agent-name>.md
```

`harness.every-runbook-at-a-fixed-path` · deterministic
