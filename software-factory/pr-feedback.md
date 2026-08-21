---
type: Guide
title: PR Feedback
description: The comment surfaces a pull request carries, threads first, and how a committing node re-enters on a rework lap
---

# PR Feedback

A pull request's feedback is spread across several surfaces, and no single `gh`
command shows them all. This is what a node reads to see the whole of it, and
how a committing node re-enters when that feedback is its work list.

Reading is kept apart from reviewing on purpose: a committing node loads
this only on a rework lap, and never needs the
[review contract](/software-factory/review-contract.md) to learn how to read a
pull request.

## The comment surfaces

**Threads are the primary surface.** Every review finding is a resolvable
inline thread, and a thread carries its own state — open or resolved — which no
other surface does. One GraphQL read returns all of them with that state:

```bash
gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") {
  pullRequest(number:<pr>) { reviewThreads(first:100) { nodes {
    id isResolved isOutdated path line originalLine
    comments(first:10) { nodes { databaseId body } }
  } } } } }'
```

The rest are read for context around the threads:

| Surface | Where it lives |
|---|---|
| The PR body | `gh pr view` |
| Top-level conversation comments | `gh pr view --comments` |
| Review bodies — the cycle headers and the clean dimensions | `gh api repos/{owner}/{repo}/pulls/<pr>/reviews` |

`gh pr view --comments` shows the body and the conversation and omits the other
two, so a read that stops there sees no finding at all.

## Rework re-entry

A committing node checks for an existing PR with `gh pr view`:

- **A PR exists** — review has already run, and the work list is the
  **unresolved Blocking threads**, plus any fix-now items the relaunch prompt
  names. The prompt names each item by thread id; the thread's own content is
  read from GitHub, never pasted into the prompt.
- **No PR** — this is first implementation, and the work list is the issue
  brief alone.

Sequencing is the committing node's own: the prompt carries no ordering.

**The contract wins.** Where a finding merely disagrees with the node's
contract, the contract stands and the finding yields; the node names its own
contract where it cites this. A finding that shows the contract contradicting
reality is different — for a build node that is a deviation, handled under the
[deviation contract](/software-factory/deviation-contract.md).
