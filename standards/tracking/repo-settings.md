---
type: Standard
title: Repository Settings
description: The GitHub settings every governed repo carries — a GitHub origin, squash-only merges with the PR message format and auto-deleted merged branches, and a default branch protected from destructive operations
population: "a governed repo's GitHub settings: its merge settings and the rules in force on its default branch"
---

# Repository Settings

The GitHub settings every governed repo carries. The merge settings and
the rulesets both sit behind GitHub's all-or-nothing **Administration**
permission, too broad to grant for a one-time toggle, so they are set by
hand and only audited: workspace-lint reads them over `gh api` and
reports drift, and no repair tool exists.

## GitHub origin

The repo's `origin` remote is a GitHub repository. Without one there are
no settings to read; workspace-lint reports the repo and checks nothing
further (`tracking.remote`).

## Squash-only merges

One pull request lands as one commit on `main`, its message from the PR
title and body, and the merged branch is deleted: in **Settings → General
→ Pull Requests**, every row of the table holds (`tracking.settings`).

| Setting | Value |
|---------|-------|
| Allow squash merging | on |
| Default commit message | Pull request title and description |
| Allow merge commits | off |
| Allow rebase merging | off |
| Automatically delete head branches | on |

## Default branch protection

The default branch carries a ruleset named `protect-main`, enforcement
**Active**, an empty bypass list, targeting the default branch, with the
two destructive-operation rules on (`tracking.branch-protection`).

| Rule | Denies |
|---|---|
| Block force pushes | rewriting history under the branch |
| Restrict deletions | removing the branch |

Together these make the branch's history append-only: every commit that
reaches `main` stays reachable, so a mistaken push cannot erase reviewed
work and no recovery depends on someone's local reflog.

Create it at **Settings → Rules → Rulesets → New ruleset → New branch
ruleset**. Every field:

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

Every other rule stays unchecked, and nothing is added to the bypass
list — a bypass actor would return the destructive operations to whoever
holds it, which is the one thing this ruleset exists to deny.

Every field above is audited. workspace-lint reads the rules **in force
on the default branch**: a ruleset that is inactive or aimed elsewhere
supplies no rule to read, which settles enforcement and targeting. It
then reads the ruleset behind each destructive-operation rule and
requires an empty bypass list, with at least one named `protect-main`. A
ruleset it cannot read is reported, not assumed empty.

Extra rules and extra rulesets are fine — the destructive-operation rules
above are a floor.

This is deliberately not [branch protection with required status
checks](/standards/standard/gates.md#a-red-ci-run-is-never-merged):
nothing here makes CI a merge precondition, which stays the user's
standing rule.
