---
type: Standard-Card
title: Tracking
description: Governs how work is tracked — candidates, issue shapes, the label scheme, and repository settings
---

# Tracking

Governs how work is tracked — candidates, issue shapes, the label
scheme, and repository settings. This card owns the **shapes** a
candidate and an issue take, the **labels** a tracker mints and an issue
carries, and the **settings** the tracker they live on assumes. The
lifecycle the phase labels name is
[the software factory](/software-factory/software-factory.md), as are
[pull requests](/software-factory/factory-operations.md#pull-requests).

## Define

- [Candidates](/standards/tracking/candidates.md) — the `CANDIDATES.md`
  register: the only future-work file, entry shape, structure, and
  promotion
- [Issue Shapes](/standards/tracking/issue-shapes.md) — the five species
  of issue, the labels and body headings each carries, and the rules
  every body obeys
- [Label Scheme](/standards/tracking/label-scheme.md) — the closed-world
  label set, generated from the scheme data, and no blocked label
- [Repository Settings](/standards/tracking/repo-settings.md) — a GitHub
  origin, squash-only merges, and a default branch protected from
  destructive operations

## Audit

- [workspace-lint](/scripts/workspace-lint) — across repositories via
  `gh api`: a missing GitHub origin, settings drift, and the default
  branch's protection (`tracking.remote`, `tracking.settings`,
  `tracking.branch-protection`); label-scheme parity and the
  blocked-label ban (`tracking.label-scheme`, `tracking.no-blocked-label`);
  every open post-intake leaf's labels and brief shape
  (`tracking.tuple-valid`, `tracking.issue-brief-shape`); every session
  leaf's labels (`tracking.session-shape`); every epic's category-only
  shape (`tracking.epic-shape`); and every wayfinder map's and decision
  ticket's shape (`tracking.wayfinder-shape`)
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
  inside the file is convention, not a checked rule
- [bootstrap-labels](/scripts/bootstrap-labels) — **on demand**, rewrites
  the current repo's labels into the scheme: every canonical label
  created or updated, every other label deleted, idempotent — the same
  set workspace-lint reports

GitHub itself sits outside every gate: workspace-lint reports and
bootstrap-labels repairs, but nothing blocks a malformed issue, a drifted
label, or a drifted setting. Settings repairs stay manual: admin
permissions are too broad to automate.

## Adopt

- none
