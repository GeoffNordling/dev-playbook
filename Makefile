.PHONY: format format-check lint typecheck test check check-judgments-cache
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
# Arms the judgment cache gate: asserts the cache is passed for whatever
# judgments the repo has tripwired via pytest; finding none passes vacuously.
# Machines without the cache set NO_JUDGMENT_CACHE=1 to skip the cache check.
check-judgments-cache:
	$(MAKE) check SKIP_JUDGMENTS=$(if $(NO_JUDGMENT_CACHE),1,0)
# Arms the job launcher's real-spawn test: the one end-to-end proof that the
# live harness still keeps the promises the launcher is built on. It launches
# actual claude on the subscription, so `make test`, `make check` and CI skip it
# visibly (they export SKIP_REAL_SPAWN=1) and this target is what runs it.
.PHONY: check-real-spawn
SKIP_REAL_SPAWN ?= 1
export SKIP_REAL_SPAWN
check-real-spawn:
	$(MAKE) check SKIP_REAL_SPAWN=0
