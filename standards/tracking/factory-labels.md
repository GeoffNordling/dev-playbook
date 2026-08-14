---
type: Standard
title: Factory Labels
description: The four-tuple every leaf carries — the factory's fixed-value labels, phase-label naming, and the parity invariant binding them to the graph
---

# Factory Labels

The state of an issue is written on the issue, as labels. This document is the
label contract: which labels exist, what a leaf must carry, and how a phase
label is derived from the node it names. The states themselves — the graph these
labels are read against — are
[the software factory](/software-factory/software-factory.md).

## The four-tuple

Every **leaf** — the unit of work — carries the full four-tuple `(category:*,
mode:*, tests:*, phase:*)`, with `phase:*` naming its current node. An **epic**
is not a leaf: it never dispatches and carries `category:*` alone; its children
carry the work. Roles are derived, never labeled
([issue-authoring.md](/standards/tracking/issue-authoring.md)).

An untriaged issue may carry `phase:intake` or no labels at all — either way it
is untriaged, with `phase:intake` the implied default. Issue **relationships** —
hierarchy and blocked-by — are native GitHub relationships, tracked outside this
tuple.

## Valid labels

The factory's labels are exactly these: the fixed-value labels in the table
below, plus one `phase:*` label per work node, derived per [Naming](#naming).
[bootstrap-labels](/scripts/bootstrap-labels) mints them.

The scheme carries dimensions beyond the factory's. Each is governed where it is
defined — `wayfinder` by
[Wayfinding operations](/standards/tracking/tracker-operations.md#wayfinding-operations)
— and this doc restates none of their values.

| Dimension | Label | Meaning |
|---|---|---|
| Category | `category:maintenance` | Maintains shipped state — a bug fix, hygiene, or polish that adds no new capability. |
| Category | `category:extension` | Extends a system past its shipped line — a capability it does not have today. |
| Mode | `mode:direct` | The ordinary path: an issue that ends in merged code. |
| Mode | `mode:spike` | A question; the answer closes the issue, no PR. Always `tests:no` — a spike merges nothing. |
| Tests | `tests:yes` | The work writes or modifies tests, so `build` runs it test-first. |
| Tests | `tests:no` | The work touches no tests, so `build` implements directly. |

Every mode either fixes `tests:*` or splits on it, so the four-tuple is complete
on every leaf. Category is required metadata and affects no routing.

## Naming

A phase label is its node id with `_` mapped to `-`, `phase:`-prefixed: node
`pr_review` → label `phase:pr-review`.

**The parity invariant.** The work nodes of
[the factory graph](/software-factory/software-factory.md#the-graph) — its
rectangles and diamonds — mapped that way must equal the scheme's `phase:*`
values exactly. The inventory: `intake, design, spike, build, pr-review`. A
scheme value no node answers to, or a node no scheme value names, is the
violation; the `scheme-vs-graph` judgment enforces it. Two things are exempt,
and only these:

- **Pre-issue states** — `CANDIDATES.md` and the idea funnel. No issue exists, so
  there is nothing to label.
- **Terminal endpoints** — merged, closed. An issue leaves the graph there rather
  than occupying a state.

A work node is usually served by a slash-command of the same name (`design` →
`/design`), but the mapping is not guaranteed: a review diamond dispatches
several skills, none named after the node.
