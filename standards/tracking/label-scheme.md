---
type: Standard
title: Label Scheme
description: The labels a governed repo's tracker mints — the fixed-value labels of every dimension, phase labels derived from the factory graph, and the blocked-label ban
population: "a governed repo's GitHub labels"
---

# Label Scheme

The labels a governed repo's tracker mints. The state of an issue is
written on the issue as labels, so the scheme is closed-world: which
labels exist is fixed here and, as data, in
`src/dev_playbook/label_scheme.json`, and
[bootstrap-labels](/scripts/bootstrap-labels) mints the scheme into a
repo. What an issue carries from it — the four-tuple on a leaf, the
category alone on an epic, nothing of the factory's on a wayfinder issue
— is [Issue Authoring](/standards/tracking/issue-authoring.md). The
states the phase labels name are
[the software factory](/software-factory/software-factory.md).

## Valid labels

The repo's labels are exactly the scheme's: the fixed-value labels in
the table below, plus one `phase:*` label per work node of the factory
graph ([Phase labels](#phase-labels)), each with the scheme's color and
description, and no other. workspace-lint reports a missing, drifted, or
unexpected label (`tracking.label-scheme`).

| Dimension | Label | Meaning |
|---|---|---|
| Category | `category:maintenance` | Maintains shipped state — a bug fix, hygiene, or polish that adds no new capability. |
| Category | `category:extension` | Extends a system past its shipped line — a capability it does not have today. |
| Mode | `mode:direct` | The ordinary path: an issue that ends in merged code. |
| Mode | `mode:spike` | A question; the answer closes the issue, no PR. Always `tests:no` — a spike merges nothing. |
| Tests | `tests:yes` | The work writes or modifies tests, so `build` runs it test-first. |
| Tests | `tests:no` | The work touches no tests, so `build` implements directly. |
| Origin | `origin:deferral` | The issue was opened by the factory itself, to hold work a review suggested and the run deferred. |
| Wayfinder | `wayfinder:map` | A wayfinder map: the planning epic the `/wayfinder` skill drives. |
| Wayfinder | `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task` | A decision ticket's type, one per ticket; the skill defines what each type asks. |

Category, mode, tests, and phase are the factory's dimensions, the
four-tuple a leaf carries. Every mode either fixes `tests:*` or splits on
it, so the four-tuple is complete on every leaf; category is required
metadata and affects no routing.

`origin:*` is outside the four-tuple. It records where an issue came from
rather than what it is or where it stands, so no leaf is required to
carry one, and an issue opened by hand carries none. A deferral stub is
the whole of the dimension today —
[the suggestion dispositions](/software-factory/review-contract.md#suggestion-dispositions)
mint it, at `phase:intake` like any other fresh issue.

`wayfinder:*` is the `/wayfinder` skill's dimension: the skill owns the
method and the meaning of each ticket type, and the scheme mints only
the values the skill names.

## Phase labels

A phase label is its node id with `_` mapped to `-`, `phase:`-prefixed
(node `pr_review` → label `phase:pr-review`), and the scheme's `phase:*`
values equal the work nodes of
[the factory graph](/software-factory/software-factory.md#the-graph) —
its rectangles and diamonds — mapped that way, exactly:
`intake, design, spike, build, pr-review`.

**The parity invariant.** A scheme value no node answers to, or a node no
scheme value names, is the violation; the `scheme-vs-graph` judgment
checks it. Exempt, and only these:

- **Pre-issue states** — `CANDIDATES.md` and the idea funnel. No issue exists, so
  there is nothing to label.
- **Terminal endpoints** — merged, closed, escalated. An issue leaves the graph
  there rather than occupying a state. Escalated is where a review loop that
  cannot converge puts the pull request down for the user; the issue keeps
  whatever phase it was in, so no label answers to it.

## No blocked label

No label names a blocked state. Blocked is derived from an issue's open
blockers ([Relationships](/standards/tracking/issue-authoring.md#relationships)),
never minted; workspace-lint reports a label whose value is `blocked`
(`tracking.no-blocked-label`).
