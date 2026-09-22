---
type: Guide
title: Linking Issues
description: The `gh api` calls that make one issue a sub-issue of another or blocked by another, and read the open ones back — relationships the `gh` CLI has no subcommand for
---

# Linking Issues

Hierarchy and dependency are native GitHub relationships. Neither has a
`gh` subcommand, so both go through `gh api`.

## The database id, not the number

Both write endpoints take the target issue's internal **database id**
rather than its number:

```bash
gh api repos/{owner}/{repo}/issues/<n> --jq .id
```

That id is neither the `#number` nor the `node_id`; passing either fails.

## The parent takes the sub-issue

`gh api --method POST repos/{owner}/{repo}/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`

## The dependent takes the blocker

`gh api --method POST repos/{owner}/{repo}/issues/<dependent>/dependencies/blocked_by -F issue_id=<blocker-db-id>`

## The dependent lists its open blockers

`gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by --jq '.[] | select(.state == "open") | .number'`

## The parent lists its open sub-issues

`gh api repos/{owner}/{repo}/issues/<parent>/sub_issues --jq '.[] | select(.state == "open") | .number'`
