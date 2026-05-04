# CLAUDE.md

## Build / Run

- **uv is the project runner.** Although `pyproject.toml` uses hatchling as the build backend, all commands; tests, scripts, anything; run through `uv`. Use `uv run pytest`, `uv run python`, etc. **Never use `hatch run`.**

{% if 'package' in cookiecutter.project_layout -%}
Install the project in development mode:

```bash
uv sync
```

{% endif -%}
## Make targets

```bash
make check       # read-only: format --check + lint + typecheck + test
make format      # apply formatter fixes
make lint        # ruff lint
make typecheck   # mypy
make test        # pytest
```

`make check` is the "is this branch ready?" gate. It is read-only; if it
complains about formatting, run `make format` to apply fixes.

See [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md)
for the canonical target definitions.

## Code Style

- Ruff enforces linting and formatting; mypy enforces type correctness in gradual mode.
- Pre-commit hooks run ruff and mypy on every commit.

## Formatting

- Do not use emdashes; use semicolons instead.

## Agent skills

> **STOP — agent-skills configuration is not yet scaffolded for this repo.**
>
> Before taking any further actions in this repo, run `/setup-matt-pocock-skills`
> in Claude Code. The skill writes `docs/agents/{issue-tracker,triage-labels,domain}.md`
> and replaces this section with the proper Agent skills block. Several engineering
> skills (`/triage`, `/to-issues`, `/tdd`, `/grill-with-docs`, `/improve-codebase-architecture`,
> `/zoom-out`) read from those files and produce degraded output without them.
