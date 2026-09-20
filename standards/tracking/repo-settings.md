---
type: Standard-Ruleset
title: Repository Settings
description: The GitHub settings every governed repo carries — a GitHub origin, squash-only merges with the PR message format and auto-deleted merged branches, and a default branch protected from destructive operations
population: "a governed repo's GitHub settings: its merge settings and the rules in force on its default branch"
---

# Repository Settings

The GitHub settings every governed repo carries.

## GitHub origin

A governed repo's `origin` remote is a repository on github.com.

`tracking.github-origin` · deterministic

## Squash-only merges

A governed repo's GitHub merge settings hold every row of this table:

| Setting | Value |
|---------|-------|
| Allow squash merging | on |
| Default commit message | Pull request title and description |
| Allow merge commits | off |
| Allow rebase merging | off |
| Automatically delete head branches | on |

`tracking.squash-only-merges` · deterministic

## Default branch protection

A governed repo's default branch carries both destructive-operation
rules in force: force pushes are blocked, and deletions are restricted.
Every ruleset supplying one of those two rules has enforcement Active
and an empty bypass list, and at least one of them is named
`protect-main`.

`tracking.default-branch-protection` · deterministic
