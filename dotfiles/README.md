---
type: README
title: Dotfiles
description: Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
---

# Dotfiles

Claude Code configuration — skills, rules, settings, and hooks — managed via GNU Stow.

Stow links `.agents/`, `.bashrc.d/`, and `bin/` into `$HOME`. The contents of `dot-claude/` are stowed into `~/.claude/` separately (the source is named `dot-claude` rather than `.claude` so Claude Code's hardcoded protected-paths prompt does not fire when editing files under it).

One machine runs one configuration, and the machines differ — see [machines.md](/docs/machines.md).

## Structure

```
dot-claude/
  skills/      Claude Code skills (SDD workflow, commit, tool wrappers, etc.)
  rules/       Global rules applied to every conversation
  hooks/       Claude Code hook scripts
settings/
  base.json        Portable Claude Code settings — every machine gets these
  <machine>.json   One machine's remainder, merged over the base
.agents/skills/    Externally managed skills
.bashrc.d/         Bash snippets sourced by ~/.bashrc (the sync wires up the
                   loader where the distro's stock bashrc has none)
bin/
  sync-dotfiles.sh   Stow sync (main checkout only) — run after adding or removing files
```

## Settings are generated, not symlinked

`~/.claude/settings.json` is the one managed file that is not a symlink. Claude Code reads a single user-scope settings file and offers no local override layer, so the machine-specific remainder cannot be layered on top of a shared checked-in file — the sync merges `settings/base.json` with `settings/<machine>.json` and installs the result. Editing the installed copy loses the edit at the next sync; a session-start hook reports the drift rather than letting it pass silently.

## Workflow

1. Edit files here (never chase symlinks into `~/.claude/`)
2. Run `bin/sync-dotfiles.sh` after adding or removing files — from the main checkout only; it relinks live `~/.claude`, so it's a human step, never run from a per-issue worktree
3. Edits to existing files take effect immediately (already symlinked) — except under `settings/`, which needs a sync to reinstall
