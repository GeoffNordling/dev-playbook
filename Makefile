.PHONY: format format-check lint typecheck test check
format:
	uv run ruff format .
format-check:
	uv run ruff format --check .
lint:
	uv run ruff check .
typecheck:
	uv run mypy src tests
test:
	uv run pytest --deselect "tests/test_judgments_gate.py::test_judgment_cached[judgments-standard-matches-loader]" --deselect "tests/test_judgments_gate.py::test_judgment_cached[run-judgments-skill-matches-tooling]"
check: format-check lint typecheck test
	uvx pre-commit run --all-files
