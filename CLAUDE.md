# dev-playbook

## Rules

- This is a public repository. Never commit secrets or confidential information.
- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks.

## LaTeX in Markdown

- Use `\ast` instead of `*` in LaTeX superscripts (e.g., `$A^\ast$` not `$A^*$`). GitHub's Markdown parser consumes bare `*` as italic markup before the math renderer sees it.
- Do not use `\;` for spacing in LaTeX equations. GitHub renders it as a visible semicolon. Use regular spaces instead.

## Tools development (tools/)

- Standalone scripts in `bin/` use PEP 723 inline metadata (`# /// script` blocks); do not add their dependencies to `pyproject.toml`.
- Packages in `src/` are installed via `pyproject.toml` console entry points.
- When adding a new tool, add it to the tools table and tool reference section in `tools/README.md`.
- Tests: `cd tools && uv run pytest`
- Lint: `cd tools && make lint`
- Format: `cd tools && make format`
- Typecheck: `cd tools && make typecheck`
- Setup: `cd tools && uv pip install -e .` (packages)

## Code style (tools/)

- Python >= 3.11; ruff for lint + format, mypy for type checking
- Line length 88 (ruff default)
- Ruff rules: E, W, F, I, UP, B, SIM (E501 ignored)
