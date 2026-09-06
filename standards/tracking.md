---
type: Standard-Card
title: Tracking
description: Governs how work is tracked — candidates, issue authoring, the label scheme, and repository settings
---

# Tracking

Governs how work is tracked — candidates, issue authoring, the label
scheme, and repository settings. This card owns the **shapes** — what a
candidate, an issue, and a brief must look like — the **labels** a tracker
mints and an issue carries to name its state, and the **settings** the
tracker they live on assumes. The **lifecycle** those labels name — the
states an issue occupies and the moves between them — is
[the software factory](/software-factory/software-factory.md), as are
[pull requests](/software-factory/factory-operations.md#pull-requests).

## Define

- [Candidates](/standards/tracking/candidates.md) — the `CANDIDATES.md`
  register: the only future-work file, entry shape, structure, and
  promotion
- [Issue Authoring](/standards/tracking/issue-authoring.md) — an issue's
  derived role and its labels, readiness, the three brief formats, the
  wayfinder shapes, native relationships, and the rules every brief obeys
- [Label Scheme](/standards/tracking/label-scheme.md) — the labels a
  repo's tracker mints: every dimension's values, phase labels derived
  from the factory graph, and no blocked label
- [Repository Settings](/standards/tracking/repo-settings.md) — a GitHub
  origin, squash-only merges, and a default branch protected from
  destructive operations

## Audit

- [workspace-lint](/scripts/workspace-lint) — across repositories via
  `gh api`: a missing GitHub origin, settings drift, and the default
  branch's protection (`tracking.remote`, `tracking.settings`,
  `tracking.branch-protection`); label-scheme parity and the
  blocked-label ban (`tracking.label-scheme`, `tracking.no-blocked-label`);
  every open post-intake leaf's four-tuple and brief shape
  (`tracking.tuple-valid`, `tracking.issue-brief-shape`); every epic's
  category-only shape (`tracking.epic-shape`); and every wayfinder map's
  and decision ticket's shape (`tracking.wayfinder-shape`)
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
- [bootstrap-labels](/scripts/bootstrap-labels) — **on demand**, rewrites
  the current repo's labels into the scheme: every canonical label
  created or updated, every other label deleted, idempotent — the same
  set workspace-lint reports

GitHub itself sits outside every gate: workspace-lint reports, the weekly
ritual and bootstrap-labels repair, but nothing blocks a malformed issue, a
drifted label, or a drifted setting. Settings repairs stay manual — admin
permissions are too broad to automate, so no repair tool is built.

## Adopt

- none
