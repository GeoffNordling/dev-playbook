# Edit Dotfiles in dev-playbook

Files under `~/.claude/` (skills, rules, settings) are symlinked from the
dev-playbook dotfiles repo. Always edit the **source** — the
`dotfiles/dot-claude/` tree of the dev-playbook checkout you are standing in,
main checkout or issue worktree — never the `~/.claude/` symlink. Per
same-repo resolution: from a dev-playbook issue worktree, edit that
worktree's `dotfiles/dot-claude/` so the change rides the issue branch, not
the live main checkout.

(The source directory is `dot-claude/`, not `.claude/`, so editing it does
not trigger Claude Code's hardcoded protected-paths prompt. Stow links it
into `~/.claude/` at runtime.)

After editing, commit and push the dev-playbook repo.
