---
type: General-Sheet
title: Decisions Rulings
description: The decisions family agent's work order — every rule under standards/decisions/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Decisions Rulings

The work order of the `decisions` family agent: every rule under `standards/decisions/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `decisions.the-bar` | decisions/records.md | keep | stochastic |  |
| `decisions.scope` | decisions/records.md | guide |  | Guide: `guides/governed-repo.md` |
| `decisions.the-directory` | decisions/records.md | keep | deterministic |  |
| `decisions.sequential-numbering` | decisions/records.md | keep | deterministic |  |
| `decisions.slug-case` | decisions/records.md | delete |  |  |
| `decisions.template` | decisions/records.md | rewrite | deterministic | Sentence: A Decision Record's frontmatter holds `type: Decision-Record`, a `title`, a `description`, and a `date`; its body opens with an H1 repeating the `title`. |
| `decisions.context-decision-and-reason` | decisions/records.md | rewrite | stochastic | Sentence: A Decision Record's body gives the context the decision was made in, the decision itself, and the reason for it. |
| `decisions.date` | decisions/records.md | rewrite | deterministic | Sentence: A Decision Record's `date` frontmatter key holds a `YYYY-MM-DD` date or `null`<br>Why: The date is the day the decision was made, not the writing day, and null where that day is unrecoverable. |
| `decisions.immutable-after-merge` | decisions/records.md | guide |  | Guide: `guides/governed-repo.md` |
| `decisions.status-vocabulary` | decisions/records.md | keep | deterministic |  |
| `decisions.supersession-target` | decisions/records.md | keep | deterministic |  |
| `decisions.optional-sections` | decisions/records.md | delete |  |  |
| `decisions.external-convention-evaluation` | decisions/records.md | condition |  |  |
| `decisions.what-was-examined` | decisions/records.md | rewrite | stochastic | Sentence: A Decision Record whose decision is a verdict on something outside the workspace names the source and pins at least one of the repository SHA and the release or version examined.<br>Why: *stands.* The pin lets a later reader tell whether the thing judged has changed since; the record's own `date` is the day it was read. |

## Acronyms

- **H1** — markdown heading level one.
- **SHA** — the hash naming a git commit.
