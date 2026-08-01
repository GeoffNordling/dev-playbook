---
type: Decision-Record
title: One Published Hook — Enrollment Rides the Pin
description: Collapse the published per-detector hook ids into one playbook-lint aggregate whose in-clone roster enrolls every consumer at pin bump
date: 2026-07-24
---

# One Published Hook — Enrollment Rides the Pin

**Status:** Accepted.

## Decision

Publish exactly one pre-commit hook, `playbook-lint`. Its roster
(`DETECTORS` in `src/dev_playbook/playbook_lint.py`) ships inside the pinned
clone and dispatches every commit-gate detector; the per-detector ids leave
the manifest, the canonical template's pinned block shrinks to the single id,
and dev-playbook's dogfood block mirrors it. Adding a detector to the roster
is enrolling it workspace-wide — a consumer's only action is the pin bump it
already performs.

Consequential removals and reworks:

- **`build.skills-hook` is deleted.** It demanded consumers hand-carry
  `- id: skill-lint`, the opt-in shape this decision abolishes; skill-lint
  now runs everywhere by construction.
- **`validate-manifest` folds into the dispatcher**, running only where the
  audited repo publishes a `.pre-commit-hooks.yaml`.
- **`SKIP` is honored by detector name inside the dispatcher** — pre-commit's
  own `SKIP` keys on config hook ids, which no longer name detectors — so the
  canonical CI workflow's `SKIP: ref-lint` and one-off developer skips keep
  their exact spelling.
- **standards-lint's hook-surfaces rule reads the roster**, not the config,
  as dev-playbook's detector enumeration, and gains a closure leg: a script
  cited by a card's Audit cell that is neither in the roster nor a registered
  ungated audit (workspace-lint) is a finding — a detector card cannot be
  authored without gating its detector.

## Why

Consumers subscribed to detectors by hand-listing `- id:` lines.
`pre-commit autoupdate` moves `rev` but never adds hook entries, so a
detector published after a consumer's pin reached that repo only by hand —
enrollment was opt-in by construction, backwards for a workspace whose
standards ride downhill. The check that should have caught under-enrollment,
repo-lint's canonical-block compare, ships inside the same pinned clone: at a
stale pin it compared the consumer against the stale canonical block and
passed. story-forge sat one release behind and never ran standards-lint or
validate-manifest, green the whole time.

With one id there is nothing to enumerate, so nothing to under-enumerate:
the pin bump is the complete release, detectors included.

**Costs:** per-hook `SKIP` granularity and pre-commit's per-hook status lines
move into the dispatcher (which prints per-detector summaries and names the
red detectors in its roll-up); ref-lint's `types: [markdown]` gate is gone —
it now runs on every commit like the other always-run detectors; migration is
a hard cut — at the first pin bump past this decision, pre-commit fails loud
on the retired ids until the consumer swaps its eleven hook lines for the one
id, which the canonical-block compare at that same rev then enforces.
Dispatch is concurrent with output in roster order, so the aggregate is
faster than the eleven serial hooks it replaces.
