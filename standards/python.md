---
type: Standard-Card
title: Python
description: Governs how Python source code is written — language conventions and the anti-pattern catalog
---

# Python

Governs how Python source code is written — language conventions and the
anti-pattern catalog.

## Define

- [python/style.md](/standards/python/style.md) — the contract: language
  conventions and the anti-pattern catalog

## Audit

- [python-lint](/scripts/python-lint) — the workspace Python-source
  detector; read-only, run ad hoc or by the suite
- ruff — third-party lint and docstring detector, hook `ruff-check` (the
  pydocstyle `D` family, configured in the canonical
  [pyproject.toml](/standards/build/canonical/pyproject.toml)), located by its
  pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
- mypy — third-party type detector, located by the `typecheck` target in
  [Makefile.python](/standards/build/canonical/Makefile.python)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where python-lint (dispatched by the published
  `playbook-lint` hook) and ruff (its own pinned hook) block every commit
- `make check-judgments-cache` — the **push gate**, where mypy blocks every push

## Adopt

- none
