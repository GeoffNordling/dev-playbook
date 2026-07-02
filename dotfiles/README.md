---
type: README
title: Dotfiles
description: Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
---

# Dotfiles

Claude Code configuration — skills, rules, settings, and hooks — managed via GNU Stow.

Stow links `.agents/`, `.bashrc.d/`, and `bin/` into `$HOME`. The contents of `dot-claude/` are stowed into `~/.claude/` separately (the source is named `dot-claude` rather than `.claude` so Claude Code's hardcoded protected-paths prompt does not fire when editing files under it).

## Structure

```
dot-claude/
  skills/      Claude Code skills (SDD workflow, commit, tool wrappers, etc.)
  rules/       Global rules applied to every conversation
  hooks/       Claude Code hook scripts
  settings.json          Global Claude Code settings (model, permissions, hooks)
.agents/skills/    Externally managed skills
.bashrc.d/         Bash snippets auto-sourced by Fedora's stock ~/.bashrc
bin/
  sync-dotfiles.sh   Stow sync (main checkout only) — run after adding or removing files
```

## Workflow

1. Edit files here (never chase symlinks into `~/.claude/`)
2. Run `bin/sync-dotfiles.sh` after adding or removing files — from the main checkout only; it relinks live `~/.claude`, so it's a human step, never run from a per-issue worktree
3. Edits to existing files take effect immediately (already symlinked)
