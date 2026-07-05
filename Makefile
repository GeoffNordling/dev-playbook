# Transitional check gate: delegates to the current tools/ layout while the
# migration in PLAN.md runs. Task 1 there replaces this file with the
# canonical Python form. The two --deselect flags skip the known
# judgment-cache misses; task 5 fills the cache and removes them.
.PHONY: check
check:
	uvx pre-commit run --all-files
	$(MAKE) -C tools format-check lint typecheck
	cd tools && uv run pytest -q --deselect "tests/test_judgments_gate.py::test_judgment_cached[judgments-standard-matches-loader]" --deselect "tests/test_judgments_gate.py::test_judgment_cached[run-judgments-skill-matches-tooling]"
