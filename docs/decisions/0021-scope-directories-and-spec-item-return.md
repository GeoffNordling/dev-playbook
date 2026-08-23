---
type: Decision-Record
title: Scope Directories and Spec-Item Return — Partially Reversing 0017
description: Readmit unit/integration scope directories as mirror roots and the Spec-Item registry row — generically framed workspace vocabulary, with the rest of 0017 standing
date: 2026-08-11
---

# Scope Directories and Spec-Item Return — Partially Reversing 0017

## Context

[0017](/docs/decisions/0017-remove-sdd-support.md) removed dev-playbook's SDD
support end-to-end, and among its removals were two pieces the governed
population still needs. A family of spec-driven consumer repos — spec-tools
first, with more expected on the same layout — splits `tests/` into `unit/`,
`integration/`, and `agent_review/` scope directories and types its spec
documents `Spec-Item`; at any current pin, testing-lint flags every scoped
mirror in such a repo and okf-lint flags every spec document.

## Decision

Readmit both, framed as generic workspace vocabulary rather than SDD support:

- **Scope directories are layout, not methodology.** `testing.mirror-layout`
  accepts a module's mirror flat (`tests/x/test_y.py`) or beneath the
  recognized scope directories `unit` and `integration`; `tests/agent_review/`
  holds free-stem judgment gate tests
  ([cache-gate.md](/standards/semantic-validation/cache-gate.md)) and sits outside the
  rule. 0017 dropped the scopes because their names were semantic input to SDD
  traceability; they return with no such semantics attached — `unit` and
  `integration` are plain pytest vocabulary, and `agent_review` is workspace
  judgments vocabulary. The set is fixed rather than open so a misplacement
  cannot masquerade as a scope.
- **`Spec-Item` returns to the global type registry**, reinstating the part of
  [0010](/docs/decisions/0010-specs-join-okf.md) that 0017 reversed, with a
  generic one-line description. The registry places a type where its document
  population lives; this population spans the whole spec-driven family, and the
  two-level registry offers no shared tier between sibling consumers short of
  the global table — per-repo extensions would be N identical copies with
  nothing checking their agreement.

The rest of 0017 stands: no SDD labels or build layer, no `covers` markers, no
spec-tools worked examples in standards, and a `validate` target stays local
Makefile business.
