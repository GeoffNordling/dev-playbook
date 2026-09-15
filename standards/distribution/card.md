---
type: Standard-Card
title: Distribution
description: Governs how dev-playbook's checks reach the governed repos — the published hook, the roster, dogfooding, and the pinned rev
---

# Distribution

Governs how dev-playbook's checks reach the governed repos — the published
hook, the roster, dogfooding, and the pinned rev.

## Define

- [Distribution Channel](/standards/distribution/channel.md)

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
- [bump-pin](/scripts/bump-pin) — **on demand**, probes or moves one
  consumer's dev-playbook `rev` against the published head; commits nothing
- [update-standards-pin](/dotfiles/dot-claude/skills/update-standards-pin/SKILL.md)
  — **on demand**, the release runbook run from inside the consumer, which
  carries a green bump to a commit on `main` and a red one to a PR; invoke
  it as /update-standards-pin

The pin sits outside every gate: a stale pin blocks nothing, and
workspace-lint only reports it.

## Adopt

- none
