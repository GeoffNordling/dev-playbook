---
type: Standard
title: Python Project Conventions
description: Python project structure, pyproject.toml shape, directory layout, and dev-tool version requirements
---

# Python Project Conventions

Conventions for the shape of a Python project in this workspace: directory
layout, `pyproject.toml`, and tool configuration. Sibling to:

- [python-conventions.md](python-conventions.md) — code-level conventions
- [build-conventions.md](build-conventions.md) — Makefile and `make check`
- [testing-conventions.md](testing-conventions.md) — pytest conventions

Scope: applies to top-level Python repos and to Python sub-projects inside
meta repos (e.g. `dev-playbook/tools/`). Sub-projects `MAY` deviate on
packaging details — e.g. `dev-playbook/tools/` uses `[tool.uv] package =
false` because it is a script collection, not a packageable library. They
`SHALL NOT` deviate on the lint, type-check, and test contract: every
sub-project has the full `[tool.ruff]`, `[tool.mypy]`, and pytest config
described below, and the standard targets defined in
[build-conventions.md](build-conventions.md).

## Directory layout

```
<repo>/
├── pyproject.toml
├── Makefile
├── README.md
├── CLAUDE.md
├── .pre-commit-config.yaml      # relative symlink — see build-conventions.md
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml               # per build-conventions.md — Continuous Integration
├── src/
│   └── <package>/
│       └── __init__.py          # empty per python-conventions.md
└── tests/
    └── __init__.py              # empty
```

## Name mapping

The repo name is kebab-case (`spec-tools`); the package name is the
snake-case transformation (`spec_tools`). Hyphens become underscores.

## pyproject.toml

The canonical shape, using `<repo>` and `<package>` placeholders:

```toml
[project]
name = "<repo>"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<package>"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[dependency-groups]
dev = [
    "mypy>=2.0",
    "pytest>=9.0",
    "ruff>=0.15.14",
]

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "SLF"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["<package>"]

[tool.mypy]
python_version = "3.14"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disable_error_code = ["import-untyped"]
```

## Rationale

- **Hatchling, not setuptools or poetry.** uv's default build backend; one
  fewer choice to make per project.
- **`disallow_untyped_defs = true`.** Every function gets a signature.
  Lighter than full `strict = true`, which also turns on
  `disallow_untyped_calls` (chokes on every untyped third-party lib) and
  `disallow_any_generics` (noisy about every bare `list`/`dict`).
- **`disallow_incomplete_defs = true`.** Pairs with the above: if a function
  annotates *some* but not all of its parameters or return, mypy errors.
  Without it, a half-annotated signature passes silently and yields no type
  information for the unannotated slots.
- **`disable_error_code = ["import-untyped"]`.** Allows imports from
  libraries without type stubs without forcing `# type: ignore` at each
  import. Add `types-*` stub packages to `dev` when a specific library
  warrants them (e.g. `types-pyyaml` for `pyyaml`).
- **Ruff rule selection.** `E`/`W`/`F` are pycodestyle/pyflakes; `I` is
  isort; `UP` is pyupgrade; `B` is bugbear; `SIM` is simplification; `SLF`
  flags private-member access from outside the defining class. `E501`
  (line length) is ignored because line length is enforced by `ruff
  format`.

## Dev tooling versions

The standard pins minimum versions of `mypy`, `pytest`, and `ruff` (see the
`dev` group above). Consumer repos `SHALL` declare floors at least as high
as the standard's; bumping the workspace floor is done by editing this file
and propagating to consumer repos. Exact resolved versions are recorded in
each repo's `uv.lock`.

## Project scripts

When a project exposes a CLI, add a `[project.scripts]` entry:

```toml
[project.scripts]
<command> = "<package>.cli:main"
```

This is lazy — only present when the project actually has a CLI. Repos
that start as libraries do not need this section.

## Initial setup

A new Python project initializes via `uv init --lib --package <repo>`,
followed by overwriting the generated `pyproject.toml` with the shape
above. The `new-repo` skill handles this.
