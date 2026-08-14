---
type: Standard-Card
title: Tracking
description: Card for the tracking standard — how committed and uncommitted work is tracked through issue authoring, tracker operations, candidates, and repository settings
---

# Tracking

Governs how work is tracked — committed work as issues, uncommitted work as
candidates, and repository settings. This card owns the **shapes** — what an
issue, a candidate, and a brief must look like — the **labels** an issue carries
to name its state, and the **tracker surface** they live on: the `gh` commands
that create, link, and close an issue. The **lifecycle** those labels name — the
states an issue occupies and the moves between them — is
[the software factory](/software-factory/software-factory.md), as are
[pull requests](/software-factory/factory-operations.md#pull-requests).

## Define

- [standards/tracking/](/standards/tracking/index.md) — the contract:
  candidate conventions, issue authoring, factory labels, tracker operations,
  and repository settings

## Audit

- [workspace-lint](/scripts/workspace-lint) — across repositories via
  `gh api`: GitHub settings drift, the default branch's protection against
  destructive operations, label-scheme parity and the blocked-label
  ban, every open post-intake leaf's four-tuple (`tracking.tuple-valid`) and
  brief shape, every epic's category-only shape, and every wayfinder map's and
  decision ticket's shape
- [repo-lint](/scripts/repo-lint) — a `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or
  `IDEAS.md` at any depth (`tracking.rogue-future-work-file`), and a
  `CANDIDATES.md` outside the repo root (`build.forbidden`)
- [judgments/code-matches-docs.yaml](/judgments/code-matches-docs.yaml) — the
  LLM-judged `scheme-vs-tracker` claim that the label scheme's `wayfinder`
  dimension mints exactly what
  [tracker-operations.md](/standards/tracking/tracker-operations.md#wayfinding-operations)
  states, `scheme-vs-graph` that its factory dimensions mint exactly what
  [factory-labels.md](/standards/tracking/factory-labels.md) states — the
  parity invariant against the factory graph included — and
  `wayfinder-lint-mirrors-skill` that workspace-lint's map and ticket rules
  restate only what the `/wayfinder` skill states

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
