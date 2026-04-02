.PHONY: format lint typecheck

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy{% if 'package' in cookiecutter.project_layout %} src/{% endif %}{% if 'scripts' in cookiecutter.project_layout %} scripts/{% endif %}

