.PHONY: format lint typecheck test

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src/

test:
	uv run pytest
