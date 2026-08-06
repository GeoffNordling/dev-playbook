---
type: Decision-Record
title: Remove SDD Support Entirely
description: Remove both SDD systems — the factory's ratified retention with its label values, and the specs/ build layer with its Makefile.sdd validate gate — leaving no trace of the methodology outside the Decision Records
date: 2026-08-06
---

# Remove SDD Support Entirely

## Context

Two independent SDD systems survived in this repo, and neither was in use.

**The factory's ratified retention.** `software-factory/software-factory.md`
carried a `### SDD is not supported` section, ratified 2026-07-30: the factory
has no SDD path and intake never mints `mode:sdd` — but the label *values* were
deliberately kept, against a later return. `mode:sdd` and the four `phase:sdd-*`
values sat in [label_scheme.json](/src/dev_playbook/label_scheme.json) and were
minted by [bootstrap-labels](/scripts/bootstrap-labels); they were the third
exemption to the parity invariant that binds the scheme's `phase:*` values to
the workflow graph's nodes; and they drove live branches in
[workspace-lint](/scripts/workspace-lint) — a `mode:sdd`/`tests:yes` pairing
rule and an SDD arm of the brief-heading selector. The methodology also reached
past the factory: [testing conventions](/standards/testing/conventions.md)
admitted three SDD scope roots (`tests/unit/`, `tests/integration/`,
`tests/agent_review/`) as alternative mirror locations because their names are
semantic input to SDD traceability, and required a `@pytest.mark.covers("<id>")`
marker on every test for `pytest-sdd`; the document-type registry carried a
`Spec-Item` row (added by
[0010](/docs/decisions/0010-specs-join-okf.md)); and two standards used
spec-tools citations as their worked examples.

**The `specs/` build layer.** A repo holding a `specs/` directory entered an
`sdd` build layer, which composed the canonical fragment
`standards/build/canonical/Makefile.sdd` — a `validate` target running
`uv run spec-tools validate .`, wired into `check` — with the layer detected,
composed, and shape-checked by [repo-lint](/scripts/repo-lint) and tabled
across five build standards.

Retention was not free. Every change to the label scheme, the brief standard,
or the testing standard had to reason about a dimension nothing answered to,
and each retained value was one more branch for a reader to discount. The
retention's own premise — that the values would be reused on SDD's return — does
not hold: the factory has moved substantially since, so reinstating SDD would be
a fresh design against the factory as it then stands, not a revival of four
parked label values.

## Decision

Remove both systems entirely. No SDD label values, no SDD build layer, no SDD
rules in the testing or docs standards, no spec-tools worked examples. After
this record, the methodology appears nowhere in the repo outside
`docs/decisions/`, which is immutable history.

This reverses the 2026-07-30 ratification's retention clause, and with it the
part of [0010](/docs/decisions/0010-specs-join-okf.md) that put a `Spec-Item`
row in the type registry. [0005](/docs/decisions/0005-issue-workflow-reorganization.md)
and [0007](/docs/decisions/0007-merge-sdd-spec-authoring-phase.md) — which
designed the SDD phases the factory later dropped — stand as history of a path
that no longer exists.

## Scope

The [spec-tools](https://github.com/GeoffNordling/spec-tools) repo is untouched
and out of scope. What is removed here is dev-playbook's *support* for the
methodology — the workspace-wide labels, standards, and build layer that made
SDD a first-class path. Whether spec-tools itself lives on is its own decision.

## Recovery

Everything removed was last alive on `main` at commit
`207a1bf64f4ce3a0df191e479c65609e87d91ec4`, the branch point of
`worktree-simplify`. Recover any file with `git show 207a1bf:<path>`; the two
removal commits on that branch are `Strip the SDD build layer` and
`Un-ratify the SDD retention`, and their diffs are the exact inverse of a
reinstatement.

## Consequences

- `mode:sdd` is now an *invalid* mode value, not a retained one: an issue still
  carrying it draws a tuple-valid finding from workspace-lint. Labels already
  minted on a repo linger in GitHub until deleted by hand — bootstrap-labels
  only adds.
- The parity invariant has two exemptions (pre-issue states, terminal
  endpoints), not three, so the scheme's `phase:*` values and the graph's work
  nodes now match with no residue.
- `tests/` is the only mirror root the testing standard accepts; a repo using
  `tests/unit/` or `tests/integration/` is nonconformant until it flattens.
- A repo holding `specs/` gets no build layer for it. Its `validate` target, if
  it wants one, is local Makefile business rather than a workspace-canonical
  fragment, and repo-lint neither expects nor composes it.
