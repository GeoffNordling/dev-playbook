---
type: General-Sheet
title: Python Rulings
description: The python family agent's work order — every rule under standards/python/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Python Rulings

The work order of the `python` family agent: every rule under `standards/python/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `python.empty-init` | python/style.md | keep | deterministic |  |
| `python.docstrings` | python/style.md | keep | deterministic |  |
| `python.docstring-content` | python/style.md | guide |  | Guide: `guides/design-and-testing.md` |
| `python.fail-loudly` | python/style.md | guide |  | Guide: `guides/design-and-testing.md` |
| `python.module-layout` | python/style.md | delete |  |  |
| `python.no-future-annotations` | python/style.md | keep | deterministic |  |
| `python.helper-justification` | python/style.md | delete |  |  |
| `python.helper-placement` | python/style.md | delete |  |  |
| `python.formatted-by-ruff-format` | python/style.md | keep | deterministic |  |
| `python.annotated-signatures` | python/style.md | delete |  |  |
