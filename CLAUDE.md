# dev-playbook

## Rules

- This is a public repository. Never commit secrets or confidential information.
- This is primarily a documentation repo. Application code belongs in project repos.
- Infrastructure scripts (sync, hooks) and templates are fine.
- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.
