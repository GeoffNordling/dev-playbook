---
name: frozen-open-pr
description: Opens the long-lived PR for an issue once its branch is on origin — the copy frozen for the factory rebuild. Use when the frozen issue overwatch reaches a review stop.
disable-model-invocation: false
model: sonnet
effort: low
argument-hint: "<issue-number>"
---

# Open PR (frozen)

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`, pushed as its commits landed; you create the PR on top of it and touch nothing else.

## Do

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. In the terminal lines, `<node>` is the issue's current `phase:*` label.

1. **Confirm the branch on origin matches local.** Compare `git rev-parse issue-<issue>` against `gh api repos/{owner}/{repo}/branches/issue-<issue> --jq .commit.sha`. A 404 means the branch was never pushed; a mismatch means the last push is stale — either way, escalate (§Escalate); don't open a PR over missing or stale work.
2. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. If it lists one, this step already ran (a re-review) — leave it untouched and close (§Close) reporting that PR.
3. **Create it, with an authored merge message.** Synthesize the title and body to the [merge-message recipe](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#the-merge-message-recipe), which defines the three mandatory sections. Your sources are the issue brief and its comments (`gh issue view <issue> --json title,body,comments`) — the `## Deviation ledger` entries are lifted from the issue comment of that name, recorded at build's close — and the diff the branch carries (`git diff origin/main...issue-<issue>`).

   Stage the body in `/tmp/pr-body-<issue>.md`, then `gh pr create --head issue-<issue>` with that title and `--body-file /tmp/pr-body-<issue>.md`, taking the default base branch. The body is staged outside the repository so the worktree keeps only the deliverable — a stray file at its root turns the next node's `make check` red.

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
