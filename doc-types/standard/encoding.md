---
type: General-Sheet
title: Population and Rules Encoding
description: The layer below the shape — how a Standard's file writes its population, its rules, and its conditions for rulegen, and where the file sits
---

# Population and Rules Encoding

The layer below
[the shape](/doc-types/standard/contract-shape.md): the form a
Standard's file takes so `scripts/rulegen` reads the population, every
rule, and every condition deterministically, and where the file sits.
rulegen slices; it never interprets. The cut points are one frontmatter
key, the heading levels, and the first paragraph under a heading. Doc
Conventions' [one rule, one place](/standards/prose/conventions.md#one-rule-one-place)
states the same cut for a reader: each rule lives in the lead sentence
of its section.

## The population

The frontmatter key `population` holds the population as one phrase:
the class, then `, except` and its exclusions when it has them.

```yaml
population: "an authored document, except type: Reference and the paths in .prose-lint-exempt"
```

The phrase is double-quoted, since YAML reads an unquoted `: ` as a
nested key. It travels to the standards table verbatim. The prose
between the H1 and the first H2 elaborates on it, defines the
exclusions, and links the neighbors; rulegen carries nothing from it.

## Rules

A rule is a heading; its section is the rule.

- **The name.** The heading's text, in sentence case, naming the rule:
  `Declarative present tense`, `tests/ present`, `ci.yml`. The rule
  column is the heading's GitHub slug, the anchor a link to the section
  uses and the one ref-lint resolves: inline marks stripped, lowercased,
  every character outside letters, digits, whitespace, and hyphens
  dropped, each run of whitespace one hyphen
  (`declarative-present-tense`, `tests-present`, `ciyml`,
  `pre-commit-configyaml`). A view row's rule column is therefore the
  anchor a citation of the rule ends in. Slugs are unique within a
  Standard.
- **The predicate.** The first paragraph under the heading. It states
  the check whole: a reader with only that paragraph can apply it.
- **The body.** Everything after the first paragraph: the definition,
  the exemptions, the action, the examples. Carried, never read.

## Conditions

A condition is an H2 whose section holds H3s. Its text names the
member subset, its slug, formed the same way as a rule's, is the
`when` column of every rule beneath it, and its first paragraph states
the membership test: `a repo in which pyproject.toml exists at the
root`. Each H3 beneath it is a rule bound under that condition.

Heading levels are the whole of the mark. An H2 with no H3 beneath it
is a rule that binds every member, `—` in the view. An H2 with H3s
beneath it is a condition, and its H3s are the rules. There is nothing
deeper: a rule's body holds paragraphs, lists, tables, and fences. The
reader's map of a long Standard is its `description` and the view, so a
heading that only groups rules for navigation, `Voice` or `Mechanics`,
is written as neither: the view would print it as a condition.

## Everything else

Content that is not the population, a condition, or a rule has its
home in another document: rationale, procedure, and a writer's
heuristics each do a second thing
([System Legibility](/docs/system-legibility.md#standing-principles)).

## Where a Standard lives

A Standard is `standards/<card>/<standard>.md`, typed `Standard`. The
card column of the view is the directory, the standard column the stem,
and the population the frontmatter. The label's rule and its lint are
in
[definition.md](/doc-types/standard/definition.md#where-a-standard-lives).
A Standard's filename follows the card encoding's
[naming rule](/doc-types/standard-card/encoding.md#naming).

## The generator

`scripts/rulegen`, cardgen's sibling, reads every file typed `Standard`
under `standards/` and writes the two tables to
`doc-types/standard/standards.txt`; `--check` diffs and fails on drift.
A file that cannot be sliced fails the generator: no `population` key,
a rule heading with no paragraph beneath it, two rules with one slug in
one Standard, or a heading below H3.
