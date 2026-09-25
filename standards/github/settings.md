---
type: Standard
title: GitHub Settings
description: The GitHub settings every governed repo carries — a GitHub origin, squash-only merges with the PR message format and auto-deleted merged branches, and a default branch protected from destructive operations
population: "a governed repo's GitHub settings: its origin, its merge settings, and the rules in force on its default branch"
---

# GitHub Settings

The GitHub settings every governed repo carries: predicates over the
repo's state on github.com, which `scripts/workspace-lint` reads over
`gh api` and never writes. How the settings are set is
[Repository Settings](/guides/repo-settings.md).

> **Why.** The merge settings and the rulesets both sit behind
> GitHub's all-or-nothing **Administration** permission, too broad to
> grant for a one-time toggle, so they are set by hand and the
> Standard only reads them.

## Origin on GitHub

A governed repo's `origin` remote is a repository on github.com.

`github.origin-on-github` · deterministic

## Squash-only merges

Each GitHub merge setting of a governed repo has the value this
table gives:

| Setting | Value |
|---------|-------|
| Allow squash merging | on |
| Default commit message | Pull request title and description |
| Allow merge commits | off |
| Allow rebase merging | off |
| Automatically delete head branches | on |

`github.squash-only-merges` · deterministic

> **Why.** The branch's own commits do not survive the squash, so what
> the branch settled survives only in the tree it merges or in the
> pull request's message.

## Default branch protected from destructive operations

The default branch of a governed repo has two rules in force:
force pushes are blocked and deletions are restricted. Each ruleset
that supplies one of these two rules has enforcement Active and an
empty bypass list, and one of those rulesets is named
`protect-main`.

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

`github.default-branch-protected-from-destructive-operations` · deterministic

> **Why.** Together the two rules make the branch's history
> append-only: every commit that reaches the default branch stays
> reachable, so a mistaken push cannot erase reviewed work and no
> recovery depends on someone's local reflog. A bypass actor would
> return the destructive operations to whoever holds it, which is the
> one thing the ruleset exists to deny.
