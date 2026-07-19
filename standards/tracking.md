---
type: Standard-Card
title: Tracking
description: Card for the tracking standard — how work is tracked through issues and repository settings
---

# Tracking

Governs how work is tracked — issues and repository settings. Pull
requests belong to the [software factory standard](/software-factory/software-factory.md).

## Define

- [standards/tracking/](/standards/tracking/index.md) — the contract:
  issue conventions and repository settings

## Audit

- [workspace-audit](/scripts/workspace-audit) — across repositories via
  `gh api`: GitHub settings drift, label-scheme parity and the blocked-label
  ban, and every open post-intake leaf's brief shape and every epic's
  category-only shape

## Enforce

- none — GitHub sits outside every gate: workspace-audit reports, the weekly
  ritual and bootstrap-labels repair, but nothing blocks a malformed issue, a
  drifted label, or a drifted setting. Settings repairs stay manual — admin
  permissions are too broad to automate, so no repair tool is built

## Adopt

- [bootstrap-labels](/scripts/bootstrap-labels) — mints the canonical
  label scheme in the current repo
