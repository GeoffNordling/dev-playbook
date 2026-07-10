---
type: Standard Card
title: Shell
description: Card for the shell standard — how shell is written
---

# Shell

Governs how shell is written.

## Define

- none — shellcheck enforces a standard no prose states; writing the
  contract is an open conformance gap

## Audit

- shellcheck — the third-party detector; read-only on any shell file, run
  ad hoc or by the suite. Its only workspace home is its pin in the
  canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the venue where shellcheck blocks every commit

## Adopt

- none
