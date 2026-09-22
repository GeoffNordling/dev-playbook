---
type: Standard
title: Label Scheme
description: The closed-world label set a governed repo's tracker mints — every label with its description, generated from the scheme data
population: "a governed repo's GitHub labels"
---

# Label Scheme

The labels a governed repo's tracker mints. The scheme is closed-world:
which labels exist is fixed as data in
`src/dev_playbook/label_scheme.json`, and [labelgen](/scripts/labelgen)
renders that data as the table below. Which labels an issue carries is
[Issue Shapes](/standards/tracking/issue-shapes.md).

<!-- labelgen:start -->
| Label | Description |
|---|---|
| `category:maintenance` | Maintains shipped state: a fix, hygiene, or polish that adds no capability. |
| `category:extension` | Extends a system past its shipped line: a capability it lacks today. |
| `mode:direct` | Built by the software factory against its brief; ends in merged code. |
| `mode:spike` | A question; the answer closes the issue in a comment, and no PR opens. |
| `mode:session` | Led by the user in a session: worked in a worktree, PR opened by hand, never dispatched. |
| `tests:yes` | The work writes or changes tests, so the build runs test-first. |
| `tests:no` | The work touches no tests, so the build implements directly. |
| `phase:intake` | Untriaged; intake authors the brief and routes the issue. |
| `phase:design` | The approach is explored and the brief re-authored or decomposed. |
| `phase:spike` | The question is being answered. |
| `phase:build` | Released to the factory; the build node runs next. |
| `phase:pr-review` | A pull request is open and in the review loop. |
| `wayfinder:map` | A wayfinder map: the planning epic the /wayfinder skill drives. |
| `wayfinder:research` | A decision ticket resolved by research: sources outside the working directory. |
| `wayfinder:prototype` | A decision ticket resolved by a cheap, concrete artifact to react to. |
| `wayfinder:grilling` | A decision ticket resolved in conversation with the user. |
| `wayfinder:task` | A decision ticket resolved by manual work that unblocks a decision. |
| `origin:deferral` | Opened by the factory to hold work a review suggested and the run deferred. |
<!-- labelgen:end -->

## Valid labels

A governed repo's GitHub labels are exactly the labels declared in the
scheme data `src/dev_playbook/label_scheme.json`, each carrying the
color and the description that data gives it.

`tracking.valid-labels` · deterministic

> **Why.** The scheme is closed-world so that an issue's labels can be
> read as a state, and a label the scheme does not name, or one whose
> description has drifted, is a state the tracker cannot read.
