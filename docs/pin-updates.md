---
type: Log
title: Pin Updates Ledger
description: Every run of update-pins, one row per governed repo — when it ran, which release head it moved the pin to, the verdict at that head, where the bump landed, and the remote branches the run saw still unmerged
---

# Pin Updates Ledger

The record of every run of [update-pins](/scripts/update-pins), the command
that moves each governed repo's dev-playbook pin to the release head and
lands the result: one row per repo per run, appended by the command itself
and committed to `main`, so the release history of the workspace reads in
`git log` and in the IDE.

A commit that changes this file and nothing else is not a release. The
release head — the sha consumers pin, and the one `Release head` names —
is the newest commit on `main` that touches any other file, so this
ledger's own bookkeeping never triggers the next run.

## Reading a row

- **Time (UTC)** — when the run started.
- **Release head** — the first twelve characters of the sha the pin moved
  to. A repo is done for a release when it has a row at that head,
  whatever the verdict; update-pins never retries a head by itself.
- **Repo** — the governed repo.
- **Verdict** — one of:
  - `current` — `main` already pinned the release head.
  - `green` — the gate passed at the new pin; one commit landed on `main`.
  - `red` — the gate failed at the new pin; a worktree was cut, a headless
    agent ran `/finish-pin-bump`, and the PR named in Landing is the
    user's to merge or veto.
  - `pending` — a PR for this head was already open on the repo's
    `bump-pin-<sha12>` branch; nothing was run.
  - `failed` — the run could not finish for this repo; Landing says why.
    A red repo whose agent opened no PR keeps its worktree at
    `.claude/worktrees/bump-pin-<sha12>` for the user to read.

  A `bump-pin-<sha12>` worktree and branch live until their PR is merged
  or closed; the next run removes them, worktree, local branch and remote
  branch, and says so on stdout. A branch with no PR, or an open one, is
  kept.
- **Landing** — `main <sha12>` for a landed commit, `PR <url>` for a
  pull request, or the reason for a failure.
- **Notes** — the remote branches not merged to `main` when the run
  looked, each with its last-commit date and how many commits it is
  ahead. `main` is bumped regardless; a branch meets the new pin when it
  merges, and its findings surface then on its own PR. A recent date is a
  live branch whose owner may want to veto; an old one is abandoned.

## Runs

| Time (UTC) | Release head | Repo | Verdict | Landing | Notes |
|---|---|---|---|---|---|
| 2026-09-24 02:38 | c67174ed88eb | sounds | failed | the agent opened no PR; worktree kept at /home/geoff/workspace/sounds/.claude/worktrees/bump-pin-c67174ed88eb, log at /home/geoff/.local/state/dev-playbook/update-pins/20260924T023859Z/sounds.log |  |
| 2026-09-24 02:51 | 38d8585f4785 | sounds | red | PR https://github.com/GeoffNordling/sounds/pull/6 | no unmerged branches |
