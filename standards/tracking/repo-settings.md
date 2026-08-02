---
type: Standard
title: Repository Settings
description: GitHub repository settings every repo should have — squash-only merges, PR message format, auto-deleted merged branches, a default branch protected from destructive operations
---

# Repository Settings

GitHub settings every repository in the workspace `SHALL` have.

## Merge strategy: squash only

In **Settings → General → Pull Requests**:

| Setting | Value |
|---------|-------|
| Allow squash merging | on |
| Default commit message | Pull request title and description |
| Allow merge commits | off |
| Allow rebase merging | off |
| Automatically delete head branches | on |

One pull request lands as one commit on `main`, its message from the PR title and
body. Set these by hand, not by token — the merge settings sit behind GitHub's
all-or-nothing **Administration** permission, too broad to grant for a one-time toggle.

## Default branch: protected from destructive operations

The default branch `SHALL` carry a **ruleset** — **Settings → Rules → Rulesets** —
targeting it with enforcement **Active** and both destructive-operation rules on:

| Rule | Denies |
|---|---|
| Block force pushes | rewriting history under the branch |
| Restrict deletions | removing the branch |

Together these make the branch's history append-only: every commit that reaches
`main` stays reachable, so a mistaken push cannot erase reviewed work and no
recovery depends on someone's local reflog.

The ruleset's name, count, and ref pattern are the repo's own business. The
requirement is on the branch, not on the arrangement: whatever rulesets a repo
keeps, the rules **in force on the default branch** must include these two.
Extra rules are free — this is a floor, not an exact set.

This is deliberately not [branch protection with required status
checks](/standards/build/enforcement.md): nothing here makes CI a merge
precondition, which stays the human's standing rule. It denies only the two
operations that destroy history.
