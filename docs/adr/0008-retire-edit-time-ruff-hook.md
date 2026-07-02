---
type: ADR
title: Retire the Edit-Time ruff Hook for a Single Pre-commit Gate
description: Remove the edit-time PostToolUse ruff hook so pre-commit is the single ruff gate over every authored .py
---

# Retire the Edit-Time ruff Hook for a Single Pre-commit Gate

**Status:** Supersedes [ADR-0002](0002-compounding-with-ai.md)'s edit-time-hook decisions in part (issue #127); its tiered-instruction decisions stand.

## Decision

Delete the `PostToolUse` ruff hook — `dotfiles/dot-claude/hooks/ruff-edit.sh` and its `settings.json` entry. **Pre-commit is the single ruff gate.** ruff's rules, version, and exclusions stay per-repo in each repo's `pyproject.toml` + `.pre-commit-config.yaml`, as they already are. No dev-playbook-published ruff hook.

## Why

The hook resolved ruff by walking up to `.venv/bin/ruff`, which fails on every `.py` under `dotfiles/` — dev-playbook's venv is at `tools/.venv`, a sibling not an ancestor (issue #127). Its fail-loud remedy (`uv sync` at the repo root) then spawned a stray root venv.

It was never needed for coverage: pre-commit already lints every authored `.py` — dotfiles skill scripts under `dot-claude/skills/**/scripts/` included — excluding only the vendored `dotfiles/.agents/` and `.dhub/` trees. So the hook merely ran ruff a second, independently-resolved way, reintroducing the version-drift ADR-0002 warned against.

**Cost:** no more mid-edit lint feedback; ruff now surfaces at commit and CI. ADR-0002's 2026-06-06 amendment already floated moving all checking onto pre-commit.
