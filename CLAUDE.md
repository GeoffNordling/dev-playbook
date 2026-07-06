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

- This is a meta repo: what is authored here governs the population of
  ~/workspace repos, most of which are not visible from this one. Write
  standards for that audience, never around this repo's internals.
- Before changing the published hooks (the `scripts/` entry points or
  `.pre-commit-hooks.yaml`), read
  [distribution.md](/standards/build/distribution.md) — consumer repos pin a
  `rev` and need a bump after hook changes.
