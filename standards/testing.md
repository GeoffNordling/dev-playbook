---
type: Standard-Card
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

- [testing-lint](/scripts/testing-lint) — the Python-testing detector,
  three rules: no private-name access from tests
  (`testing.no-private-access`), test-file mirror placement
  (`testing.mirror-layout`), and no `if`/`try` logic in a test body
  (`testing.no-logic`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where testing-lint blocks every commit
- `make check-judgments` — the **push gate**, where pytest runs the suite

## Adopt

- none
