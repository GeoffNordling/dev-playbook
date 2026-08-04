---
name: open-pr
description: Opens the long-lived PR for an issue once its branch is on origin — idempotent. Use when the issue overwatch reaches a review stop.
disable-model-invocation: false
model: sonnet
effort: low
argument-hint: "<issue-number>"
---

# Open PR

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`, pushed by the committing node that ran before this one. This skill only reads and creates the PR; it does not push. If the branch isn't on origin, that is the previous node's work missing, so escalate rather than pushing it here.

## Do

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

1. **Confirm the branch on origin matches local.** Compare `git rev-parse issue-<issue>` against `gh api repos/{owner}/{repo}/branches/issue-<issue> --jq .commit.sha`. A 404 means the branch was never pushed; a mismatch means the last push is stale — either way, escalate (§Escalate); don't open a PR over missing or stale work.
2. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. If it lists one, this step already ran (a re-review) — leave it untouched and close (§Close) reporting that PR.
3. **Create it, with an authored merge message.** Synthesize the title and body from the issue brief (`gh issue view <issue> --json title,body`) and the diff the branch carries (`git diff origin/main...issue-<issue>`), per the [merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe). The body ends with the mandatory `Closes #<issue>` line — merging the PR closes the issue. Then `gh pr create --head issue-<issue> --title "<title>" --body "<body>"`, taking the default base branch.

## Close

Emit the terminal line, then stop:

```
DONE: <repo>#<issue> · phase: <node> · PR #<n> open
```

## Escalate

Origin doesn't hold the implementation as committed — the branch was never pushed, or local commits sit ahead of the last push. Either way the committing node left work behind, which is its problem to fix and not this skill's to paper over. Emit the terminal line naming which, then stop:

```
ESCALATE: <repo>#<issue> · phase: <node> · branch issue-<issue> <isn't on origin | is stale on origin> — local commits unpushed
```
