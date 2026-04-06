.PHONY: format lint typecheck

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src/
