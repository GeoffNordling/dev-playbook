---
type: General-Sheet
title: Tracking
description: The rewrite of the tracking family's seventeen deterministic rules — one check over the model, fourteen registered to workspace-lint, two deleted per their escalations, four Standards edited to the triage, and nothing retired
---

# Tracking

The step built `src/dev_playbook/checks/tracking.py` and
`tests/dev_playbook/checks/test_tracking.py` from
[the tracking triage](/working-docs/doc-type-system/detector-rewrite/triage/tracking.md).
`scripts/workspace-lint` and `src/dev_playbook/workspace_lint.py` are
unchanged.

## Built

- `tracking.one-list-item-per-entry`: function
  `one_list_item_per_entry`, a new check over the root
  `CANDIDATES.md`, per Escalation 1. The escalation's blockquote
  replaced the body in `standards/tracking/candidates.md`; the sentence
  limit is gone. 31 list items today, 0 findings.
- `tracking.origin-on-github`: hook `workspace-lint`. Kept as written.
- `tracking.squash-only-merges`: hook `workspace-lint`. The blockquote
  replaced the sentence above the table in
  `standards/tracking/github-settings.md`.
- `tracking.default-branch-protected-from-destructive-operations`: hook
  `workspace-lint`. The blockquote replaced the body above the table.
- `tracking.closed-fences`, `tracking.one-label-from-each-prefix`,
  `tracking.every-build-heading-in-bold`,
  `tracking.one-label-from-each-prefix-tests-fixed-at-no`,
  `tracking.summary-question-and-deliverable`,
  `tracking.one-category-label-no-phase-or-tests`,
  `tracking.every-session-heading-in-bold`, `tracking.category-only`,
  `tracking.one-wayfinder-label-and-nothing-else`, and
  `tracking.map-sections-ticket-question`: hook `workspace-lint`. Each
  blockquote replaced its body in `standards/tracking/issue-shapes.md`;
  the example blocks and the Why are unchanged.
- `tracking.exactly-the-labels-the-scheme-declares`: hook
  `workspace-lint`. The blockquote replaced the body in
  `standards/tracking/label-scheme.md`.

The five species definitions in `issue-shapes.md` now say "has" where
they said "carries", as the triage's `issue-shapes.md` section asks.

## Deleted

- `tracking.outcome-and-decomposition-rationale`, per Escalation 2:
  heading, body, example block, and trailer removed. Two links pointed
  at the heading, in `working-docs/software-factory/docs/software-factory.md`
  and `working-docs/software-factory/skills/wayfinder-to-build/SKILL.md`;
  both now point at `#no-child-list`, the surviving rule on an epic's
  body.
- `tracking.ticket-under-a-map`, per Escalation 3: heading, body, and
  trailer removed. No link pointed at the heading.

Neither deletion empties its condition, and `workspace-lint` never
emitted either id.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.39 s, 16 checks over 448 files, zero
  findings.
- `scripts/playbook-lint .`: 0.24 s, clean.

## Acronyms

None.
