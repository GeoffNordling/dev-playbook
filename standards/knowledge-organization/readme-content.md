---
type: Standard
title: README Content
description: The README content floor — OKF frontmatter, an H1, and a one-line purpose, with no agent instructions, no decisions, and no roster of harness-injected files
population: "a README.md"
---

# README Content

The `README.md` of a repo or a directory, the GitHub-rendered landing
document. Its floor is fixed and its depth grows with the project:
prerequisites, a quick-start, an architecture overview, and examples
arrive as the project earns them. repo-lint checks the shape
([Knowledge Organization](/standards/knowledge-organization.md)).

## OKF frontmatter

The file opens with `type: README`, `title`, and `description`
([Document Types](/standards/knowledge-organization/document-types.md)).

## H1 and purpose

An H1 follows the frontmatter, then a one-line purpose.

## No agent instructions or decisions

Agent instructions and architecture decisions are absent; they live in
`CLAUDE.md` ([CLAUDE.md Content](/standards/harness/claude-content.md))
and `docs/decisions/`
([Decision Record Conventions](/standards/decisions/records.md)).

## No roster of harness-injected files

The README enumerates no skill and no other file the harness injects
into a session.

Claude Code puts each injected file's name and description into every
session, so a hand-maintained roster duplicates what its reader already
has and rots the moment a skill is added. An inventory of files the
harness does not inject, the executables under `scripts/`, is
legitimate content: nothing else hands the reader that list.
