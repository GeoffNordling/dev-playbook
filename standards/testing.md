---
type: Standard-Card
title: Python Testing
description: Governs how Python tests are written — the pytest framework, mirror layout, test structure, behavioral focus, doubles, and fixtures
---

# Python Testing

Governs how Python tests are written — the pytest framework, mirror layout,
test structure, behavioral focus, doubles, and fixtures. The boundary with
[Build](/standards/build.md): that a repo has a `tests/` directory at all is
File Skeleton's rule, and everything inside it is this card's.

## Define

- [testing/conventions.md](/standards/testing/conventions.md) — the
  contract: framework, layout, structure, behavioral focus, doubles,
  fixtures

## Audit

- [testing-lint](/scripts/testing-lint) — the Python-testing detector,
  three rules: no private-name access from tests
  (`testing.no-private-access`), test-file mirror placement
  (`testing.mirror-layout`), and no `if`/`try` logic in a test body
  (`testing.no-logic`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where testing-lint blocks every commit by way of
  the published `playbook-lint` hook

## Adopt

- none
