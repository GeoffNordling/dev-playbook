---
type: General-Sheet
title: Doc Type Rulings
description: The doc-type family agent's work order — every rule under standards/doc-type/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Doc Type Rulings

The work order of the `doc-type` family agent: every rule under `standards/doc-type/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `doc-type.registered` | doc-type/doc-type.md | keep | deterministic |  |
| `doc-type.a-verb-set` | doc-type/doc-type.md | keep | stochastic |  |
| `doc-type.one-base` | doc-type/doc-type.md | retrailer | deterministic |  |
| `doc-type.a-composition-rule` | doc-type/doc-type.md | keep | stochastic |  |
| `doc-type.an-encoding` | doc-type/doc-type.md | keep | stochastic |  |
| `doc-type.held-to-a-standard` | doc-type/doc-type.md | keep | stochastic |  |
| `doc-type.one-sentence` | doc-type/doc-type.md | rewrite | stochastic | Sentence: `definition.md` opens with one sentence that says what one instance is. |
| `doc-type.one-graph` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.what-the-paragraph-says` | doc-type/loop-conventions.md | keep | stochastic |  |
| `doc-type.three-verb-sections` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.nodes-and-entries-agree` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.edges-follow-the-shape` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.entries-point-and-condition` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.an-act-links-a-runbook` | doc-type/loop-conventions.md | keep | deterministic |  |
| `doc-type.front-matter` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.name-matches-its-home` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.kebab-case-name` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.description` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.description-states-what-and-when` | doc-type/runbook-conventions.md | keep | stochastic |  |
| `doc-type.model-and-effort` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.body-opens-with-an-h1` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.steps-end-on-a-completion-criterion` | doc-type/runbook-conventions.md | guide |  | Guide: `guides/writing-for-agents.md` |
| `doc-type.carries-its-chain` | doc-type/runbook-conventions.md | rewrite | stochastic | Block: exemption clause becomes "except an edge the span vocabulary cannot carry". |
| `doc-type.skill` | doc-type/runbook-conventions.md | condition |  |  |
| `doc-type.bundle-layout` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.model-invocation-flag` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.interactive-skills-inherit` | doc-type/runbook-conventions.md | keep | stochastic |  |
| `doc-type.tool-fields` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.disallowed-tools-restate-nothing` | doc-type/runbook-conventions.md | delete |  |  |
| `doc-type.arguments` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.no-argument-placeholder` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.references-one-level-deep` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.skillmd-at-most-500-lines` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.agent` | doc-type/runbook-conventions.md | condition |  |  |
| `doc-type.tools` | doc-type/runbook-conventions.md | keep | deterministic |  |
| `doc-type.the-population` | doc-type/standard-conventions.md | rewrite | deterministic | Sentence: A file typed `Standard` names the population its rules bind in its frontmatter: a `population` key holding one phrase.<br>Why: standards-lint reports a Standard without a population. What a detector reports is not part of the predicate, so the clause lives here. |
| `doc-type.the-rule-shape` | doc-type/standard-conventions.md | rewrite | deterministic | Why: The first paragraph is the predicate every member is held to; the block or table is the target state it compares against. An H2 without a trailer is a condition: it names which members the rules under it bind. It is one shape whether it has one child or eleven, and its definition is never repeated in the children. |
| `doc-type.decidable-predicates` | doc-type/standard-conventions.md | rewrite | stochastic | Why: A predicate is decided from the bytes of the repo at one commit, by reading them or by a pure function of them such as a formatter. It is not a test over run-time behaviour, what a script exits or prints; not an instruction to an author; not a fact held outside the files, the day a decision was made, the latest upstream release, a GitHub setting, git history, another repo; and not a definition that scopes other rules. Behaviour and instruction go to a Guide, the why to the why block, a scoping definition to an H2 with no trailer. Kind is judged from the sentence, not the trailer: a sentence a script decides from the files with no judgment call is deterministic, a sentence with a judgment word is stochastic, and where a sentence mixes the two the mechanical part stays deterministic and the judgment moves to the why block. |
| `doc-type.headings-carry-the-gist` | doc-type/guide-conventions.md | delete |  | Superseded by `prose.assertion-headings`, which the prose family adds in this wave. |

## Acronyms

- **H2** — markdown heading level two.
