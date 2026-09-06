---
type: Standard-Card
title: Build
description: Governs how a repository is laid out, built, and checked — the file skeleton, the canonical artifacts, and the Python project
---

# Build

Governs how a repository is laid out, built, and checked — the file
skeleton, the canonical artifacts, and the Python project.

## Define

- [File Skeleton](/standards/build/skeleton.md) — the tree: the entries
  every repo requires, keeps at the root, and forbids, and what each layer
  adds
- [Canonical Artifacts](/standards/build/canonical.md) — the single-source
  files under `standards/build/canonical/` and how each repo's copy is
  compared
- [The Python Project](/standards/build/python.md) — the name mapping,
  scripts, and entry points

## Audit

- [repo-lint](/scripts/repo-lint) — structural conformance and canonical
  comparison for one repository

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the hook suite every repo runs at the **commit gate**; repo-lint
  reaches it through the published `playbook-lint` hook, which dispatches
  to the whole roster
- `make check-judgments-cache` ([Makefile.base](/standards/build/canonical/Makefile.base))
  — the **push gate**
- thin CI ([ci.yml](/standards/build/canonical/ci.yml)) — the **CI gate**,
  the same suite on every push and PR, less `ref-lint`: its cross-repo
  citations cannot resolve in a one-repo checkout

## Adopt

- [Bootstrap](/standards/build/bootstrap.md) — how a repository joins the
  workspace: scaffold a fresh repo with `repo-init` or adopt an existing one
  to green, then the GitHub tail and roster enrollment
- [enable-repo-governance](/dotfiles/dot-claude/skills/enable-repo-governance/SKILL.md)
  — the adoption path's runbook: preflight, the findings loop, the hand-offs,
  and the landing; invoke it as /enable-repo-governance
