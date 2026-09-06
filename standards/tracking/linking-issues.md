---
type: Guide
title: Linking Issues
description: The `gh api` calls that make one issue a sub-issue of another or blocked by another, and read the open ones back — relationships the `gh` CLI has no subcommand for
---

# Linking Issues

Hierarchy and dependency are native GitHub relationships
([Relationships](/standards/tracking/issue-shapes.md#relationships)).
Neither has a `gh` subcommand, so both go through `gh api`, and both
write endpoints take the target issue's internal **database id** rather
than its number:

```bash
gh api repos/{owner}/{repo}/issues/<n> --jq .id
```

That id is neither the `#number` nor the `node_id`; passing either fails.

- **Sub-issue** —
  `gh api --method POST repos/{owner}/{repo}/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`
- **Blocked-by** —
  `gh api --method POST repos/{owner}/{repo}/issues/<dependent>/dependencies/blocked_by -F issue_id=<blocker-db-id>`
- **Open blockers** —
  `gh api repos/{owner}/{repo}/issues/<n>/dependencies/blocked_by --jq '.[] | select(.state == "open") | .number'`
- **Open sub-issues** —
  `gh api repos/{owner}/{repo}/issues/<parent>/sub_issues --jq '.[] | select(.state == "open") | .number'`
