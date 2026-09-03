---
type: Standard-Card
title: Python
description: Governs how Python source is written — fail-loud code, docstrings, module layout, helpers, formatting, and type annotations
---

# Python

Governs how Python source is written — fail-loud code, docstrings, module
layout, helpers, formatting, and type annotations.

## Define

- [python/style.md](/standards/python/style.md) — the contract: a Python
  file's initializers, docstrings, fail-loud values, statement order,
  helpers, formatting, and annotations

## Audit

- [python-lint](/scripts/python-lint) — the workspace Python-source
  detector; read-only, run ad hoc or by the suite (`python.empty-init`,
  `python.no-future-annotations`)
- ruff — third-party lint, docstring, and format detector, located by its
  pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml):
  the `ruff-check` hook reports the lint families and the pydocstyle `D`
  family, and `ruff format --check` reports the formatting rule, the check
  mode of the `ruff-format` hook the commit gate stations; both are
  configured in the canonical
  [pyproject.toml](/standards/build/canonical/pyproject.toml)
- mypy — third-party type detector, backing Annotated signatures, located
  by the `typecheck` target in
  [Makefile.python](/standards/build/canonical/Makefile.python)

Five of the nine rules have no detector and are the reviewer's call: the
plain-English half of Docstrings, Fail loudly, Module layout, Helper
justification, and Helper placement. A chosen gap, not a forgotten one.

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where python-lint (dispatched by the published
  `playbook-lint` hook) and ruff's two pinned hooks block every commit:
  `ruff-check` reports, `ruff-format` rewrites
- `make check-judgments-cache` — the **push gate**, where `make check` runs
  mypy and `ruff format --check`, either of which blocks the push

## Adopt

- none
