# dev-playbook

## Rules

- This is a public repository. Never commit secrets or confidential information.
- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.

## LaTeX in Markdown

- Use `\ast` instead of `*` in LaTeX superscripts (e.g., `$A^\ast$` not `$A^*$`). GitHub's Markdown parser consumes bare `*` as italic markup before the math renderer sees it.
- Do not use `\;` for spacing in LaTeX equations. GitHub renders it as a visible semicolon. Use regular spaces instead.
