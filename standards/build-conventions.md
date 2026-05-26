# Build Conventions

Conventions for the build-and-check surface that Python projects in this
workspace.

These conventions apply to every Python sub-project, including
script-only ones with no `src/` (e.g. `dev-playbook/tools/`). Repos with
no Python at all (e.g. `dev-playbook` root) need no `Makefile`.

## Make

Make is the task runner. Every Python sub-project `SHALL` have a `Makefile` at its root with these targets:

| Target | Definition |
|---|---|
| `format` (mutating) | `uv run ruff format .` |
| `format-check` | `uv run ruff format --check .` |
| `lint` | `uv run ruff check .` |
| `typecheck` | `uv run mypy <code-roots>` |
| `test` | `uv run pytest` |

`make check` runs `format-check lint typecheck test` as prerequisites. All targets are `.PHONY`. `<code-roots>` is whichever of `src/`, `tests/`, `scripts/` exist (PEP 723 scripts under `bin/` are out of scope).

## Pre-commit

The canonical hook set is [`dev-playbook/.pre-commit-config.yaml`](../.pre-commit-config.yaml).
That file — including its header preamble explaining the three-environment
contract — is the standard. Consumer repos opt in by symlinking it:

```bash
ln -s ../dev-playbook/.pre-commit-config.yaml .pre-commit-config.yaml
```

Make the symlink relative, not absolute. Absolute symlinks bake `$HOME` into the working tree and break on CI runners. The relative form resolves wherever the two repos sit as siblings — locally under `~/workspace/`, and on CI when dev-playbook is checked out alongside the consumer (see [Continuous Integration](#continuous-integration)).

Meta repos that author the config (e.g. `dev-playbook` itself) keep the real file; everything else symlinks.

Pre-commit is fast and runs on every commit. Do not invoke `make check` from a pre-commit hook — `make check` is whole-repo (including the test suite), so it runs at gate points like `pre-push` or CI instead.

## Continuous Integration

The canonical workflow is [`dev-playbook/.github/workflows/ci.yml`](../.github/workflows/ci.yml). It runs two gates: pre-commit against `.pre-commit-config.yaml`, and `make check` in each Python sub-project's root. CI's Python version matches the `requires-python` floor in `pyproject.toml`. Consumer repos use the same workflow with the sibling checkout from [Pre-commit](#pre-commit) so the symlinked config resolves.

The sibling-checkout step (`actions/checkout@v4` with `repository: GeoffNordling/dev-playbook`) runs unauthenticated on the consumer's runner, so **dev-playbook must remain a public repository**. Making it private would break CI for every consumer repo that symlinks the canonical config.
