---
type: Standard-Card
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

- [repo-lint](/scripts/repo-lint) — CLAUDE.md presence and its canonical
  standards block; the agent-facing voice of every CLAUDE.md, root to global
  (`claude-code.agent-facing-voice`); and, in dev-playbook only, the global
  CLAUDE.md source's two-element XML shape and well-formedness
  (`claude-code.global-claude-shape`, `claude-code.global-claude-wellformed`)
- [skill-lint](/scripts/skill-lint) — skill bundles in
  skill-authoring repos, plus the `claude-code.skill-mirror`
  correspondence between authored and installed skills (dev-playbook)
- [judgements/claude-code.yaml](/judgements/claude-code.yaml) — the LLM-judged
  claim that the root and global CLAUDE.md genuinely read as agent-facing
  voice, the semantic check the token-level rule cannot make

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — repo-lint and skill-lint both at the **commit gate** in every repo's
  suite; skill-lint no-ops where a repo authors no skills

## Adopt

- [CLAUDE.md.standards](/standards/build/canonical/CLAUDE.md.standards) —
  the standards block, pasted verbatim into a repo's `CLAUDE.md`
