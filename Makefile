.PHONY: format format-check lint typecheck test check check-judgments
SKIP_JUDGMENTS ?= 1
export SKIP_JUDGMENTS
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
# The judgment cache exists only on the Fedora primary, which checks it before
# every push. The WSL secondaries have no cache, so they set
# NO_JUDGMENT_CACHE=1 and this skips that one check there.
check-judgments:
	$(MAKE) check SKIP_JUDGMENTS=$(if $(NO_JUDGMENT_CACHE),1,0)
