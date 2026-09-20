---
type: Guide
title: Python Guide
description: The thinking behind the Python style rules — why an init is empty, which docstrings matter, what a fallback hides, where a constant sits, why future annotations are gone, what justifies a helper, and which tool decides each rule
---

# Python Guide

The guide behind [Python Style](/standards/python/style.md), the
ruleset that binds a Python file a governed repo tracks. This guide
carries the reasoning and the examples; nothing here is enforced.

## Why an init is empty

An `__init__.py` holds nothing, ideally zero bytes
([Empty init](/standards/python/style.md#empty-init)); every import,
re-export, and `__all__` declaration sits in a named module instead.
Callers then import from the specific submodule,
`from pkg.sub import thing`, rather than from the package root, and a
package's overview belongs in its primary named module or in a README.

## Which docstrings matter

One short sentence is enough when the behavior is simple, longer when
it is not ([Docstrings](/standards/python/style.md#docstrings)). A
pytest test function follows a `test_<behavior>` naming convention
literal enough that a docstring restates the name, which is why it is
exempt. A test module's own helpers, the factories and fixtures defined
as plain functions, carry docstrings: their names are not similarly
load-bearing.

## What a fallback hides

A value the code requires is read directly, so a missing one raises:
`dict[key]` raises `KeyError`, `obj.attr` raises `AttributeError`, and
each points straight at the defect
([Fail loudly](/standards/python/style.md#fail-loudly)). A fallback
that hides a bug delays the failure to a place far from the cause,
where it is much harder to diagnose. A legitimate fallback is one where
the missing value is a real runtime state rather than a programming
error, and its inline comment is the signal that the author weighed it.

## Where a constant sits

A module reads top to bottom in one order
([Module layout](/standards/python/style.md#module-layout)). A
single-use constant sits at the top with the rest, or, when it is
derived, in its grouped section directly after what it derives from,
never beside its one user mid-file. The `# ---` banner sections that
hold shared helpers
([Helper placement](/standards/python/style.md#helper-placement)) let
a reader navigate a file by concern rather than by call graph.

## Why future annotations are gone

Python 3.11 and later already provide every motivation for
`from __future__ import annotations`: PEP 604 unions, `X | Y`, builtin
generics, `list[int]`, and string-quoted forward references
([No future annotations](/standards/python/style.md#no-future-annotations)).

## What justifies a helper

De-duplication is the clearest justification: a helper called from two
or more sites earns its name
([Helper justification](/standards/python/style.md#helper-justification)).
A substantial body earns it too, when lifting the logic out makes the
caller readable; a one-line or two-line helper called once is pure
relocation and belongs inline. A helper at another abstraction level, a
regex check inside a high-level dispatch loop, earns it because the
name then documents the layer boundary. An entry in a dispatch table
looks single-use by static call count and is pluggable by design.

Symmetry with siblings, prior existence, and speculative reuse justify
nothing: a trivial single-use function beside two siblings of the same
shape is still trivial, the bar is the same for a new helper and for
one inherited from earlier work, and extraction waits for the second
caller.

## Which tool decides each rule

`ruff format` owns line length, under the `line-length` the canonical
[pyproject.toml](/standards/build/canonical.md#pyprojecttoml) pins,
which is why the `E501` lint rule is off
([Formatted by ruff format](/standards/python/style.md#formatted-by-ruff-format)).
`ruff check`'s `D` family decides docstring presence. mypy decides
annotated signatures: the canonical `disallow_untyped_defs` and
`disallow_incomplete_defs` together make a partly annotated signature
an error
([Annotated signatures](/standards/python/style.md#annotated-signatures)).
python-lint decides the empty init and the future import. The rest is
a reviewer's.
