# dev-playbook

## Rules

- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.
- `.pre-commit-config.yaml` is the source of truth for pre-commit hooks. Edit it directly to add, change, or remove a hook. When adding a new validation script under `tools/bin/`, add its hook entry to the YAML at the same time.
- Pre-commit hook entries run in three environments: dev-playbook locally, consumer repos (which symlink the config back here), and the GitHub Actions runner (checked out at an arbitrary path). Any change to a `local` hook entry MUST work in all three. See the comment at the top of `.pre-commit-config.yaml` for the pattern and the rationale.

## Audience

This is a meta repo. Most of what's authored here applies to *other* repos that
live elsewhere in the workspace and are not visible from this one:

- `standards/` — cross-project standards; apply to every workspace repo,
  not just this one
- `dotfiles/dot-claude/` — Stow-linked to `~/.claude/`, used by every project

When editing anything under those paths, the audience is the population of
workspace repos, not this repo.
