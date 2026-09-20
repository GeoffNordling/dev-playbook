---
type: Standard-Ruleset
title: Python Style
description: How a Python file is written — empty initializers, docstrings, fail-loud values, statement order, banned future imports, helper shape, formatting, and annotations
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

## Docstrings

Every module, class, function, and method in the file carries a
docstring, except a file named `__init__.py` and a pytest test function,
whose name begins with `test_`.

`python.docstrings` · deterministic

## Docstring content

A docstring in the file says in plain English what the module, class,
function, or method it documents does.

`python.docstring-content` · stochastic

## Fail loudly

A value the code requires is read directly, so a missing one raises. A
fallback stands only where the missing value is a real runtime state
rather than a programming error, and it carries an inline comment giving
that reason. Each of these shapes, over a value that always exists, is a
fallback that hides the missing value:

- `dict.get(key, default)` where `key` is always present.
- `if x is None: return default`, or `x or default`, conditioning a value
  that always exists.
- `try: ... except Exception: return default`, swallowing the error into a
  sentinel.
- `getattr(obj, "attr", default)` for an attribute the object is required
  to have.
- A default parameter value papering over state the caller always
  supplies.

`python.fail-loudly` · stochastic

## Module layout

A module's top-level statements run in one order:

1. The module docstring.
2. `import` and `from ... import` statements.
3. Plain-literal module constants: `UPPER_SNAKE_CASE` names whose values
   are literals, tuples of literals, or `re.compile(...)` patterns,
   `_PRIVATE` constants included.
4. Type aliases, dataclasses, classes, and functions, interleaved with
   *derived* constants: module-level `UPPER_SNAKE_CASE` names whose values
   depend on a class, function, or enum defined in the file. A derived
   constant sits immediately after the definitions it derives from.

`python.module-layout` · deterministic

## No future annotations

`from __future__ import annotations` does not appear in the file, unless
one of the file's parent directories is named `build`, `dist`, or
`deprecated`.

`python.no-future-annotations` · deterministic

## Helper justification

Every helper function in the file is multi-use, substantial in body, a
distinct concern at another abstraction level, or an entry in a dispatch
table, registry, or strategy map:

- **Multi-use**: called from two or more sites.
- **Substantial body**: the logic is long or intricate enough that lifting
  it out makes the caller readable. A one-line or two-line helper called
  once is pure relocation.
- **Distinct concern at another abstraction level**: the helper's job
  belongs to a different layer than its caller, such as a regex-based
  enforcement check inside a high-level dispatch loop.
- **Architectural pluggability**: an entry in a dispatch table, registry,
  or strategy map, which looks single-use by static call count and is
  pluggable by design.

Symmetry with siblings, prior existence, and speculative reuse justify no
helper: a trivial single-use function beside two siblings of the same
shape is still trivial, the bar is the same for a new helper and for one
inherited from earlier work, and extraction waits for the second caller.

`python.helper-justification` · stochastic

## Helper placement

A helper function sits directly beneath the function that uses it, or,
where two or more functions use it, in a `# ---` banner section.

`python.helper-placement` · deterministic

## Formatted by ruff format

The file is byte-identical to the output of `ruff format` run under the
`line-length` that the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml) pins.

`python.formatted-by-ruff-format` · deterministic

## Annotated signatures

Every function and method in the file annotates each parameter, except a
`self` or `cls` first parameter, and its return.

`python.annotated-signatures` · deterministic
