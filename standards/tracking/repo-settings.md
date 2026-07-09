---
type: Standard
title: Repository Settings
description: GitHub repository settings every repo should have — squash-only merges, PR message format, auto-deleted merged branches
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
