---
type: Standard
title: Factory Labels
description: The four-tuple every leaf carries — the factory's fixed-value labels, phase-label naming, and the parity invariant binding them to the graph
---

# Factory Labels

The state of an issue is written on the issue, as labels. This document is the
label contract: which labels exist, what a leaf must carry, and how a phase
label is derived from the node it names. The states themselves — the graph
these labels are read against — are
[the software factory](/software-factory/software-factory.md).

## The four-tuple

Every **leaf** — the unit of work — carries the four-tuple `(category:*,
mode:*, tests:*, phase:*)`, with `phase:*` naming its current node. An
**epic** is not a leaf: it never dispatches and carries `category:*` alone;
its children carry the work. Roles are derived, never labeled
([issue-authoring.md](/standards/tracking/issue-authoring.md)).

An issue is untriaged whether it carries `phase:intake` or no labels at all;
`phase:intake` is the implied default. Issue **relationships** — hierarchy and
blocked-by — are native to GitHub, tracked outside this tuple.

## Valid labels

The factory's labels are exactly these: the fixed-value labels in the table
below, plus one `phase:*` label per work node, derived per [Naming](#naming).
[bootstrap-labels](/scripts/bootstrap-labels) mints them.

The scheme carries dimensions beyond the factory's. Each is governed where it
is defined — `wayfinder` by
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
| Origin | `origin:deferral` | The issue was opened by the factory itself, to hold work a review suggested and the run deferred. |

Every mode either fixes `tests:*` or splits on it, so the four-tuple is complete
on every leaf. Category is required metadata and affects no routing.

`origin:*` is outside the four-tuple. It records where an issue came from rather
than what it is or where it stands, so it rides no leaf's tuple and no leaf is
required to carry one; an issue opened by hand carries none. A deferral stub is
the whole of the dimension today —
[the suggestion dispositions](/software-factory/review-contract.md#suggestion-dispositions)
mint it, at `phase:intake` like any other fresh issue.

## Naming

A phase label is its node id with `_` mapped to `-`, `phase:`-prefixed: node
`pr_review` → label `phase:pr-review`.

**The parity invariant.** The work nodes of
[the factory graph](/software-factory/software-factory.md#the-graph) — its
rectangles and diamonds — mapped that way must equal the scheme's `phase:*`
values exactly. The inventory: `intake, design, spike, build, pr-review`. A
scheme value no node answers to, or a node no scheme value names, is the
violation; the `scheme-vs-graph` judgment enforces it. Exempt, and only these:

- **Pre-issue states** — `CANDIDATES.md` and the idea funnel. No issue exists, so
  there is nothing to label.
- **Terminal endpoints** — merged, closed, escalated. An issue leaves the graph
  there rather than occupying a state. Escalated is where a review loop that
  cannot converge puts the pull request down for the user; the issue keeps
  whatever phase it was in, so no label answers to it.

The factory region's work nodes are served by typed agent definitions that the
traverse script launches — several of them at a review diamond. A
definition-region node is usually served by a slash-command of the same name
(`design` → `/design`), but that mapping is not guaranteed.
