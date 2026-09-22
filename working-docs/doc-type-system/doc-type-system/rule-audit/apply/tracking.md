---
type: General-Sheet
title: Tracking Rulings
description: The tracking family agent's work order — every rule under standards/tracking/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Tracking Rulings

The work order of the `tracking` family agent: every rule under `standards/tracking/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `tracking.one-home` | tracking/candidates.md | guide |  | Guide: `guides/repo-settings.md` |
| `tracking.entry-shape` | tracking/candidates.md | rewrite | deterministic | Sentence: An entry is one list item: a bolded name, an em dash, then at most two sentences, with no fields, no acceptance criteria, and no checkboxes.<br>Why: *stands.* The name is short and the sentences state intent; a candidate is a seed, not a specification. |
| `tracking.structure` | tracking/candidates.md | keep | stochastic |  |
| `tracking.written-for-the-user` | tracking/issue-shapes.md | keep | stochastic |  |
| `tracking.behavioural-not-procedural` | tracking/issue-shapes.md | keep | stochastic |  |
| `tracking.one-goal` | tracking/issue-shapes.md | keep | stochastic |  |
| `tracking.user-intent` | tracking/issue-shapes.md | rewrite | stochastic | Sentence: An issue's `User intent` section is written in the user's voice, not an agent's paraphrase.<br>Why: *stands.* The section holds the user's own words, never an agent's paraphrase; only the user can vouch for that, so the predicate asks for the user's voice. |
| `tracking.closed-fences` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.build-leaf` | tracking/issue-shapes.md | condition |  |  |
| `tracking.build-labels` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.build-headings` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.prohibited-surfaces` | tracking/issue-shapes.md | delete |  |  |
| `tracking.artifacts` | tracking/issue-shapes.md | retrailer | stochastic |  |
| `tracking.spike` | tracking/issue-shapes.md | condition |  |  |
| `tracking.spike-labels` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.spike-headings` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.session-leaf` | tracking/issue-shapes.md | condition |  |  |
| `tracking.session-labels` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.session-headings` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.a-stable-body` | tracking/issue-shapes.md | keep | stochastic |  |
| `tracking.epic` | tracking/issue-shapes.md | condition |  |  |
| `tracking.category-only` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.epic-headings` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.no-child-list` | tracking/issue-shapes.md | keep | stochastic |  |
| `tracking.standing-rulings` | tracking/issue-shapes.md | delete |  |  |
| `tracking.wayfinder-map-or-ticket` | tracking/issue-shapes.md | condition |  |  |
| `tracking.wayfinder-labels` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.wayfinder-body` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.ticket-parentage` | tracking/issue-shapes.md | keep | deterministic |  |
| `tracking.valid-labels` | tracking/label-scheme.md | guide |  | Guide: `guides/repo-settings.md` |
| `tracking.github-origin` | tracking/repo-settings.md | guide |  | Guide: `guides/repo-settings.md` |
| `tracking.squash-only-merges` | tracking/repo-settings.md | guide |  | Guide: `guides/repo-settings.md` |
| `tracking.default-branch-protection` | tracking/repo-settings.md | guide |  | Guide: `guides/repo-settings.md` |
