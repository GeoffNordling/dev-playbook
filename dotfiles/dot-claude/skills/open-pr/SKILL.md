---
name: open-pr
description: Opens the long-lived PR for an issue once its branch is on origin — idempotent. Use when the issue overwatch reaches a review stop.
disable-model-invocation: false
model: sonnet
effort: low
argument-hint: "<issue-number>"
---

# Open PR

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`, pushed as its commits landed; you create the PR on top of it and touch nothing else.

## Do

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

1. **Confirm the branch on origin matches local.** Compare `git rev-parse issue-<issue>` against `gh api repos/{owner}/{repo}/branches/issue-<issue> --jq .commit.sha`. A 404 means the branch was never pushed; a mismatch means the last push is stale — either way, escalate (§Escalate); don't open a PR over missing or stale work.
2. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. If it lists one, this step already ran (a re-review) — leave it untouched and close (§Close) reporting that PR.
3. **Create it, with an authored merge message.** Synthesize the title and body from the issue brief and its comments (`gh issue view <issue> --json title,body,comments`) and the diff the branch carries (`git diff origin/main...issue-<issue>`), per the [merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe). The body carries the recipe's three mandatory sections:
   - `## Summary` — what changed and why, ending with the mandatory `Closes #<issue>` line — merging the PR closes the issue.
   - `## Deviation ledger` — lift the entries from the issue comment headed `## Deviation ledger`, recorded at build's close; no such comment means `No deviations.` explicitly.
   - `## Deferred` — `Nothing deferred.` explicitly, unless the issue's comments already carry deferred tracker stubs; name each of those by issue link.

   Then `gh pr create --head issue-<issue> --title "<title>" --body "<body>"`, taking the default base branch.

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
