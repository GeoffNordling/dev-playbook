---
type: Standard
title: Testing Conventions
description: Where a repo's Python test files, fixtures, and fakes live — test file naming, the mirror layout, the conftest hierarchy, and the home of a fake
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

Every test file in the suite is named `test_*.py`.

`testing.test-files-carry-the-test-prefix` · deterministic

## Test tree mirrors the source tree

A `test_*.py` file under `tests/` whose name, with the `test_` prefix
removed, is the file name of a module under `src/` other than an
`__init__.py` sits at that module's mirror: `tests/`, then the module's
directory path below `src/`, then the file name with `test_` prefixed, so
that `src/auth/login.py` is tested at `tests/auth/test_login.py`; or at
that same path beneath one of the two scope directories `unit` and
`integration`, as `tests/unit/auth/test_login.py`. Where the file name
belongs to more than one module under `src/`, the mirror of any one of
them satisfies the rule.

`testing.test-tree-mirrors-the-source-tree` · deterministic

> **Why.** Mirroring scales with the source tree and keeps two modules
> of the same file name from colliding.

## Fixture lives in the narrowest conftest

A fixture lives in the `conftest.py` of the narrowest directory whose tests
use it.

`testing.fixture-lives-in-the-narrowest-conftest` · deterministic

## Fakes live in the test tree

A fake lives under `tests/`, in `tests/fakes.py` or beside the tests that
use it.

`testing.fakes-live-in-the-test-tree` · stochastic
