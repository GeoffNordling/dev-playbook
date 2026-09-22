---
type: README
title: Dotfiles
description: Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
---

# Dotfiles

Claude Code configuration — skills, rules, settings, and hooks — managed via GNU Stow.

Two packages are stowed into `$HOME`. The `dot-claude/` package is named without a literal `.claude` path segment so Claude Code's hardcoded protected-paths prompt does not fire when editing files under it.

Every machine runs the same configuration; the few hooks that only make sense on one machine detect the host at runtime — see [machines.md](/docs/machines.md).

## Structure

```
dot-claude/          -> ~/.claude/
  agents/        Typed agent definitions
  skills/        Claude Code skills (commit, doc-set audits, tool wrappers, etc.)
  rules/         Global rules applied to every conversation
  hooks/         Claude Code hook scripts
  settings.json  Claude Code settings, shared by every machine (see below)
.bashrc.d/           -> ~/.bashrc.d/
                 Bash snippets sourced by ~/.bashrc (the sync wires up the
                 loader where the distro's stock bashrc has none)
```

The two stowed packages each install into the directory they are named for.
Stow places a package's *contents* in the target, so targeting `$HOME` would
scatter them one level too high — `scripts/sync-dotfiles` holds the mapping.

## Settings

`~/.claude/settings.json` is a stowed symlink to `dot-claude/settings.json`,
and Claude Code writes settings changes through it, so a setting toggled in
a session lands in the main checkout as an ordinary uncommitted edit. Why it
is kept that way, and the one failure mode a session-start hook watches for,
are in
[The Live Settings File Is the Authority](/docs/decisions/0030-the-live-settings-file-is-the-authority.md).

## Workflow

1. Edit files here (never chase symlinks into `~/.claude/`)
2. Run `scripts/sync-dotfiles` after adding or removing files — from the main checkout only; it relinks live `~/.claude`, so it's a step the user runs, never one from a per-issue worktree
3. Edits to existing files take effect immediately (already symlinked); a settings edit loads at the next session start
