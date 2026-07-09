---
type: Standard Card
title: Tracking
description: Card for the tracking standard — how work is tracked through issues, pull requests, and repository settings
---

# Tracking

Governs how work is tracked — issues, pull requests, and repository
settings.

## Define

- [standards/tracking/](/standards/tracking/index.md) — the contract:
  issue conventions and repository settings

## Audit

- [sweep](/scripts/sweep) — GitHub settings drift across repositories via
  `gh api`

## Enforce

- none — sweep reports and bootstrap-labels repairs, but nothing blocks a
  malformed issue or a drifted setting

## Adopt

- [bootstrap-labels](/scripts/bootstrap-labels) — mints the canonical
  label scheme in the current repo
