# dotfiles

## Rules

- Always edit files here — never at the symlink targets under `~/`.
- Run `bin/sync-dotfiles.sh` after adding or removing files. Edits to existing files take effect immediately.

## Structure

- `.claude/skills/` — Claude Code skills
- `.claude/rules/` — global rules (applied to every conversation)
- `.claude/settings.json` — model, permissions, hooks
- `.agents/skills/`, `.dhub/skills/` — externally managed skills
- `bin/sync-dotfiles.sh` — Stow sync script
