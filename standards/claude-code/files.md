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
wherever its contents reach a user turn, because the reader sees the marker and
not where it came from. Where the element has to be written about, assemble it
from pieces (`"<command-" + "name>"`) so no single line holds it.

The route that was measured is a **skill body**: the harness records one as a
user turn of text blocks, and the hook reads those in full. Two routes that look
like the same risk are not — an `@`-mentioned file's content is recorded as an
attachment entry, and a tool reading a file back is recorded as a tool result,
and the hook reads neither. A paste does reach a user turn, but whoever can
paste is whoever can type the command. The rule still covers every file type,
because the coverage is cheap and no measurement stays current forever.

`repo-lint`'s `claude-code.command-marker` rule enforces it. Each file is read
to a fixed cap, and one whose first block holds a NUL byte is skipped as binary:
the element cannot hide from a reader inside a generated blob, and only authored
content can be asked to change. Vendored trees are exempt, and that exemption
covers the entire measured vector rather than a corner of it — vendored skills
are stowed live into the skills root, so their bodies reach a user turn exactly
as any other skill's do. They are carried verbatim from upstream and cannot be
edited, so enforcing there would be a red gate on something nobody can fix. It
is an accepted gap, recorded with the mechanism in
[git-authority](/software-factory/git-authority.md).
