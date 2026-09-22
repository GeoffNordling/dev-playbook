---
type: General-Sheet
title: Harness Rulings
description: The harness family agent's work order — every rule under standards/harness/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Harness Rulings

The work order of the `harness` family agent: every rule under `standards/harness/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `harness.no-frontmatter` | harness/claude-content.md | keep | deterministic |  |
| `harness.operational-scope` | harness/claude-content.md | keep | stochastic |  |
| `harness.one-scope` | harness/claude-content.md | rewrite | stochastic | Sentence: A nested <dir>/CLAUDE.md states no rule already stated in the root file above it.<br>Why: A rule sits at the widest scope where it is true: machine-wide in the global source, repo-wide in the root file, only the delta in a nested file. A repo can check one part of that, the nested file against its root. |
| `harness.global-file` | harness/claude-content.md | condition |  |  |
| `harness.two-sections` | harness/claude-content.md | keep | deterministic |  |
| `harness.required-rules` | harness/claude-content.md | keep | deterministic |  |
| `harness.one-rule-per-heading` | harness/claude-content.md | keep | stochastic |  |
| `harness.members` | harness/files.md | rewrite | deterministic | Sentence: Every file under .claude/ or dotfiles/dot-claude/ in a governed repo matches a member row of the table below.<br>Why: Claude Code fixes which files it reads; the table is the workspace's record of that set, and the predicate holds the repo to the table. |
| `harness.location` | harness/files.md | rewrite | deterministic | Block: the tree block gains the optional `agents/` bundle line the repo already uses. |

## Acronyms

None.
