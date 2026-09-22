---
type: Standard
title: Python Style
description: How a Python file is written — empty initializers, docstrings, banned future imports, and formatting
population: "a Python file a governed repo tracks: a .py file, or an extensionless file with a Python shebang"
---

# Python Style

A Python file a governed repo tracks: any `.py` file, and any
extensionless file whose first line is a Python shebang. Every rule below
binds one file's own state. The repo-level shape around that file, meaning
`pyproject.toml`'s name mapping, `[project.scripts]`, and what a `scripts/`
file carries to run from a bare clone, is
[The Python Project](/standards/build/python.md). The task-runner targets
that invoke ruff and mypy are
[Canonical Artifacts](/standards/build/canonical.md#makefile), and pytest
conventions are
[Testing Conventions](/standards/testing/conventions.md).

## Empty init

A file named `__init__.py` holds no character other than whitespace: no
docstring, no import, no re-export, no `__all__` declaration, and no
other code.

`python.empty-init` · deterministic

> **Why.** An empty init leaves each caller importing from the
> specific submodule, `from pkg.sub import thing`, rather than from
> the package root, so an import path names where the object is
> defined.

## Every definition carries a docstring

Every module, class, function, and method in the file carries a
docstring, except a file named `__init__.py` and a pytest test function,
whose name begins with `test_`.

`python.every-definition-carries-a-docstring` · deterministic

> **Why.** A pytest test function is named `test_<behavior>`, literal
> enough that a docstring restates the name.

## No future annotations

`from __future__ import annotations` does not appear in the file, unless
one of the file's parent directories is named `build`, `dist`, or
`deprecated`.

`python.no-future-annotations` · deterministic

> **Why.** Python 3.11 and later provide every motivation for the
> import: PEP 604 unions, `X | Y`, builtin generics, `list[int]`, and
> string-quoted forward references.

## Formatted by ruff format

The file is byte-identical to the output of `ruff format` run under the
`line-length` that the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml) pins.

`python.formatted-by-ruff-format` · deterministic
