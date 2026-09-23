---
type: Standard
title: Testing Conventions
description: Where a repo's Python test files and fakes live — test file naming, the mirror layout, and the home of a fake
population: "a governed repo's Python test suite: the test_*.py files anywhere in its tree, and the conftest.py and fake modules under tests/"
---

# Testing Conventions

A governed repo's Python test suite is one object: every `test_*.py` file
anywhere in the tree, together with the `conftest.py` files and the fake
modules under `tests/`. A rule about where a fixture or a fake lives binds
the suite as surely as a rule about a test body does. That `tests/` exists
at all is
[File Skeleton](/standards/build/skeleton.md#tests-present)'s rule; what
goes where inside it is this Standard's.

## Test files carry the test prefix

Every `.py` file that defines, at module level, a function whose
name begins `test_` or a class whose name begins `Test` is named
`test_*.py`.

`testing.test-files-carry-the-test-prefix` · deterministic

## Test tree mirrors the source tree

Take a file `tests/**/test_<name>.py` where at least one module
`src/<dir>/<name>.py` exists, other than `__init__.py`. The file is
at `tests/<dir>/test_<name>.py`,
`tests/unit/<dir>/test_<name>.py`, or
`tests/integration/<dir>/test_<name>.py`. Example:
`src/auth/login.py` is tested at `tests/auth/test_login.py`. When
more than one module has the name `<name>.py`, the mirror of any
one of them passes.

`testing.test-tree-mirrors-the-source-tree` · deterministic

> **Why.** Mirroring scales with the source tree and keeps two modules
> of the same file name from colliding.

## Fakes live in the test tree

A fake lives under `tests/`, in `tests/fakes.py` or beside the tests that
use it.

`testing.fakes-live-in-the-test-tree` · stochastic
