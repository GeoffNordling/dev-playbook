---
type: Standard
title: Build Conventions
description: Standard Make targets and the pre-commit hook-repo model for Python sub-projects — format, lint, typecheck, test, check
---

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

dev-playbook publishes the canonical hook set as a **pre-commit hook repository**: the hook definitions live in [`dev-playbook/.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml), backed by the scripts in `tools/bin/` and the shared primitives in `tools/lib/`. Consumer repos reference them by URL and a pinned revision in their own `.pre-commit-config.yaml`, exactly as they reference any third-party hook (e.g. ruff):

```yaml
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: <commit-sha>
    hooks:
      - id: python-lint
      - id: ref-check
      - id: okf-lint
      - id: internal-skill-audit
      - id: judgments-lint
```

The hooks group by concern: `python-lint` runs the Python-source rules (no `from __future__ import annotations`, empty `__init__.py`, no private-name access from tests) in one walk; `ref-check` and `okf-lint` cover markdown and OKF-bundle integrity (cross-references, concept-doc types, `index.md` freshness); `internal-skill-audit` and `judgments-lint` validate skill bundles and judgment declarations. Third-party ruff (`ruff` + `ruff-format`) is configured locally, not published here.

pre-commit clones dev-playbook into its own cache at the pinned `rev` and runs the hooks from there, so resolution is independent of where the consumer repo — or any of its worktrees — sits on disk. The hooks work uniformly in normal checkouts, in `.claude/worktrees/`, and on CI.

Pinning is deliberate. A consumer runs a known revision of the hooks, not whatever is on dev-playbook's default branch this minute. A change to the hook tools — any `tools/bin/` hook script or `.pre-commit-hooks.yaml` — therefore reaches a consumer only when that consumer bumps its pinned `rev`, a manual and reviewable step. `pre-commit autoupdate` rewrites the `rev` to the latest commit when you choose to update.

dev-playbook consumes its own hooks from the working tree via a `repo: local` block in its `.pre-commit-config.yaml`, so hook edits are testable in place before release. The hook metadata therefore appears twice *within* dev-playbook — once in the published manifest, once in the local block — which is intentional: the manifest serves consumers, the local block dogfoods the working tree, and a hook change updates both. No other repo duplicates anything; consumers hold only a pinned pointer.

Pre-commit is fast and runs on every commit. Do not invoke `make check` from a pre-commit hook — `make check` is whole-repo (including the test suite), so it runs at gate points like `pre-push` or CI instead.

## Continuous integration

CI runs two gates on every push and pull request to `main`: pre-commit across the whole repo, and `make check` in each Python sub-project's root. CI's Python version matches the `requires-python` floor in `pyproject.toml`, and the runner installs `uv` (via `astral-sh/setup-uv`) so `script` hooks with PEP 723 dependencies resolve.

CI sets `SKIP: ref-check` on the pre-commit gate. `ref-check` validates both reference forms — root-absolute Links (`/path`) and cross-repo Citations (`~/workspace/<repo>/…`) — and a CI runner checks out only the one repo, so the cross-repo citations never resolve and the hook would always fail. Local pre-commit stays the strict gate for references. (`okf-lint` is not skipped: it validates the bundle's own concept-doc types and `index.md` listings, all in-repo, so it resolves on a single-repo runner.)

A consumer's workflow runs pre-commit as a plain shell step, which honors a step-level `working-directory:` — the `pre-commit/action` wrapper does not. pre-commit fetches the dev-playbook hook repo at its pinned `rev` the same way it fetches any remote hook:

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      - uses: astral-sh/setup-uv@v3
      - run: |
          pip install pre-commit
          pre-commit run --all-files --show-diff-on-failure --color=always
        env:
          SKIP: ref-check
      - run: make check
```

dev-playbook's own [`.github/workflows/ci.yml`](/.github/workflows/ci.yml) is a self-hosting variant — it runs pre-commit via `pre-commit/action` and scopes `make check` to `working-directory: tools` for its sub-project layout. It is not the consumer template.

Because pre-commit clones dev-playbook over HTTPS unauthenticated — on every consumer's runner and on every developer's first run — **dev-playbook must remain a public repository**. Making it private would break hook resolution for every consumer.
