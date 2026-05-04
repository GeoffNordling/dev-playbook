# dotfiles

## Rules

- Always edit files here — never at the symlink targets under `~/`.
- Run `bin/sync-dotfiles.sh` after adding or removing files. Edits to existing `.claude/skills/` files require restarting Claude Code to take effect — the running session caches skill content at startup.

## Structure

- `.claude/skills/` — Claude Code skills. Mix of skills authored here and symlinks mirroring `.agents/skills/`. See [skill-management.md](~/workspace/dev-playbook/standards/skill-management.md).
- `.claude/rules/` — global rules (applied to every conversation)
- `.claude/settings.json` — model, permissions, hooks
- `.agents/skills/` — externally managed skills (e.g., from mattpocock/skills). Mirrored into `.claude/skills/` by `bin/sync-dotfiles.sh`.
- `.bashrc.d/` — Bash snippets auto-sourced by Fedora's stock `~/.bashrc`
- `bin/sync-dotfiles.sh` — Stow sync script
