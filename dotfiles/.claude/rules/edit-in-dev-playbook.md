# Edit Dotfiles in dev-playbook

Files under `~/.claude/` (skills, rules, settings) are symlinked from the
dev-playbook dotfiles repo. Always edit the source, not the symlink.

- **Mac (Darwin):** `/Volumes/workplace/dev-playbook/dotfiles/.claude/`
- **WSL:** `~/workspace/dev-playbook/dotfiles/.claude/`

After editing, commit and push the dev-playbook repo.
