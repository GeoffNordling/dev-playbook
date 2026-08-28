---
type: Standard
title: File Roles
description: The role a repository file plays and the content it may hold — rules and procedures across concept documents and harness-owned files
---

# File Roles

Every file in a workspace repository plays one of two roles, and the role
guides what the file holds — so a rule of the system has a home a reader
can find. Which files must exist is
declared once, in the build standard's
[file skeleton](/standards/build/skeleton.md); what goes inside each is
governed by that file's content standard, linked from the skeleton.

## Roles and content

Two axes. **Role** is who consumes the file; **content** is what the file
holds.

**Concept document** — prose a reader loads to *understand* something. It
carries OKF frontmatter (`type` + `title` + `description`, per
[document-types.md](/standards/knowledge-organization/document-types.md))
and is subject to the type-lint.

**Harness-owned file** — a file a tool *consumes as configuration or runs as
code / instructions*: every non-`.md` file, plus the Claude Code file set enumerated in
[the harness-files registry](/standards/harness/files.md). It carries no
OKF frontmatter, is not type-linted, and keeps whatever format its consumer
requires.

**Rule** — a rule of the system: a contract, a state and the moves out
of it, a format, what one part owes another. It binds every actor who
touches the thing, whatever job that actor is doing.

**Procedure** — the steps of one job: what triggers it, what it targets, the
order of the steps, the conditions it branches on, the commands it issues,
when it stops, what it reports. It binds one actor for the length of one
run.

## What each role may hold

The axes are independent:

| | Concept document | Harness-owned file |
|---|---|---|
| **Rule** | Its home — a Standard, a Decision Record, the vocabulary. | Cites the document that owns it; may state what its own run needs but avoid duplication. |
| **Procedure** | A recipe a reader follows — an adoption walkthrough, a migration. | A program the harness runs — a skill body, an agent definition. |

The division is a general aim, not a strict gate: rules live in documents,
procedures live in runbooks, and follow that split where it serves the
reader. A runbook that needs a rule of the system cites the document that
defines it rather than duplicating; the terms, formats,
and states of a runbook's own run are part of the procedure and need no
document.
