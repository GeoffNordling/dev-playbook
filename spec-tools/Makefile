.PHONY: format lint typecheck test check

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src/

test:
	uv run pytest

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src/
	uv run pytest
