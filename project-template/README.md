# Project Template

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Python projects using uv and Claude Code.

## Usage

```bash
cookiecutter path/to/dev-playbook/project-template
```

## Template Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | My Project | Human-readable project name |
| `project_slug` | my-project | Repo/directory name (derived from project_name) |
| `package_name` | my_project | Python package name (derived from project_slug) |
| `author_name` | Geoff Nordling | Author name for LICENSE and pyproject.toml |
| `description` | | One-line project description |
| `python_version` | 3.12 | Minimum Python version |
| `project_layout` | scripts | Project structure (see options below) |

### Layout Options

| Option | What you get |
|--------|-------------|
| `scripts` | scripts/ |
| `scripts+notebooks` | scripts/ + notebooks/ |
| `package` | src/package_name/ |
| `package+scripts` | src/package_name/ + scripts/ |
| `package+notebooks` | src/package_name/ + notebooks/ |
| `package+scripts+notebooks` | src/package_name/ + scripts/ + notebooks/ |

## What You Get

- `pyproject.toml` configured for uv with ruff, mypy, and pytest dev dependencies
- `CLAUDE.md` with standard conventions and tool commands
- `.claude/` directory with project permissions and skills skeleton
- `LICENSE` with all-rights-reserved copyright
- `Makefile` with format, lint, typecheck targets
- `.pre-commit-config.yaml` with ruff and mypy hooks
- `.github/workflows/ci.yml` with lint, format, typecheck, and test jobs
- `.python-version` pinned to your chosen Python version
- `.gitignore` with Python/uv/marimo defaults
- `tests/` directory ready for pytest
- Git repo initialized with an initial commit
- uv environment synced and pre-commit hooks installed
