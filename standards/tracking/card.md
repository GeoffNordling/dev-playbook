---
type: Standard-Card
title: Tracking
description: Governs how work is tracked — issue shapes, the label scheme, and repository settings
---

# Tracking

Governs how work is tracked — issue shapes, the label scheme, and
repository settings. This card owns the **shapes** an issue takes, the **labels** a tracker mints and an issue
carries, and the **settings** the tracker they live on assumes. The
lifecycle the phase labels name is the software factory's, isolated
under `working-docs/software-factory/` and out of scope.

## Define

- [Candidates](/standards/tracking/candidates.md)
- [Issue Shapes](/standards/tracking/issue-shapes.md)
- [Label Scheme](/standards/tracking/label-scheme.md)
- [Repository Settings](/standards/tracking/repo-settings.md)

## Audit

- [workspace-lint](/scripts/workspace-lint) — across repositories via
  `gh api`: a missing GitHub origin, settings drift, and the default
  branch's protection (`tracking.github-origin`, `tracking.squash-only-merges`,
  `tracking.default-branch-protection`); label-scheme parity
  (`tracking.valid-labels`); every open post-intake leaf's labels,
  headings, and fences (`tracking.build-labels`, `tracking.build-headings`,
  `tracking.spike-labels`, `tracking.spike-headings`,
  `tracking.closed-fences`); every session
  leaf's labels (`tracking.session-labels`); every epic's category-only
  labels (`tracking.category-only`); and every wayfinder map's and decision
  ticket's labels and body (`tracking.wayfinder-labels`,
  `tracking.wayfinder-body`)

A `CANDIDATES.md` carries `Candidate-List` frontmatter and an index entry like
any concept doc; okf-lint checks both under the
[knowledge-organization](/standards/knowledge-organization/card.md) card's rules, not
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
