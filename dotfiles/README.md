---
type: README
title: Dotfiles
description: Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
---

# Dotfiles

Claude Code configuration — skills, rules, settings, and hooks — managed via GNU Stow.

Three packages are stowed into `$HOME`. The `dot-claude/` package is named without a literal `.claude` path segment so Claude Code's hardcoded protected-paths prompt does not fire when editing files under it.

Every machine runs the same configuration; the few hooks that only make sense on one machine detect the host at runtime — see [machines.md](/docs/machines.md).

## Structure

```
dot-claude/          -> ~/.claude/
  agents/        Typed agent definitions the software factory launches
  skills/        Claude Code skills (software factory nodes, commit, tool wrappers, etc.)
  rules/         Global rules applied to every conversation
  hooks/         Claude Code hook scripts
  settings.json  Claude Code settings, shared by every machine (see below)
.agents/             -> ~/.agents/
  skills/      Externally managed skills, mirrored into dot-claude/skills/
.bashrc.d/           -> ~/.bashrc.d/
                 Bash snippets sourced by ~/.bashrc (the sync wires up the
                 loader where the distro's stock bashrc has none)
```

The three stowed packages each install into the directory they are named for.
Stow places a package's *contents* in the target, so targeting `$HOME` would
scatter them one level too high — `scripts/sync-dotfiles` holds the mapping.

## Settings: the live file is the authority

`~/.claude/settings.json` is a stowed symlink to `dot-claude/settings.json`,
and Claude Code writes settings changes through it (verified 2026-08-28 on
version 2.1.250): toggle a setting in a session and the change lands in the
main checkout as an ordinary uncommitted edit, on whatever branch is checked
out there. The repo is the carrier that syncs settings between machines, not
a source of authority to enforce — committing and pushing those edits is the
user's, like any other change.

Two consequences hold the design together:

- **One file serves every machine.** A hook that must not run somewhere
  guards itself at runtime (`hooks/play-sound`, `hooks/measure-event`)
  instead of living in a per-machine settings variant.
- **The one failure left is the symlink itself.** If a future Claude Code
  version replaces the symlink with a regular file instead of writing through
  it, the repo silently stops receiving changes —
  `hooks/session-start-settings-link` checks for exactly that at every
  session start.

## Workflow

1. Edit files here (never chase symlinks into `~/.claude/`)
2. Run `scripts/sync-dotfiles` after adding or removing files — from the main checkout only; it relinks live `~/.claude`, so it's a step the user runs, never one from a per-issue worktree
3. Edits to existing files take effect immediately (already symlinked); a settings edit loads at the next session start
