---
type: Guide
title: Fedora Test Instructions
description: Temporary — how the agent on the Fedora primary installs and verifies the cross-machine-sync branch, and reports back
---

# Fedora test instructions

**Temporary file.** It is deleted before `cross-machine-sync` merges. If you are
reading this on `main`, it has outlived its purpose — say so and stop.

You are the agent on the **Fedora primary machine**. The `cross-machine-sync`
branch reworks how this machine's Claude Code configuration is installed, and it
has been verified on a WSL secondary only. Your job is to run it here and report
what happened. The author is at the keyboard.

## Rules

1. **Do not merge, and do not push to `main`.** Not part of this task.
2. **Do not fix what breaks.** If a step fails, stop and report it. This is a
   live `$HOME` and an improvised repair is worse than a failed test.
3. **Commit only the results file** named in step 6, and only on
   `cross-machine-sync`.
4. **Record every command's actual output.** The author cannot copy text between
   machines, so the results file is the only channel back.

## What is being tested

`~/.claude/settings.json` stops being a symlink and becomes generated — merged
from `dotfiles/settings/base.json` plus `dotfiles/settings/fedora.json`, because
Claude Code reads one user-scope settings file and offers no override layer to
hold the Fedora-only sound hook and sandbox block. The stow invocation is also
fixed: it had been targeting `$HOME` for packages whose contents belong one
level down, which scatters files into `$HOME` and leaves `~/.bashrc.d`
uncreated. Expect to find that wreckage here.

## Step 1 — diagnose, before touching anything

Read-only. Record all of it.

```bash
ls -la ~/aliases.sh ~/worktree.sh ~/skills ~/.skill-lock.json ~/sync-dotfiles.sh 2>&1
ls -ld ~/.bashrc.d ~/.agents ~/bin ~/.claude 2>&1
ls -l ~/.claude/settings.json
git -C ~/workspace/dev-playbook status --short
git -C ~/workspace/dev-playbook branch --show-current
```

Files loose in `$HOME` are the stow bug's output. A missing `~/.bashrc.d` is the
same bug seen from the other side.

**Stop and report if `git status` shows uncommitted work.** That is this
machine's own work and it is not yours to stash or discard.

## Step 2 — remove the misplaced links, before checking out

Order matters: this unstows using the *old* package list, and one of those
packages (`bin`) does not exist on the branch.

Run this only for the paths step 1 actually found:

```bash
stow -D -d ~/workspace/dev-playbook/dotfiles -t ~ .agents .bashrc.d bin
```

Nothing to remove is a fine outcome — record what it printed either way. A
complaint that a link is "not owned by stow" is not a failure here; note it and
continue.

## Step 3 — check out the branch

```bash
git -C ~/workspace/dev-playbook fetch origin
git -C ~/workspace/dev-playbook checkout cross-machine-sync
```

The fetch needs the author's YubiKey — hand them the command rather than running
it yourself if it stalls.

This checkout deletes `dotfiles/dot-claude/settings.json` and renames a hook, so
some `~/.claude` symlinks go broken the moment it lands. That is expected and
step 4 repairs it. **Do not stop between step 3 and step 4** — a half-installed
configuration is the one state worth avoiding.

## Step 4 — install

```bash
~/workspace/dev-playbook/scripts/sync-dotfiles
```

Then run it a second time. It is idempotent: the second run must print
`settings already current (fedora)` and must not report new work.

## Step 5 — verify

```bash
~/workspace/dev-playbook/scripts/sync-dotfiles --check ; echo "check exit=$?"
ls -ld ~/.bashrc.d ~/.agents ~/.claude
ls ~/.bashrc.d/
ls -l ~/.claude/settings.json
ls -l ~/.claude/hooks/
ls ~/aliases.sh ~/worktree.sh ~/skills ~/sync-dotfiles.sh 2>&1
grep -c '"sandbox"' ~/.claude/settings.json
bash ~/.claude/hooks/session-start-settings </dev/null ; echo "settings hook exit=$?"
bash ~/.claude/hooks/session-start-stale-base </dev/null ; echo "stale-base hook exit=$?"
```

Passing looks like:

- `--check` exits 0 and prints nothing.
- `~/.bashrc.d`, `~/.agents`, `~/.claude` are all real directories.
- `~/.bashrc.d/` holds `aliases.sh`, `machine-env.sh`, `worktree.sh`.
- `~/.claude/settings.json` is a **regular file**, not a symlink.
- `~/.claude/hooks/` holds `session-start-settings` and
  `session-start-stale-base`, and no `session-start-sync`.
- The four `$HOME` paths in the last `ls` are all "No such file or directory".
- `grep -c` returns 1 — Fedora's fragment carries the sandbox block, which is
  the whole reason the file is generated per machine.
- Both hooks exit 0 and print nothing.

`~/bin` is deliberately gone; that package was retired. If a broken
`~/bin/sync-dotfiles.sh` survives, remove it and note that you did.

Then open a **new terminal** and run:

```bash
echo "SKIP=$SKIP JUDGMENTS=$SKIP_JUDGMENTS"
alias work
```

On Fedora both variables must be **empty** — the skips exist only on a
secondary, and every detector is expected to run here. `work` must resolve to
`cd "$HOME/workspace"`.

## Step 6 — report back

Write `FEDORA-TEST-RESULTS.md` at the repo root. Include, for every step: the
command, its actual output, and whether it matched what this file predicted.
Quote real terminal output — do not summarize it and do not tidy it up. A
prediction this file got wrong is the single most valuable thing you can return,
so give those the most space.

Then, on `cross-machine-sync`:

```bash
git -C ~/workspace/dev-playbook add FEDORA-TEST-RESULTS.md
git -C ~/workspace/dev-playbook commit -m "Fedora test results"
```

The push is over SSH and needs the author's YubiKey. Give them this line and let
them run it:

```bash
git -C ~/workspace/dev-playbook push
```

If the commit gate blocks the commit, that is itself a finding — report the
findings verbatim in the results file and use `--no-verify` for this one commit,
noting that you did.
