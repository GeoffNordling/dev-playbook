---
type: Decision-Record
title: Working Documentation Sets Drain into Permanent Homes
description: A working documentation set's lasting content is promoted in the same pull request that deletes the set, as a Decision Record in the repo the work governs or as a correction to the shared document the run proved wrong, because squash-only merges with head-branch deletion leave a branch-only file nowhere in main's history
date: 2026-09-10
status: accepted
---

# Working Documentation Sets Drain into Permanent Homes

Every governed repo merges squash-only with the head branch deleted
([Repository Settings](/standards/tracking/repo-settings.md#squash-only-merges)),
so a working documentation set that lives on its branch alone leaves no trace
in `main`'s history and appears in no fresh clone once its pull request lands:
the files survive only under GitHub's `refs/pull/N/head`, a GitHub feature
rather than a git one, reachable only by someone holding the pull request
number. The decision: a set's lasting content is distilled and promoted in the
same pull request that deletes the set, so one squashed commit carries both and
git itself records what matters. A promoted item takes one of two homes. A
decision about the repo the work governs becomes a Decision Record in that
repo. A fact the run proved about a shared tool, recipe, standard, or the
factory itself is a correction to that document where it already lives, usually
in dev-playbook; this is the home a drain misses, because the finding does not
look like it belongs to the repo the work was done in.

No new standard is written for it.
[Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
states the end state, and the factory's guides carry the procedure and the
final-review check, per the Standard-versus-Guide line of
[0027](/docs/decisions/0027-registry-refactor-rulings.md).

## Considered Options

- **Rely on `refs/pull/N/head`.** Rejected. It was verified to work: a merged,
  branch-deleted pull request's head ref still fetches, and its commits are
  orphaned from `main`. It is rejected anyway, because recovery needs the pull
  request number and the knowledge that the ref exists, and no procedure in
  this workspace rests on a hosting provider's feature that git does not have.
- **Keep the merged branch.** Rejected. Automatic head-branch deletion is a
  settings row every governed repo carries, and suspending it per branch trades
  a readable branch list for an archive nobody navigates.
- **Land the set under `docs/` unchanged.** Rejected. A set is written
  speculatively, a guess stated as a guess, and `docs/` holds permanent
  documents; promoting a set wholesale would put unreviewed guesses on `main`
  with a permanent document's authority. Distillation to what clears the
  Decision Record bar is the point of the drain, and a drain that promotes
  everything has not been done.
