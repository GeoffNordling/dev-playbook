---
type: Standard-Card
title: Tracking
description: Card for the tracking standard — how committed and uncommitted work is tracked through issues, candidates, and repository settings
---

# Tracking

Governs how work is tracked — committed work as issues, uncommitted work as
candidates, and repository settings. Pull requests belong to the
[software factory standard](/software-factory/software-factory.md).

## Define

- [standards/tracking/](/standards/tracking/index.md) — the contract:
  candidate conventions, issue authoring, tracker operations, and repository
  settings

## Audit

- [workspace-lint](/scripts/workspace-lint) — across repositories via
  `gh api`: GitHub settings drift, label-scheme parity and the blocked-label
  ban, and every open post-intake leaf's brief shape and every epic's
  category-only shape
- [repo-lint](/scripts/repo-lint) — a `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or
  `IDEAS.md` at any depth (`tracking.rogue-future-work-file`), and a
  `CANDIDATES.md` outside the repo root (`build.forbidden`)

A `CANDIDATES.md` carries `Candidate-List` frontmatter and an index entry like
any concept doc; okf-lint checks both under the
[knowledge-organization](/standards/knowledge-organization.md) card's rules, not
this one's.

## Enforce

- **commit gate** — the tree half only: repo-lint blocks a rogue `ROADMAP.md`,
  `TODO.md`, `BACKLOG.md`, or `IDEAS.md` anywhere in the tree. Entry shape
  inside the file is convention, not a checked rule — a candidate register that
  drifts into a shadow issue tracker is an authoring problem, not a detector
  gap
- GitHub itself sits outside every gate: workspace-lint reports, the weekly
  ritual and bootstrap-labels repair, but nothing blocks a malformed issue, a
  drifted label, or a drifted setting. Settings repairs stay manual — admin
  permissions are too broad to automate, so no repair tool is built

## Adopt

- [bootstrap-labels](/scripts/bootstrap-labels) — mints the canonical
  label scheme in the current repo
