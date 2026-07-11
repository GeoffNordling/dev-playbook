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

- [python-audit](/scripts/python-audit) — partial: no private-name access
  from tests

## Enforce

- `make check` — pytest at the **push gate** in every Python repo
  ([Makefile.python](/standards/build/canonical/Makefile.python))

## Adopt

- none
