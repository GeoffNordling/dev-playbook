---
type: Standard-Ruleset
title: README Content
description: The README content floor — an H1 and a purpose sentence, with no agent instructions, no decisions, and no roster of harness-injected files
population: "a README.md"
---

# README Content

The `README.md` of a repo or a directory, the GitHub-rendered landing
document. Its floor is fixed and its depth grows with the project:
prerequisites, a quick-start, an architecture overview, and examples
arrive as the project earns them.

The reasoning behind the rules is the
[Knowledge Organization Guide](/docs/guides/knowledge-organization.md).

## H1

A `README.md` holds an H1 heading.

`knowledge-organization.h1` · deterministic

## The purpose sentence

A sentence follows the H1 of a `README.md` and says what the repo or
the directory the file introduces holds or is for.

`knowledge-organization.the-purpose-sentence` · stochastic

## No agent instructions or decisions

A `README.md` holds no instruction addressed to an agent and no
architecture decision.

`knowledge-organization.no-agent-instructions-or-decisions` · stochastic

## No roster of harness-injected files

A `README.md` enumerates no skill and no other file the harness injects
into a session.

`knowledge-organization.no-roster-of-harness-injected-files` · stochastic
