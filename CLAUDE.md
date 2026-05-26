# dev-playbook

## Rules

- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.
- `.pre-commit-config.yaml` is the source of truth for pre-commit hooks. Edit it directly to add, change, or remove a hook. When adding a new validation script under `tools/bin/`, add its hook entry to the YAML at the same time.

## Audience

This is a meta repo. Most of what's authored here applies to *other* repos that
live elsewhere in the workspace and are not visible from this one.
The audience is the population of ~/workspace repos, not this particular one.