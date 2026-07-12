---
type: Standard Card
title: Python
description: Card for the Python standard — how Python source code is written
---

# Python

Governs how Python source code is written.

## Define

- [python/style.md](/standards/python/style.md) — the contract: language
  conventions and the anti-pattern catalog

## Audit

- [python-audit](/scripts/python-audit) — the workspace Python-source
  detector; read-only, run ad hoc or by the suite
- ruff (`ruff-check`, `ruff-format`) — third-party lint, formatting, and
  docstring detector (the pydocstyle `D` family, configured in the canonical
  [pyproject.toml](/standards/build/canonical/pyproject.toml)), located by its
  pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
- mypy — third-party type detector, located by the `typecheck` target in
  [Makefile.python](/standards/build/canonical/Makefile.python)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where python-audit and ruff block every commit
- `make check` — the **push gate**, where mypy blocks every push

## Adopt

- none
