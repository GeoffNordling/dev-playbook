---
type: General-Sheet
title: Modules Rulings
description: The modules family agent's work order — every rule under standards/modules/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Modules Rulings

The work order of the `modules` family agent: every rule under `standards/modules/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `modules.deep-not-shallow` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.internal-seams-stay-inside` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.two-adapters-or-no-seam` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.dependencies-are-accepted-not-constructed` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.a-port-at-a-process-boundary` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.the-interface-is-the-test-surface` | modules/design.md | guide |  | Guide: `guides/design-and-testing.md` |
| `modules.results-are-returned-not-written` | modules/design.md | delete |  |  |

## After the rows

Every rule leaves `standards/modules/design.md`, so the family retires, and this order overrides the prompt's one-family limit for the four files it names. Move the lead's definitions of module, interface, and implementation into the lead of `guides/design-and-testing.md`, word for word, then `git rm` `standards/modules/design.md` and `standards/modules/index.md`, remove the `modules/` row from `standards/index.md`, and repoint every link to the two removed files, nine files today including four under `working-docs/software-factory/`, to `guides/design-and-testing.md`, a link with a rule anchor to the Guide heading that now holds that rule's words.

## Acronyms

None.
