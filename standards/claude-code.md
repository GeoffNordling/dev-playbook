---
type: Standard Card
title: Claude Code Harness Files
description: Card for the Claude Code harness-files standard — how harness-consumed files are distinguished from ordinary files and what each contains
---

# Claude Code Harness Files

Governs how the repo files the Claude Code harness consumes — injected
into context, read as configuration, or run as code — are distinguished
from ordinary files, and what each may contain.

## Define

- [standards/claude-code/](/standards/claude-code/index.md) — the member
  registry and the CLAUDE.md content standard; start at Files
- [Skill Conventions](/standards/claude-code/skill-conventions.md) — the skill-bundle
  format
- [Skill Management](/standards/claude-code/skill-management.md) — where skills live
  and the authored/installed mirror rule

## Audit

- [repo-audit](/scripts/repo-audit) — CLAUDE.md presence and its canonical
  standards block
- [skill-audit](/scripts/skill-audit) — skill bundles in
  skill-authoring repos, plus the `claude-code.skill-mirror`
  correspondence between authored and installed skills (dev-playbook)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — repo-audit at the **commit gate** in every repo's suite;
  skill-authoring repos append skill-audit

## Adopt

- [CLAUDE.md.standards](/standards/build/canonical/CLAUDE.md.standards) —
  the standards block, pasted verbatim into a repo's `CLAUDE.md`
