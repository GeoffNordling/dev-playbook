# project-template

## Rules

- This repo is a Cookiecutter template; do not try to run or install it as a Python project.

## Structure

- `cookiecutter.json` — template variables and defaults
- `{{ cookiecutter.project_slug }}/` — the Jinja2 template directory that Cookiecutter renders
- `hooks/post_gen_project.py` — post-generation script (removes unused dirs, git init, uv sync, pre-commit install)
- `README.md` — usage instructions for the template

The generated project includes standard code quality tooling: ruff (format + lint), mypy (gradual type checking), pre-commit hooks, GitHub Actions CI, and a Makefile.

## Testing Changes

After editing template files, smoke-test with:

```bash
cookiecutter --no-input /path/to/this/repo project_name="Smoke Test" -o /tmp
```

Test multiple `project_layout` options (e.g., `scripts`, `package+scripts+notebooks`).

## Formatting

- Do not use emdashes; use semicolons instead.
