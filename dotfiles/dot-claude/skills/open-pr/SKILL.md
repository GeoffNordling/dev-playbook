---
name: open-pr
description: Open the long-lived PR for an issue once its branch is on origin — idempotent, the first step of the code-review goal. Use when the agents dashboard launches the code-review phase.
disable-model-invocation: false
model: opus
effort: low
disallowed-tools: AskUserQuestion
argument-hint: "<issue-number>"
---

# Open PR

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`; the user pushed it before launching this phase. You create the PR — a tap-free `gh` call — but you never push.

## Do

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

1. **Confirm the branch reached origin.** `gh api repos/{owner}/{repo}/branches/issue-<issue>`. A 404 means the user hasn't pushed yet — escalate (§Escalate); don't try to create a PR over a missing branch.
2. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. If it lists one, this phase has already run (a re-review) — leave it untouched and stop.
3. **Create it.** `gh pr create --head issue-<issue> --title "$(gh issue view <issue> --json title -q .title)" --body "Closes #<issue>"`. The `Closes #<issue>` token is mandatory — merging the PR closes the issue. Take the default base branch.

This phase opens nothing else and advances no label — the review steps that follow in the same goal do that. On success, finish without a terminal line so the goal proceeds to them.

## Escalate

The branch isn't on origin — the implementation is committed but unpushed. Print and stop:

```
ESCALATE: #<issue> — branch issue-<issue> isn't on origin (needs pushing before the PR can open)
```
