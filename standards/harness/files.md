---
type: Standard
title: Claude Code Files
description: The repo files the Claude Code harness consumes — every tracked file under a harness root a registered member, and where a runbook sits
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

The members are the rows of the
[Harness File Registry](/registries/harness-files.md#members).

`harness.every-harness-file-matches-a-member-row` · deterministic

> **Why.** Claude Code fixes which files it reads; the Harness File
> Registry is the workspace's record of that set, and the
> predicate holds the repo to the table.

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
