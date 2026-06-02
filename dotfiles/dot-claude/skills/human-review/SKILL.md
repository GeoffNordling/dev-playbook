---
name: human-review
description: Administrative wrapper for any human-review phase — reads the workflow graph, locates the issue by its phase label, and carries out the human's verdict (advance, merge, or route back) along the edge the graph defines. The human reviews in their own tools; this handles the transition bookkeeping and answers questions. Use when the agents dashboard launches a human-review phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue view *) Bash(gh issue edit *) Bash(gh issue comment *) Bash(gh pr view *) Bash(gh pr diff *) Bash(git worktree *) Bash(git branch *) AskUserQuestion
argument-hint: "<issue-number>"
---

# Human Review

One skill for every human-review phase in the workflow. The human does the reviewing — spec and code in VS Code, issue and PR on GitHub. You are a thin wrapper: you hold the whole graph in mind, you answer questions when asked, and you carry out the human's verdict — the transitions they would otherwise make by hand. The verdict is always the human's; you never approve, merge, or route on your own judgment.

## Read first

Before doing anything else, read end-to-end:

- [workflow standard](~/workspace/dev-playbook/workflow/workflow.md) — the state-machine graph: every node, the edges out of each, the verdict labels on the human-review edges, and what a transition does to an issue's labels and PR.

Then report: `READ: workflow.md`. Proceed only after.

## 1. Place the issue

`$ARGUMENTS` is the issue number; below, `<issue>` is that number. Read its labels (`gh issue view <issue>`) and place its `phase:*` node in the graph. It should be a human-review node; its outgoing edges are the verdicts open to the human. If it isn't, you were launched on the wrong issue — say so and stop. (You run from the main checkout, not the issue's worktree, so name the branch when you reach for its artifacts: `gh pr view issue-<issue>`, `gh pr diff issue-<issue>`, and read spec files at `.claude/worktrees/issue-<issue>/`.)

## 2. Stand by

Tell the human, in one line, which review this is and the verdicts the graph gives it — then wait; they review the artifact in their own tools. Don't dump diffs, specs, or findings to the terminal. When a question needs it, read what the prior agent review left — findings on the issue before a PR exists, on the PR once it does — or the artifact itself, and answer concisely. If something the graph says should be there is missing, tell the human; something upstream didn't run.

## 3. Carry out the verdict

On the human's word, follow the edge they chose and make the transition the graph defines for it — the `phase:*` label change, and whatever that edge implies for the PR. On a reject, first record the human's reason so the next agent reads it. Where a verdict has more than one possible target, the issue's other labels disambiguate per the graph's routing.

The commands these draw on, reached for as the chosen edge needs them:

- **Move the phase** — `gh issue edit <issue> --remove-label "phase:<from>" --add-label "phase:<to>"`.
- **Record a reject reason** — `gh issue comment <issue> --body "<the human's reason>"`.
- **Merge** (the `approve: merge` edge) — the human squash-merges in the GitHub UI; you can't (the PAT can't merge). Their merge drops the origin branch and closes the issue via the PR's `Closes #<issue>`, so no label change follows. Once they confirm it's merged, tear down the local side: `git worktree remove .claude/worktrees/issue-<issue>` and `git branch -D issue-<issue>`.

## 4. Close

Report what you did — the verdict, the transition, and the issue's new state. The human's review runs alongside them, so there is no terminal `DONE:` line and nothing to escalate.
