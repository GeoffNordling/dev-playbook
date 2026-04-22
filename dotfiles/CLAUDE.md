# dotfiles

## Rules

- Always edit files here — never at the symlink targets under `~/`.
- Run `bin/sync-dotfiles.sh` after adding or removing files. Edits to existing `.claude/skills/` files require restarting Claude Code to take effect — the running session caches skill content at startup.

## Structure

- `.claude/skills/` — Claude Code skills
- `.claude/rules/` — global rules (applied to every conversation)
- `.claude/settings.json` — model, permissions, hooks
- `.agents/skills/`, `.dhub/skills/` — externally managed skills
- `.bashrc.d/` — Bash snippets auto-sourced by Fedora's stock `~/.bashrc`
- `bin/sync-dotfiles.sh` — Stow sync script
