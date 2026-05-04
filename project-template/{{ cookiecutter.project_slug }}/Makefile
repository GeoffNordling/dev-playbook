.PHONY: format lint typecheck test check

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy{% if 'package' in cookiecutter.project_layout %} src/{% endif %}{% if 'scripts' in cookiecutter.project_layout %} scripts/{% endif %}

test:
	uv run pytest

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy{% if 'package' in cookiecutter.project_layout %} src/{% endif %}{% if 'scripts' in cookiecutter.project_layout %} scripts/{% endif %}
	uv run pytest
