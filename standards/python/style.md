---
type: Standard
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

## Package initializers

A file named `__init__.py`.

### Empty

The file holds no docstring and no code, ideally zero bytes; every import,
re-export, and `__all__` declaration sits in a named module instead.
python-lint reports one that does not (`python.empty-init`).

Callers import from the specific submodule, `from pkg.sub import thing`,
rather than from the package root. A package's overview belongs in its
primary named module or in a README.

## Docstrings

Every module, class, function, and method carries a docstring saying in
plain English what it does, except an `__init__.py`, which stays empty,
and a pytest test function, whose name carries the behavior. One short
sentence is enough when the behavior is simple, longer when it is not.

A pytest test function follows a `test_<behavior>` naming convention
literal enough that a docstring restates the name. A test module's own
helpers, meaning the factories and fixtures defined as plain functions,
carry docstrings: their names are not similarly load-bearing.

## Fail loudly

A value the code requires is read directly, so a missing one raises; a
fallback for a state that is genuinely runtime carries an inline comment
giving the reason. These are the shapes that quietly hide a missing value:

- `dict.get(key, default)` where `key` is always present. `dict[key]`
  raises `KeyError` instead.
- `if x is None: return default`, or `x or default`, conditioning a value
  that always exists.
- `try: ... except Exception: return default`, swallowing the error into a
  sentinel.
- `getattr(obj, "attr", default)` for an attribute the object is required
  to have. `obj.attr` raises instead.
- A default parameter value papering over state the caller always
  supplies.

A legitimate fallback is one where the missing value is a real runtime
state rather than a programming error. Its inline comment is the signal
that the author weighed it.

A fallback that hides a bug delays the failure to a place far from the
cause, where it is much harder to diagnose. Failing at the point of the
missing value points straight at the defect.

## Module layout

A module's top-level statements run in one order: the module docstring,
the imports, the plain-literal constants, then the definitions
interleaved with the derived constants, each derived constant placed
directly after what it derives from.

1. The module docstring.
2. `import` and `from ... import` statements.
3. Plain-literal module constants: `UPPER_SNAKE_CASE` names whose values
   are literals, tuples of literals, or `re.compile(...)` patterns,
   `_PRIVATE` constants included.
4. Type aliases, dataclasses, classes, and functions, interleaved with
   *derived* constants: module-level `UPPER_SNAKE_CASE` names whose values
   depend on a class, function, or enum defined in the file. A derived
   constant sits immediately after the things it derives from, in a
   labeled section.

A single-use constant sits at the top with the rest, or, when it is
derived, in its grouped section near its dependencies, never beside its
one user mid-file.

## No future annotations

`from __future__ import annotations` does not appear in the file.

python-lint rejects the import (`python.no-future-annotations`).

Python 3.11+ already provides every motivation for it: PEP 604 unions
(`X | Y`), builtin generics (`list[int]`), and string-quoted forward
references.

## Helper justification

Every helper function is multi-use, substantial in body, a distinct
concern at another abstraction level, or an entry in a dispatch table,
registry, or strategy map.

- **Multi-use**: called from two or more sites. De-duplication is the
  clearest justification.
- **Substantial body**: the logic is long or intricate enough that lifting
  it out makes the caller readable. A one-line or two-line helper called
  once is pure relocation, and belongs inline.
- **Distinct concern at another abstraction level**: the helper's job
  belongs to a different layer than its caller, such as a regex-based
  enforcement check inside a high-level dispatch loop. The name then
  documents the layer boundary.
- **Architectural pluggability**: an entry in a dispatch table, registry,
  or strategy map. These look single-use by static call count and are
  pluggable by design.

These do not justify a helper:

- **Symmetry with siblings**: a trivial single-use function beside two
  siblings of the same shape is still trivial. Each helper stands on its
  own merits.
- **Prior existence**: the bar is the same for a new helper and for one
  inherited from earlier work.
- **Speculative reuse**: extraction waits for the second caller.

## Helper placement

A justified helper sits directly beneath the function that uses it, or in
a `# ---` banner section when several callers share it.

The banner sections let a reader navigate a file by concern rather than by
call graph.

## Formatted by ruff format

The file is byte-identical to `ruff format`'s output under the canonical
`line-length`.

`line-length` is pinned by the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml).

## Annotated signatures

Every function and method annotates each parameter and its return, so the
file passes mypy under the canonical `[tool.mypy]` keys.

[Canonical Artifacts](/standards/build/canonical.md#pyprojecttoml) pins
those keys: `disallow_untyped_defs` and `disallow_incomplete_defs`
together make a partly annotated signature an error.
