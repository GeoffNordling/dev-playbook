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
	uv run pytest
check: format-check lint typecheck test
	uvx pre-commit run --all-files

# cloa-viewer page. A second .PHONY line rather than an edit to the first: the
# canonical Makefile fragment must appear verbatim, and scripts/repo-lint
# compares it line by line (extras may follow).
.PHONY: web web-check
web:
	npm --prefix src/dev_playbook/cloa_viewer/web ci
	npm --prefix src/dev_playbook/cloa_viewer/web run build
web-check:
	npm --prefix src/dev_playbook/cloa_viewer/web run typecheck
