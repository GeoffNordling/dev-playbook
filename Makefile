# Build products the gate needs that git does not carry. A repo with any
# writes artifacts.mk, which sets ARTIFACTS and builds each file.
-include artifacts.mk
.PHONY: format format-check lint typecheck test check
format:
	uv run ruff format .
format-check:
	uv run ruff format --check .
lint:
	uv run ruff check .
typecheck:
	uv run mypy src tests
test: $(ARTIFACTS)
	uv run pytest
check: format-check lint typecheck test
	uvx pre-commit run --all-files

# cloa-viewer page. A second .PHONY line rather than an edit to the first: the
# canonical Makefile fragment must appear verbatim, and scripts/repo-lint
# compares it line by line (extras may follow). Both targets reach into
# artifacts.mk for the rules that build what they need.
.PHONY: web web-check
web: $(ARTIFACTS)
web-check: $(WEB)/node_modules
	npm --prefix $(WEB) run typecheck
