---
type: Standard
title: Tracker Operations
description: How the GitHub tracker is driven — the `gh` CLI surface, native sub-issues and dependencies, and wayfinding operations
---

# Tracker Operations

How the tracker is driven. Every operation on an issue — create, read, label,
link, close — goes through the `gh` CLI, which infers the repo from the clone it
runs inside. What goes *into* an issue body is
[issue-authoring.md](/standards/tracking/issue-authoring.md); this document
covers the commands that move issues around.

## The issue surface

- **Create** — `gh issue create --title "..." --body "$(cat <<'EOF' … EOF)"`,
  a quoted heredoc so a multi-line body reaches the tracker with its backticks
  and `$` unexpanded.
- **Read** — `gh issue view <n> --comments`. Without the flag the body loads
  alone, the cheaper read when the comment thread is pure archive.
- **List** — `gh issue list --state open --json number,title,labels`, narrowed
  with `--label` and `--state` and shaped with `--jq`.
- **Comment** — `gh issue comment <n> --body "..."`.
- **Label** — `gh issue edit <n> --add-label "..."` / `--remove-label "..."`.
- **Assign** — `gh issue edit <n> --add-assignee @me`.
- **Close** — `gh issue close <n> --comment "..."`.

GitHub shares one number space across issues and pull requests, so a bare `#42`
may be either: `gh pr view 42` resolves it, falling back to `gh issue view 42`.

## Native relationships

Hierarchy (sub-issues) and dependency (blocked-by) are native GitHub
relationships, never body fields and never labels — the rule and its rationale
are in
[issue-authoring.md § Relationships](/standards/tracking/issue-authoring.md#relationships).
Neither has a `gh` subcommand, so both go through `gh api`, and both endpoints
take the target issue's internal **database id** rather than its number:

```bash
gh api repos/{owner}/{repo}/issues/<n> --jq .id
```

That id is neither the `#number` nor the `node_id`; passing either fails.

- **Sub-issue** —
  `gh api --method POST repos/{owner}/{repo}/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`
- **Blocked-by** —
  `gh api --method POST repos/{owner}/{repo}/issues/<dependent>/dependencies/blocked_by -F issue_id=<blocker-db-id>`

GitHub reports live blockers as `issue_dependencies_summary.blocked_by`, which
counts open blockers only. That count is what makes *blocked* a derived state
readable from the tracker rather than a label anyone has to maintain.

## Wayfinding operations

The `/wayfinder` skill drives a **wayfinder map** — a planning epic whose
children are decision tickets — across this same surface. The skill owns the
method; the tracker moves it makes are these.

- **Map** — one issue labelled `wayfinder:map`, created with
  `gh issue create --label wayfinder:map`.
- **Ticket** — a child issue linked to the map as a native sub-issue, labelled
  `wayfinder:<type>` (`research`, `prototype`, `grilling`, or `task`).
- **Ordering** — a ticket that must wait for another is linked blocked-by it.
- **Frontier** — the map's open children, read with
  `gh api repos/{owner}/{repo}/issues/<map>/sub_issues --jq '.[] | select(.state == "open") | .number'`
- **Claim** — `gh issue edit <n> --add-assignee @me`.
- **Resolve** — `gh issue comment <n>` carries the answer and
  `gh issue close <n>` closes the ticket.

## Upstream seed

This document was seeded from
`skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md` in
[mattpocock/skills](https://github.com/mattpocock/skills), pinned at
`2ab958093e83e0ec752e6c1c5932da465bf23e0c`, then adapted to this workspace's
voice and stack. The pin is what a later sweep delta-checks this file against.
