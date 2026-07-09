---
type: Standard Card
title: Python Testing
description: Card for the Python-testing standard — how Python tests are written
---

# Python Testing

Governs how Python tests are written.

## Define

- [testing/conventions.md](/standards/testing/conventions.md) — the
  contract: structure, behavioral focus, test doubles, fixtures, humble
  objects

## Audit

- [python-lint](/scripts/python-lint) — partial: no private-name access
  from tests

## Enforce

- `make check` — pytest in every Python repo's local gate
  ([Makefile.python](/standards/build/canonical/Makefile.python))

## Adopt

- none
