# dev-playbook

## Rules

- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.
- `.pre-commit-config.yaml` is the source of truth for pre-commit hooks. Edit it directly to add, change, or remove a hook. When adding a new validation script under `tools/bin/`, add its hook entry to the YAML at the same time.

## Audience

This is a meta repo. Most of what's authored here applies to *other* repos that
live elsewhere in the workspace and are not visible from this one:

- `standards/`, `sdd-standards/` — cross-project standards; apply to every
  workspace repo, not just this one
- `project-template/` — cookiecutter that generates fresh repos elsewhere
- `dotfiles/.claude/` — symlinked to `~/`, used by every project

When editing anything under those paths, the audience is the population of
workspace repos, not this repo.

## Agent skills

### Issue tracker

GitHub Issues, accessed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default 5-role canonical vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
