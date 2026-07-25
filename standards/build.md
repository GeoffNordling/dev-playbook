---
type: Standard-Card
title: Build
description: Card for the build standard — how a repository is laid out, built, and checked
---

# Build

Governs how a repository is laid out, built, and checked.

## Define

- [standards/build/](/standards/build/index.md) — the contract, one concern
  per document; start at Layers
- [Canonical Artifacts](/standards/build/canonical.md) — the single-source
  files under `standards/build/canonical/` and how each repo copy is
  compared

## Audit

- [repo-lint](/scripts/repo-lint) — structural conformance and canonical
  byte comparison for one repository
- [workspace-lint](/scripts/workspace-lint) — pin drift across the governed
  repos: a stale pinned hook rev, or none at all

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the hook suite every repo runs at the **commit gate**; repo-lint
  reaches it through the published `playbook-lint` hook, which dispatches
  to the whole roster
- `make check-judgments` ([Makefile.base](/standards/build/canonical/Makefile.base))
  — the **push gate**
- thin CI ([ci.yml](/standards/build/canonical/ci.yml)) — the **CI gate**,
  the same suite on every push and PR, less `ref-lint`: its cross-repo
  citations cannot resolve in a one-repo checkout

## Adopt

- none
