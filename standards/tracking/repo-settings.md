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

The default branch `SHALL` carry a **ruleset** targeting it with enforcement
**Active** and both destructive-operation rules on:

| Rule | Denies |
|---|---|
| Block force pushes | rewriting history under the branch |
| Restrict deletions | removing the branch |

Together these make the branch's history append-only: every commit that reaches
`main` stays reachable, so a mistaken push cannot erase reviewed work and no
recovery depends on someone's local reflog.

### The canonical ruleset

Create it at **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
Rulesets sit behind the same all-or-nothing **Administration** permission as the
merge settings, so this too is set by hand, not by token. Every field:

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

Every other rule stays unchecked, and nothing is added to the bypass list — a
bypass actor would return the two destructive operations to whoever holds it,
which is the one thing this ruleset exists to deny.

Every field above is audited. workspace-lint reads the rules **in force on the
default branch**: a ruleset that is inactive or aimed elsewhere supplies no
rule to read, which settles enforcement and targeting. It then reads the
ruleset behind each of the two rules and requires an empty bypass list, with at
least one named `protect-main`. A ruleset it cannot read is reported, not
assumed empty.

Extra rules and extra rulesets are fine — the two above are a floor.

This is deliberately not [branch protection with required status
checks](/standards/build/enforcement.md): nothing here makes CI a merge
precondition, which stays the user's standing rule. It denies only the two
operations that destroy history.
