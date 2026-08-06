---
type: Guide
title: PR Feedback
description: The comment surfaces a pull request carries, and how a committing node re-enters on a rework lap
---

# PR Feedback

A pull request's feedback is spread across four surfaces, and no single `gh`
command shows them all. This is what a node reads to see the whole of it, and
how a committing node re-enters when that feedback is its work list.

Reading is kept apart from reviewing on purpose: a committing node loads
this only on a rework lap, and never needs the
[review contract](/software-factory/review-contract.md) to learn how to read a
pull request.

## The comment surfaces

All four are read, from human and agent reviewers alike:

| Surface | Where it lives |
|---|---|
| The PR body | `gh pr view` |
| Top-level conversation comments | `gh pr view --comments` |
| Review summary bodies | `gh api repos/{owner}/{repo}/pulls/<pr>/reviews` |
| Inline diff comments | `gh api repos/{owner}/{repo}/pulls/<pr>/comments` |

`gh pr view --comments` shows the body and the conversation and omits the other
two, so the two `gh api` calls carry the rest: a read that stops at
`--comments` misses every inline finding on the diff.

## Rework re-entry

A committing node checks for an existing PR with `gh pr view`:

- **A PR exists** — review has already run, and the complete feedback above is
  the rework work list.
- **No PR** — this is first implementation, and the work list is the issue
  brief alone.

**The contract wins.** Where a finding merely disagrees with the node's
contract, the contract stands and the finding yields; the node names its own
contract where it cites this. A finding that shows the contract contradicting
reality is different — for a build node that is a deviation, handled under the
[deviation contract](/software-factory/deviation-contract.md).
