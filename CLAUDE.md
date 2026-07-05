# dev-playbook

## Build

The repo carries Python tooling — the published pre-commit hook scripts and the
workspace CLIs — laid out per the [build standard](/standards/build/index.md):
the importable package is `src/dev_playbook/`, executables live in `scripts/`,
and tests in `tests/`, over a single root `pyproject.toml`.

- **`make check`** is the gate — format-check, lint, typecheck, and test, then
  the full pre-commit suite (`uvx pre-commit run --all-files`). Green `check`
  means the repo passes everything it can verify locally.
- Stages run alone: `make format` (mutating), `make lint` (ruff),
  `make typecheck` (mypy over `src tests`), `make test` (pytest).
- **uv** owns the environment: `uv sync` builds the editable install of
  `dev_playbook`; run tools through `uv run …` so they use the project venv.
- Run one file or case: `uv run pytest tests/test_md.py::TestGithubSlug` (or
  narrow with `-k <expr>`).

## Rules

- See README.md for what belongs in this repo vs. other repos.
- After adding or removing files under `dotfiles/`, run `dotfiles/bin/sync-dotfiles.sh` to update Stow symlinks. It relinks `~/.claude` against this checkout — so it acts on live `$HOME` and only makes sense from the main checkout, never a per-issue worktree. It's the dotfiles analogue of `git push`: a human transition step, not something a workflow agent runs.
- Before changing the pre-commit hooks (the `tools/bin/` scripts or `.pre-commit-hooks.yaml`), read [distribution.md](/standards/build/distribution.md) — it explains the hook-repo model and why consumer repos then need their pinned `rev` bumped.

## Audience

This is a meta repo. Most of what's authored here applies to *other* repos that
live elsewhere in the workspace and are not visible from this one.
The audience is the population of ~/workspace repos, not this particular one.