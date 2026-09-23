---
type: General-Sheet
title: Tracking
description: The triage of the tracking family's seventeen deterministic rules — one kept, thirteen restated plain with meaning held and their workspace-lint checks untouched, three null rules escalated
---

# Tracking

Seventeen deterministic rules over four Standards under
`standards/tracking/`, per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
Sixteen are GitHub state that `scripts/workspace-lint` reads over
`gh api`. Per the Constraints of
[Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md),
that check is untouched: a rule it decides is keep, or a rewrite of the
body only. Each restatement below changes words, not the check. Most
restatements replace "carries" with "has" and name
`src/dev_playbook/label_scheme.json` for "a value of the label scheme".

## candidates.md

- **`one-list-item-per-entry`**, `standards/tracking/candidates.md:25`.
  Escalated, number 1. Null today.

## github-settings.md

Kept as written, the check matching the sentence: `origin-on-github`.

- **`squash-only-merges`**, `standards/tracking/github-settings.md:26`.
  Rewrite, the table unchanged.

  > Each GitHub merge setting of a governed repo has the value this
  > table gives:

  `wording only`. Check: `check_settings`,
  `src/dev_playbook/workspace_lint.py:538`, compares the six fields of
  `EXPECTED_SETTINGS` (`:171`) read over GraphQL.

- **`default-branch-protected-from-destructive-operations`**,
  `standards/tracking/github-settings.md:44`. Rewrite, the table
  unchanged.

  > The default branch of a governed repo has two rules in force:
  > force pushes are blocked and deletions are restricted. Each ruleset
  > that supplies one of these two rules has enforcement Active and an
  > empty bypass list, and one of those rulesets is named
  > `protect-main`.

  `wording only`. Check: `check_protection`,
  `src/dev_playbook/workspace_lint.py:576`, reads
  `defaultBranchRef.rules` for `NON_FAST_FORWARD` and `DELETION`, then
  each supplying ruleset's enforcement, bypass count, and name.

## issue-shapes.md

The species definitions under `Build leaf`, `Spike`, `Session leaf`,
`Epic`, and `Wayfinder map or ticket` are not rules, but they use
"carries" the same way; the same word change applies to them. The
survey row in
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
also notes that `fetch_issues` reads open issues only
(`src/dev_playbook/workspace_lint.py:534`), so the frontmatter
population "a GitHub issue in a governed repo" is wider than any check.
That is a population line, not a rule body, and is left to the
Standards pass.

- **`closed-fences`**, `standards/tracking/issue-shapes.md:57`. Rewrite.

  > The body of a leaf that has `mode:session`, or that has a `phase:*`
  > label other than `phase:intake`, closes every code fence it opens.

  `wording only`. Check: `_heading_findings`,
  `src/dev_playbook/workspace_lint.py:1033`, reports
  `md.UnclosedFence`. The gap the survey records stays, per the
  Constraint: a leaf with zero or two `mode:*` labels, or an unknown
  mode, never reaches the fence check (`_brief_findings`, `:1016`).

- **`one-label-from-each-prefix`**,
  `standards/tracking/issue-shapes.md:68`. Rewrite.

  > A build leaf with a `phase:*` label other than `phase:intake` has
  > exactly one `category:*`, one `mode:*`, one `tests:*`, and one
  > `phase:*` label, and each of the four is a label in
  > `src/dev_playbook/label_scheme.json`.

  `wording only`. Check: `_tuple_findings`,
  `src/dev_playbook/workspace_lint.py:965`, run from `check_issues`
  (`:1113`) on every leaf past intake that is not a session leaf. It
  also reports, under this id, a leaf with no `mode:*` label, which is
  no build leaf; that is wider than the sentence and stays, per the
  Constraint.

- **`every-build-heading-in-bold`**,
  `standards/tracking/issue-shapes.md:76`. Rewrite, the example block
  unchanged.

  > The body of a build leaf with a `phase:*` label other than
  > `phase:intake` has each of the eight headings below as bold text
  > followed by a colon, `**Summary:**` or `**Summary**:`, outside any
  > code fence.

  `wording only`. Check: `_has_heading`,
  `src/dev_playbook/workspace_lint.py:713`, over the lines outside
  fences, with `BUILD_HEADING_LIST` (`:105`).

- **`one-label-from-each-prefix-tests-fixed-at-no`**,
  `standards/tracking/issue-shapes.md:121`. Rewrite.

  > A spike with a `phase:*` label other than `phase:intake` has
  > exactly one `category:*`, one `mode:*`, one `tests:*`, and one
  > `phase:*` label, each a label in
  > `src/dev_playbook/label_scheme.json`, and its `tests:*` label is
  > `tests:no`.

  `wording only`. Check: `_tuple_findings`,
  `src/dev_playbook/workspace_lint.py:965`, which files the finding
  under this id when the one mode is `spike` (`:976`, `:1004`).

- **`summary-question-and-deliverable`**,
  `standards/tracking/issue-shapes.md:130`. Rewrite, the example block
  unchanged.

  > The body of a spike with a `phase:*` label other than
  > `phase:intake` has `Summary`, `Question`, and `Deliverable` as bold
  > text followed by a colon, outside any code fence.

  `wording only`. Check: `_has_heading` with `SPIKE_HEADING_LIST`,
  `src/dev_playbook/workspace_lint.py:115`, from `_brief_findings`.

- **`one-category-label-no-phase-or-tests`**,
  `standards/tracking/issue-shapes.md:152`. Rewrite.

  > A session leaf has exactly one `category:*` label, a label in
  > `src/dev_playbook/label_scheme.json`, no `mode:*` label other than
  > `mode:session`, and no `tests:*` or `phase:*` label.

  `wording only`. Check: `_session_findings`,
  `src/dev_playbook/workspace_lint.py:908`.

- **`every-session-heading-in-bold`**,
  `standards/tracking/issue-shapes.md:160`. Rewrite.

  > The body of a session leaf has `Summary`, `User intent`,
  > `Current behavior`, `Desired behavior`, `Acceptance criteria`, and
  > `Out of scope` as bold text followed by a colon, outside any code
  > fence. `Out of scope` may read `Unknown; dealt with when found.`

  `wording only`. Check: `_has_heading` with `SESSION_HEADING_LIST`,
  `src/dev_playbook/workspace_lint.py:116`, from `_brief_findings`.

- **`category-only`**, `standards/tracking/issue-shapes.md:186`.
  Rewrite.

  > An epic has exactly one `category:*` label, a label in
  > `src/dev_playbook/label_scheme.json`, and no `phase:*`, `mode:*`, or
  > `tests:*` label.

  `wording only`. Check: `_epic_findings`,
  `src/dev_playbook/workspace_lint.py:856`.

- **`outcome-and-decomposition-rationale`**,
  `standards/tracking/issue-shapes.md:193`. Escalated, number 2. Null
  today.

- **`one-wayfinder-label-and-nothing-else`**,
  `standards/tracking/issue-shapes.md:220`. Rewrite.

  > A map has `wayfinder:map` and no other `wayfinder:*` label. A
  > decision ticket has exactly one `wayfinder:*` label, a label in
  > `src/dev_playbook/label_scheme.json`. Neither has a `category:*`,
  > `mode:*`, `tests:*`, or `phase:*` label.

  `wording only`. Check: `_map_findings`,
  `src/dev_playbook/workspace_lint.py:761`, and `_ticket_findings`,
  `:803`.

- **`map-sections-ticket-question`**,
  `standards/tracking/issue-shapes.md:229`. Rewrite, the Why unchanged.

  > A map's body has a markdown heading, at any level, for each of
  > `Destination`, `Notes`, `Decisions so far`, `Not yet specified`,
  > and `Out of scope`. A decision ticket's body has a markdown heading
  > `Question`, at any level.

  `wording only`. Check: `_has_section`,
  `src/dev_playbook/workspace_lint.py:728`, an ATX heading match over
  the raw body. The gap the survey records stays, per the Constraint:
  a heading inside a fence counts (GeoffNordling/dev-playbook#386).

- **`ticket-under-a-map`**, `standards/tracking/issue-shapes.md:242`.
  Escalated, number 3. Null today; the body is already plain.

## label-scheme.md

- **`exactly-the-labels-the-scheme-declares`**,
  `standards/tracking/label-scheme.md:39`. Rewrite.

  > A governed repo's GitHub labels are exactly the labels in
  > `src/dev_playbook/label_scheme.json`, and each label has the color
  > and the description that file gives it.

  `wording only`. Check: `check_labels`,
  `src/dev_playbook/workspace_lint.py:664`: a finding for each missing
  label, each color or description that differs (color compared
  without case), and each label the file does not name.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
Item 1: built as the form check only; the sentence limit is deleted.
Items 2 and 3: deleted, both micromanage and each would read GitHub,
which the No GitHub auditing constraint puts out of scope.

1. **`one-list-item-per-entry`**, `standards/tracking/candidates.md:25`.
   - Meaning: each entry in `CANDIDATES.md` is one bullet, a bold name,
     an em dash, and one or two sentences; no brief furniture.
   - Proposal: rewrite, add a check over the model.

     > Every list item in `CANDIDATES.md`, nested or not, starts
     > `**<name>** — ` and has at most two sentences after the em dash.

     The check: a sentence ends at `.`, `?`, or `!` followed by a space
     and a capital letter, `*`, `` ` ``, `[`, or `(`.
   - Difference from today's sentence: `meaning changed`. "No fields,
     no acceptance criteria, no checkboxes" becomes the form itself. A
     field line, a checkbox item, or a criteria bullet fails because it
     does not start `**<name>** — `. One sentence of criteria written
     inside an entry's own text passes, where the old sentence fails it.
   - Difference from today's enforcement: none today; the verifier row
     is `null`.
   - Measured: 31 list items in `CANDIDATES.md`, 30 pass. One fails:
     `The parser's trigger`, `CANDIDATES.md:51`, has three sentences.
     The repo leaves compliance until that entry is cut to two.

2. **`outcome-and-decomposition-rationale`**,
   `standards/tracking/issue-shapes.md:193`.
   - Meaning: an epic's body has the two bold headings `Outcome` and
     `Decomposition rationale`.
   - Proposal: keep, restated, and add the check to `workspace-lint`
     as a named exception to the "No GitHub auditing" Constraint.
     `_epic_findings` calls `_heading_findings` with the two headings,
     as the leaves do.

     > The body of an epic has `Outcome` and `Decomposition rationale`
     > as bold text followed by a colon, outside any code fence.

     The other way: the rule stays `null` out of this strand's scope,
     against the Constraint "The null rows are in". Delete does not
     fit: an epic without the headings is a state a governed repo can
     fail.
   - Difference from today's sentence: `wording only`. "Outside any
     code fence" only states what "bold heading" already means: a
     heading shown in a fence is quoted, as the build and spike rules
     say.
   - Difference from today's enforcement: no check today;
     `_epic_findings`, `src/dev_playbook/workspace_lint.py:856`, reads
     labels only.
   - Measured, read-only over `gh api` with `fetch_issues`: 25 open
     issues in the 8 governed repos with a GitHub origin (`lunch` and
     `date-tree` have none), 0 open epics, 0 failures.

3. **`ticket-under-a-map`**, `standards/tracking/issue-shapes.md:242`.
   - Meaning: an issue with a `wayfinder:*` label other than
     `wayfinder:map` has a parent issue, and that parent has
     `wayfinder:map`.
   - Proposal: keep the body as written, and add the check to
     `workspace-lint` as the same named exception as number 2. The
     issues list that `fetch_issues` reads has no parent field; GraphQL
     `Issue.parent` has it, one query per decision ticket, or one
     `sub_issues` read per open map. The other way is as in number 2.
   - Difference from today's sentence: none.
   - Difference from today's enforcement: no check today;
     `_ticket_findings`, `src/dev_playbook/workspace_lint.py:803`,
     reads labels and body only.
   - Measured, same read as number 2: 0 open maps, 0 open decision
     tickets, 0 failures.

## New rules

None.

## Acronyms

- **ATX** — the markdown heading form that starts with `#` characters.
