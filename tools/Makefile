.PHONY: format format-check lint typecheck test check

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

typecheck:
	uv run mypy tests/ workflow_state_data/ src/skipcache/ src/judgments/ transcript_export/

test:
	uv run pytest

check: format-check lint typecheck test
