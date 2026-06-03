# dev-playbook

## Rules

- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks. It relinks `~/.claude` against this checkout — so it acts on live `$HOME` and only makes sense from the main checkout, never a per-issue worktree. It's the dotfiles analogue of `git push`: a human transition step, not something a workflow agent runs.
- Before changing the pre-commit hooks (the `tools/bin/` scripts or `.pre-commit-hooks.yaml`), read the Pre-commit section of [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md) — it explains the hook-repo model and why consumer repos then need their pinned `rev` bumped.

## Audience

This is a meta repo. Most of what's authored here applies to *other* repos that
live elsewhere in the workspace and are not visible from this one.
The audience is the population of ~/workspace repos, not this particular one.