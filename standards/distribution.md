---
type: Standard-Card
title: Distribution
description: Governs how dev-playbook's checks reach the governed repos — the published hook, the roster, dogfooding, and the pinned rev
---

# Distribution

Governs how dev-playbook's checks reach the governed repos — the published
hook, the roster, dogfooding, and the pinned rev.

## Define

- [Distribution Channel](/standards/distribution/channel.md) — the one
  published id, the roster, a publisher's local block, and a consumer's
  pinned rev

## Audit

- [workspace-lint](/scripts/workspace-lint) — a governed repo with no
  dev-playbook pin (`distribution.pin`), and a stale pin, advisory
- [repo-lint](/scripts/repo-lint) — a publisher whose local block omits an
  id its manifest publishes (`distribution.dogfood`)

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — repo-lint's dogfood check at the **commit gate**, through the
  published `playbook-lint` hook
- [bump-pins](/scripts/bump-pins) — **on demand**, moves the dev-playbook
  `rev` across the governed consumers and re-runs each one's commit gate;
  commits nothing
- [update-standards-pin](/dotfiles/dot-claude/skills/update-standards-pin/SKILL.md)
  — **on demand**, the release runbook that carries the bump through to
  each consumer's commit; invoke it as /update-standards-pin

The pin sits outside every gate: a stale pin blocks nothing, and
workspace-lint only reports it.

## Adopt

- none
