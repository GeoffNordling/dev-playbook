---
name: open-pr
description: Opens the long-lived PR for an issue once its branch is on origin — idempotent. Use when the software factory reaches a review stop.
model: sonnet
effort: low
---

# Open PR

Ensure the issue's pull request exists, so the review steps that follow have something to comment on. The branch is `issue-<issue>`, pushed as its commits landed; you create the PR on top of it and touch nothing else.

## Do

Your prompt is the issue number; below, `<issue>` is that number.

1. **Skip if the PR already exists.** `gh pr list --head issue-<issue> --state all --json number,state`. {If it lists one, {report that PR} — this step already ran (a re-review)}, leave it untouched, and go to §Close.
2. **Create it, with an authored merge message.** {Read [factory-operations.md's merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe)}, which defines the mandatory sections, and synthesize the title and body to it. Your sources are the issue brief and its comments (`gh issue view <issue> --json title,body,comments`) — the `## Deviation ledger` entries are lifted from the issue comment of that name, recorded at build's close — and the diff the branch carries (`git diff origin/main...issue-<issue>`). `## Suggestion dispositions` has nothing to hold yet: scaffold it as `None.` for the review loop to maintain.

   Write the body to `/tmp/pr-body-<issue>.md` with the Write tool. Then `gh pr create --head issue-<issue>` with that title and `--body-file /tmp/pr-body-<issue>.md`, taking the default base branch.

## Close

End on the report envelope: the session ends with structured output, never a message alone. {Report the PR's number and whether you created it or found it already open}. {If the PR cannot be created at all, {report the reason instead, as escalated}}.
