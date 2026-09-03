---
type: Standard-Card
title: Shell
description: Governs how shell is written — the glue-only boundary, strict mode, declared bash, and the shellcheck and shfmt bars every file clears
---

# Shell

Governs how shell is written — the glue-only boundary, strict mode,
declared bash, and the shellcheck and shfmt bars every file clears.

## Define

- [shell/conventions.md](/standards/shell/conventions.md) — a shell file:
  the glue boundary, strict mode, declared bash, and the shellcheck and
  shfmt bars

## Audit

- shellcheck — third-party lint detector, located by its pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
- shfmt — third-party formatter, a detector in its diff mode (`shfmt -d`);
  the commit gate stations its write mode, located by its pin in the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)

Third-party detectors only, by choice: shellcheck proves **shellcheck-clean**
and shfmt proves **Formatting**, while **Glue only**, **Strict mode**, **Bash,
declared**, **Disable carries a reason**, **No shebang, no strict mode**,
**Dialect directive**, and **Bounded to shell integration** are prose the
reviewer checks. No first-party shell detector exists: a chosen gap, not a
forgotten one.

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where shellcheck blocks every commit and shfmt
  rewrites the file in place

## Adopt

- none
