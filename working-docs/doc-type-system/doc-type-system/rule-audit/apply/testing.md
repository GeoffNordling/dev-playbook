---
type: General-Sheet
title: Testing Rulings
description: The testing family agent's work order — every rule under standards/testing/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Testing Rulings

The work order of the `testing` family agent: every rule under `standards/testing/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `testing.pytest` | testing/conventions.md | delete |  |  |
| `testing.test-file-naming` | testing/conventions.md | keep | deterministic |  |
| `testing.mirror-source-structure` | testing/conventions.md | keep | deterministic |  |
| `testing.conftest-hierarchy` | testing/conventions.md | keep | deterministic |  |
| `testing.arrange-act-assert` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.one-concept-per-test` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.no-logic-in-tests` | testing/conventions.md | delete |  |  |
| `testing.expected-values-come-from-outside-the-code` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.access-only-public-names` | testing/conventions.md | delete |  |  |
| `testing.assert-on-observable-outputs` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.assert-on-outcomes-not-call-sequences` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.name-by-capability-not-mechanism` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.replace-dont-layer` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.no-test-of-a-non-deterministic-decision` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.the-lightest-double` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.double-at-the-port` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.fakes-for-stateful-dependencies` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.one-fake-per-interface` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.fakes-live-in-the-test-tree` | testing/conventions.md | keep | stochastic |  |
| `testing.fakes-implement-only-what-callers-use` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.mocks-at-boundaries-only` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.the-mocking-library` | testing/conventions.md | delete |  |  |
| `testing.fixtures-for-setup-and-teardown` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |
| `testing.narrowest-fixture-scope` | testing/conventions.md | guide |  | Guide: `guides/design-and-testing.md` |

## Acronyms

None.
