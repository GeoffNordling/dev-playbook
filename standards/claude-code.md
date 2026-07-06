---
type: Standard Card
title: Claude Code Harness Files
description: Card for the Claude Code harness-files standard — which repo files the harness consumes and what each contains
---

# Claude Code Harness Files

Governs which repo files the Claude Code harness consumes — injected into
context, read as configuration, or run as code — and what each contains.

## Define

- [standards/claude-code/](/standards/claude-code/index.md) — the member
  registry and the CLAUDE.md content standard; start at Files
- [Skill Conventions](/standards/skill-conventions.md) — the skill-bundle
  format
- [Skill Management](/standards/skill-management.md) — where skills live
  and the authored/installed mirror rule

## Audit

- [repo-audit](/scripts/repo-audit) — CLAUDE.md presence and its canonical
  standards block
- [internal-skill-audit](/scripts/internal-skill-audit) — skill bundles in
  skill-authoring repos

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — repo-audit in every repo's suite; skill-authoring repos append
  internal-skill-audit

## Adopt

- [CLAUDE.md.standards](/standards/build/canonical/CLAUDE.md.standards) —
  the standards block, pasted verbatim into a repo's `CLAUDE.md`
