---
type: General-Sheet
title: Distribution Rulings
description: The distribution family agent's work order — every rule under standards/distribution/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Distribution Rulings

The work order of the `distribution` family agent: every rule under `standards/distribution/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `distribution.one-published-id` | distribution/channel.md | keep | deterministic |  |
| `distribution.a-publisher-dogfoods-its-manifest` | distribution/channel.md | keep | deterministic |  |
| `distribution.a-valid-manifest` | distribution/channel.md | keep | deterministic |  |
| `distribution.a-pinned-rev` | distribution/channel.md | delete |  |  |
| `distribution.the-roster` | distribution/channel.md | guide |  | Guide: `guides/governed-repo.md` |
