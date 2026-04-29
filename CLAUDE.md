# dev-playbook

## Rules

- This is a public repository. Never commit secrets or confidential information.
- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.

## LaTeX in Markdown

- Use `\ast` instead of `*` in LaTeX superscripts (e.g., `$A^\ast$` not `$A^*$`). GitHub's Markdown parser consumes bare `*` as italic markup before the math renderer sees it.
- Do not use `\;` for spacing in LaTeX equations. GitHub renders it as a visible semicolon. Use regular spaces instead.

## Agent skills

### Issue tracker

GitHub Issues, accessed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default 5-role canonical vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
