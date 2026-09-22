---
type: Guide
title: Repository Settings
description: How the GitHub side of a governed repo is set — the origin, the squash-only merge settings, the protect-main ruleset, the labels bootstrap-labels mints, and where a unit of work lives
---

# Repository Settings

How the GitHub side of a governed repo is set, whether you are creating
the repo or auditing one that exists. The merge settings and the
rulesets both sit behind GitHub's all-or-nothing **Administration**
permission, too broad to grant for a one-time toggle, so those two are
set by hand in the browser; the labels are minted by a script. The
sequence below walks all four settings in order and sends you to the
two tables that carry the values.

## Setting the GitHub side of a repo

Set the four in this order:

1. **Point `origin` at github.com.** Give the repo an `origin` remote
   that is a repository on github.com; everything below is set on that
   repository.
2. **Set the merge settings.** In the repository's settings, give every
   row of [The merge settings](#the-merge-settings) the value that table
   names.
3. **Protect the default branch.** Add the ruleset that
   [The protect-main ruleset](#the-protect-main-ruleset) describes, so
   the default branch carries both destructive-operation rules in force:
   force pushes blocked, deletions restricted. Where another ruleset
   supplies one of those two rules, give it enforcement Active and an
   empty bypass list too.
4. **Mint the labels.** Run
   [`scripts/bootstrap-labels`](/scripts/bootstrap-labels) in the repo.
   It makes the repo's labels exactly the labels declared in the scheme
   data `src/dev_playbook/label_scheme.json`, each carrying the color
   and the description that data gives it
   ([Label Scheme](/standards/tracking/label-scheme.md)). No label names
   a blocked state, because blocked is read from an issue's open
   blockers, and a minted label would drift from the truth the tracker
   already holds.

## The merge settings

| Setting | Value |
|---------|-------|
| Allow squash merging | on |
| Default commit message | Pull request title and description |
| Allow merge commits | off |
| Allow rebase merging | off |
| Automatically delete head branches | on |

The branch's own commits do not survive the squash, so what the branch
settled survives only in the tree it merges or in the pull request's
message — which is why the default commit message is the pull request's
title and description.

## The protect-main ruleset

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

Together the two rules make the branch's history append-only: every
commit that reaches the default branch stays reachable, so a mistaken
push cannot erase reviewed work and no recovery depends on someone's
local reflog.

Add nothing to the bypass list: a bypass actor would return the
destructive operations to whoever holds it, which is the one thing the
ruleset exists to deny.

## Where a unit of work lives

Keep each unit of work in one of two homes, never both: work the repo
has not committed to is an entry in its `CANDIDATES.md`
([Candidates](/standards/tracking/candidates.md)), and work it has
committed to is an issue in the repo's GitHub tracker
([Issue Shapes](/standards/tracking/issue-shapes.md)).
