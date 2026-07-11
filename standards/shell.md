---
type: Standard Card
title: Shell
description: Card for the shell standard — how shell is written
---

# Shell

Governs how shell is written.

## Define

- [shell/conventions.md](/standards/shell/conventions.md) — the contract:
  the glue boundary, strict mode, declared bash, shellcheck-clean

## Audit

- shellcheck — third-party lint detector, located by its pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
- shfmt — third-party formatting detector, located by its pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
- third-party detectors only, by choice: rules 1–3 of the contract (boundary,
  strict mode, declared bash) are prose the reviewer checks, so no first-party
  shell detector exists — a chosen gap, not a forgotten one

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where shellcheck and shfmt block every commit

## Adopt

- none
