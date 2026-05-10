# Edit Dotfiles in dev-playbook

Files under `~/.claude/` (skills, rules, settings) are symlinked from the
dev-playbook dotfiles repo. Always edit the source, not the symlink.

- `~/workspace/dev-playbook/dotfiles/dot-claude/`

(The source directory is `dot-claude/`, not `.claude/`, so editing it does
not trigger Claude Code's hardcoded protected-paths prompt. Stow links it
into `~/.claude/` at runtime.)

After editing, commit and push the dev-playbook repo.
