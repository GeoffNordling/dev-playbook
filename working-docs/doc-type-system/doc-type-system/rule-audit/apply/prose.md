---
type: General-Sheet
title: Prose Rulings
description: The prose family agent's work order — every rule under standards/prose/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Prose Rulings

The work order of the `prose` family agent: every rule under `standards/prose/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `prose.one-rule-one-place` | prose/conventions.md | rewrite | stochastic | Sentence: Each rule the document states lives in the lead sentence of its section, except a statement of the document's own scope, which sits in the section under the H1. |
| `prose.current-state-and-next-steps-only` | prose/conventions.md | keep | stochastic |  |
| `prose.point-at-canonical-artifacts` | prose/conventions.md | rewrite | stochastic | Sentence: Where a file is itself the standard, the document links that file rather than reproducing its contents; naming one entry as a worked example is not reproduction. |
| `prose.open-with-purpose` | prose/conventions.md | rewrite | stochastic | Sentence: The opening states what the document is for and what a reader should be able to do after reading; an `index.md` and a `README.md` answer instead to the opening-sentence and purpose-sentence rules of the knowledge-organization Standard. |
| `prose.declare-before-use` | prose/conventions.md | keep | stochastic |  |
| `prose.block-form-fits-its-content` | prose/conventions.md | keep | stochastic | Block: the `Table vs repeated structure` bullet becomes: the same shape with the same fields two or more times is a table; anything fewer or uneven is prose with bold leads. |
| `prose.declarative-present-tense` | prose/conventions.md | rewrite | stochastic | Sentence: Every sentence is in the present tense, except a sentence reporting a measurement or an incident that happened, and except in a member of a working documentation set, which may write a guess as a guess. |
| `prose.positive-statement` | prose/conventions.md | keep | stochastic |  |
| `prose.no-slop-tics` | prose/conventions.md | keep | stochastic |  |
| `prose.harness-loaded-agent-instructions` | prose/conventions.md | condition |  |  |
| `prose.no-first-person` | prose/conventions.md | keep | deterministic |  |
| `prose.declarative-documents` | prose/conventions.md | condition |  |  |
| `prose.third-person` | prose/conventions.md | keep | stochastic |  |
| `prose.name-concepts-once-use-consistently` | prose/conventions.md | keep | stochastic |  |
| `prose.terminology-the-person-is-the-user` | prose/conventions.md | rewrite | stochastic | Sentence: One actor, the dispatcher, reviewer, and approver, is the `user` throughout the document, its frontmatter, code spans, and fenced blocks included, never a synonym, in any case, plural, or compound. A numbered Decision Record is exempt. |
| `prose.the-banned-word` | prose/conventions.md | rewrite | deterministic | Sentence: The file does not contain a word the workspace vocabulary bans, `WORKSPACE_VOCABULARY` in `src/dev_playbook/prose_lint.py`, bare or plural, in any case, alone or in a compound, its frontmatter, code spans, and fenced blocks included. |
| `prose.the-repo-vocabulary` | prose/conventions.md | keep | deterministic |  |
| `prose.spelling` | prose/conventions.md | keep | deterministic |  |
| `prose.heading-casing` | prose/conventions.md | rewrite | stochastic | Block: the rule gains the clause "the `Considered Options` heading of a Decision Record is exempt". |
| `prose.grammatical-parallelism` | prose/conventions.md | keep | stochastic |  |
| `prose.assertion-headings` | prose/conventions.md | add | stochastic | After: `prose.heading-casing`. Rule:<br>## Assertion headings<br><br>Each heading below the H1, and each name an encoding reads from a body such as a Guide step's bold run, is an assertion: one clause stating the point its section makes, `Write docstrings that say what the thing does`, not a label naming its topic, `What a docstring says`.<br><br>`prose.assertion-headings` · stochastic<br><br>> **Why.** A parse shows the names and nothing beneath them, so read alone and in order the assertions are the document's argument, and labels are only its table of contents. One clause keeps a name a headline rather than a second body. |

## Acronyms

- **H1** — markdown heading level one.
