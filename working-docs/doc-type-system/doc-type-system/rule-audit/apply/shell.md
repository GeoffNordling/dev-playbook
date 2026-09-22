---
type: General-Sheet
title: Shell Rulings
description: The shell family agent's work order — every rule under standards/shell/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Shell Rulings

The work order of the `shell` family agent: every rule under `standards/shell/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `shell.bash-declared` | shell/conventions.md | keep | deterministic |  |
| `shell.shellcheck-clean` | shell/conventions.md | keep | deterministic |  |
| `shell.disable-carries-a-reason` | shell/conventions.md | keep | stochastic |  |
| `shell.formatting` | shell/conventions.md | keep | deterministic |  |
| `shell.executable-scripts` | shell/conventions.md | condition |  |  |
| `shell.glue-only` | shell/conventions.md | keep | deterministic |  |
| `shell.strict-mode` | shell/conventions.md | keep | deterministic |  |
| `shell.sourced-fragments` | shell/conventions.md | condition |  |  |
| `shell.no-shebang-no-strict-mode` | shell/conventions.md | keep | deterministic |  |
| `shell.dialect-directive` | shell/conventions.md | keep | deterministic |  |
| `shell.bounded-to-shell-integration` | shell/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |

## Acronyms

None.
