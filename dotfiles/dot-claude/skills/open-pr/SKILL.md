---
name: open-pr
description: Opens the long-lived PR for an issue once its branch is on origin — idempotent. Use when the issue overwatch reaches a review stop.
disable-model-invocation: false
model: opus
effort: low
disallowed-tools: AskUserQuestion
argument-hint: "<issue-number>"
---

# Open PR

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`; the user pushed it before the review launched. You create the PR — a tap-free `gh` call — but you never push.

## Do

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

1. **Confirm the branch on origin matches local.** Compare `git rev-parse issue-<issue>` against `gh api repos/{owner}/{repo}/branches/issue-<issue> --jq .commit.sha`. A 404 means the branch was never pushed; a mismatch means the last push is stale — either way, escalate (§Escalate); don't open a PR over missing or stale work.
2. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. If it lists one, this step already ran (a re-review) — leave it untouched and close (§Close) reporting that PR.
3. **Create it.** `gh pr create --head issue-<issue> --title "$(gh issue view <issue> --json title -q .title)" --body "Closes #<issue>"`. The `Closes #<issue>` token is mandatory — merging the PR closes the issue. Take the default base branch.

## Close

Emit the terminal line, then stop:

```
DONE: <repo>#<issue> · phase: <node> · PR #<n> open
```

## Escalate

Origin doesn't hold the implementation as committed — the branch was never pushed, or local commits sit ahead of the last push. Emit the terminal line naming which, then stop:

```
ESCALATE: <repo>#<issue> · phase: <node> · branch issue-<issue> <isn't on origin | is stale on origin> — local commits unpushed
```
