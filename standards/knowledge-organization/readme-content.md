---
type: Standard
title: README Content
description: The README content floor — an H1 and a purpose sentence, with no agent instructions, no decisions, and no roster of harness-injected files
population: "a README.md"
---

# README Content

The `README.md` of a repo or a directory, the GitHub-rendered landing
document. Its floor is fixed and its depth grows with the project:
prerequisites, a quick-start, an architecture overview, and examples
arrive as the project earns them.

## README holds an H1

Every `README.md` has an H1.

`knowledge-organization.readme-holds-an-h1` · deterministic

## Purpose sentence follows the H1

A sentence follows the H1 of a `README.md` and says what the repo or
the directory the file introduces holds or is for.

`knowledge-organization.purpose-sentence-follows-the-h1` · stochastic

## No agent instructions or architecture decisions

A `README.md` holds no instruction addressed to an agent and no
architecture decision.

`knowledge-organization.no-agent-instructions-or-architecture-decisions` · stochastic

## No roster of harness-injected files

A `README.md` enumerates no skill and no other file the harness injects
into a session.

`knowledge-organization.no-roster-of-harness-injected-files` · stochastic

> **Why.** Claude Code puts each injected file's name and description
> into every session, so a hand-maintained roster of skills duplicates
> what its reader already has and rots the moment a skill is added. An
> inventory of files the harness does not inject, the executables
> under `scripts/`, is different: nothing else hands the reader that
> list.
