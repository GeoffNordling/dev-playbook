# CLAUDE.md

## Build / Run

- **uv is the project runner.** Although `pyproject.toml` uses hatchling as the build backend, all commands; tests, scripts, anything; run through `uv`. Use `uv run pytest`, `uv run python`, etc. **Never use `hatch run`.**

{% if 'package' in cookiecutter.project_layout -%}
Install the project in development mode:

```bash
uv sync
```

{% endif -%}
## Lint / Format / Type Check

```bash
uv run ruff check .
uv run ruff format .
uv run mypy{% if 'package' in cookiecutter.project_layout %} src/{% endif %}{% if 'scripts' in cookiecutter.project_layout %} scripts/{% endif %}

```

Or use the Makefile:

```bash
make lint
make format
make typecheck
```

## Tests

```bash
uv run pytest
```

## Code Style

- Ruff enforces linting and formatting; mypy enforces type correctness in gradual mode.
- Pre-commit hooks run ruff and mypy on every commit.

## Formatting

- Do not use emdashes; use semicolons instead.
