---
type: Standard
title: Repository Settings
description: The GitHub settings every governed repo carries — a GitHub origin, squash-only merges with the PR message format and auto-deleted merged branches, and a default branch protected from destructive operations
population: "a governed repo's GitHub settings: its merge settings and the rules in force on its default branch"
---

# Repository Settings

The GitHub settings every governed repo carries.

> **Why.** The merge settings and the rulesets both sit behind
> GitHub's all-or-nothing **Administration** permission, too broad to
> grant for a one-time toggle, so they are set by hand and the
> Standard only audits them.

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

> **Why.** The branch's own commits do not survive the squash, so what
> the branch settled survives only in the tree it merges or in the
> pull request's message.

## Default branch protection

A governed repo's default branch carries both destructive-operation
rules in force: force pushes are blocked, and deletions are restricted.
Every ruleset supplying one of those two rules has enforcement Active
and an empty bypass list, and at least one of them is named
`protect-main`.

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

`tracking.default-branch-protection` · deterministic

> **Why.** Together the two rules make the branch's history
> append-only: every commit that reaches the default branch stays
> reachable, so a mistaken push cannot erase reviewed work and no
> recovery depends on someone's local reflog.
>
> Nothing is added to the bypass list: a bypass actor would return the
> destructive operations to whoever holds it, which is the one thing
> the ruleset exists to deny.
