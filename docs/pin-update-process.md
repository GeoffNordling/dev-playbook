---
type: General-Sheet
title: Pin Update Process
description: The one place to learn how a change to dev-playbook main reaches every governed repo — the timer, the update-pins run, the green and red landings, the ledger, the hand tools — with a pointer to where each part is documented in full
---

# Pin Update Process

Every governed repo runs the standards of the dev-playbook commit it pins
in its `.pre-commit-config.yaml`, so a change to dev-playbook `main`
reaches a repo only when that pin moves. This page tells how the pins
move, from the timer to the merged PR, so a reader can follow a run in the
ledger and find the full documentation of each part.

## A timer runs update-pins every 15 minutes

A systemd user timer on the publishing machine starts
[update-pins](/scripts/update-pins) every 15 minutes. Each run takes these
steps:

1. **Sweep.** The run removes every `bump-pin-*` worktree and branch whose
   PR is merged or closed. A branch with an open PR, or with no PR, stays.
2. **Release head.** The run reads the release head: the newest commit on
   dev-playbook `main` that changes a file other than the ledger.
3. **Due repos.** A governed repo with no ledger row at the release head
   is due. A repo with a row, whatever its verdict, waits for the next
   release head. A run with no due repo stops at once; that is the usual
   tick.
4. **Probe.** For each due repo in turn, the run moves the pin in a
   throwaway copy of the repo's `origin/main` and runs the repo's checks
   once.
5. **Green.** Checks that pass land as one commit on the repo's `main`.
6. **Red.** Checks that fail get a worktree on branch `bump-pin-<sha12>`
   and a headless Claude agent in it. The agent runs `/finish-pin-bump`:
   it fixes the findings, opens a PR, and writes each change it must not
   decide into the PR body as a question.
7. **Record.** The run appends one row per repo to the ledger and pushes
   it to dev-playbook `main`.

## The user alone merges a pin PR

No step merges. The agent opens the PR, and the user merges, edits, or
closes it; the next run's sweep then removes its branch.

## The ledger holds the last three release heads

The [Pin Updates Ledger](/docs/pin-updates.md) has one row per repo per
run. Each run drops the rows older than the last three release heads in
the same commit that appends its own, so the full record is in
`git log -p docs/pin-updates.md`.

| Verdict | Meaning |
|---|---|
| `current` | `main` already pinned the release head. |
| `green` | The checks passed, and one commit landed on `main`. |
| `red` | The checks failed, and the agent opened the PR that Landing names. |
| `pending` | A PR for this head was already open, and nothing ran. |
| `failed` | The run could not finish the repo, and Landing gives the reason. |

**Landing** is the commit, the PR, or the failure reason. **Notes** lists
the repo's remote branches not merged to `main`, each with its last date:
`main` moves regardless, and a recent date marks live work the user may
want to check.

## Hand tools cover one repo at a time

- **`update-standards-pin` skill** bumps the repo it runs in. It probes
  with [bump-pin](/scripts/bump-pin), lands a green bump, and cuts the
  `bump-pin-<sha12>` worktree for a red one.
- **`/finish-pin-bump` skill** finishes a red bump in that worktree. It is
  the skill the headless agent runs.
- **`gh pinview <number> <repo>`**, an alias in `~/.config/gh/config.yml`,
  shows a pin PR with its CI result.
- **`journalctl --user -u update-pins.service`** shows each timer run.

## Each part has its full documentation elsewhere

| Part | Where |
|---|---|
| The timer and its service unit | [update-pins periodic job](~/workspace/sysadmin-playbook/docs/periodic-jobs/update-pins.md) in sysadmin-playbook |
| The run, step by step, and its code | the module docstring of [update.py](/src/dev_playbook/pins/update.py), with one module per concern beside it |
| The governed repos | `GOVERNED` in [workspace_lint.py](/src/dev_playbook/workspace_lint.py) |
| The headless agent's prompt | [agent.py](/src/dev_playbook/pins/agent.py) |
| What a headless run costs and loads | [Headless Operation](/docs/headless.md) |
| The skills | [update-standards-pin](/dotfiles/dot-claude/skills/update-standards-pin/SKILL.md) and [finish-pin-bump](/dotfiles/dot-claude/skills/finish-pin-bump/SKILL.md) |
| What a consumer's pin must be | [Distribution Channel](/standards/distribution/channel.md) |
| Each run's findings and agent log | `~/.local/state/dev-playbook/update-pins/<run>/` |
| The GitHub token the agent pushes with | [GitHub credentials](~/workspace/sysadmin-playbook/docs/security/github-credentials.md) in sysadmin-playbook |
