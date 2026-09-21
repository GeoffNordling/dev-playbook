---
type: General-Sheet
title: Population and Rules Encoding
description: The layer below the shape — how a Standard writes its population, its rules, and its conditions so a lint reads them, where the file sits, how it is named, and the catalog that lists it
---

# Population and Rules Encoding

The layer below [the shape](/doc-types/standard/contract-shape.md): the
form a Standard takes so deterministic code reads the population, every
rule, and every condition the same way, where the file sits, what it is
named, and the catalog that lists every Standard. The cut points are
one frontmatter key, the heading levels, and the trailer line. Doc
Conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place)
states the same cut for a reader: each rule lives in its own section.

## The population

The frontmatter key `population` holds the population as one phrase:
the class, then `, except` and its exclusions when it has them.

```yaml
population: "an authored document, except type: Reference and the paths in .prose-lint-exempt"
```

The phrase is double-quoted, since YAML reads an unquoted `: ` as a
nested key. The prose between the H1 and the first H2 elaborates on
it, defines the exclusions, and links the neighbors; no lint reads it.
The rule and its lint are
[The population](/standards/doc-type/standard-conventions.md#the-population).

## Rules

A rule is a heading; its section is the rule.

- **The name.** The heading's text, in sentence case, naming the rule:
  `Declarative present tense`, `tests/ present`, `ci.yml`. The slug is
  the heading's GitHub slug, the anchor a link to the section uses and
  the one ref-lint resolves: inline marks stripped, lowercased, every
  character outside letters, digits, whitespace, and hyphens dropped,
  each run of whitespace one hyphen (`declarative-present-tense`,
  `tests-present`, `ciyml`, `pre-commit-configyaml`). Slugs are unique
  within a Standard.
- **The predicate.** Everything between the heading and the trailer:
  a first paragraph that states the check whole, and after it at most
  one block or table stating the target state the check compares
  against.
- **The trailer.** The section's last line,
  `` `<name>.<slug>` · deterministic `` or
  `` `<name>.<slug>` · stochastic ``, `<name>` the directory and
  `<slug>` the heading's slug: the rule's id and kind, and the key of
  the verifier table's row.
- **The why.** A block after the trailer, opening `> **Why.**` and
  running to the next heading: the argument for the rule, never a
  predicate. A rule may have none.

The rule and its lint are
[The rule shape](/standards/doc-type/standard-conventions.md#the-rule-shape).

## Conditions

A condition is an H2 whose section holds H3s. Its text names the
member subset, its slug, formed the same way as a rule's, and its first
paragraph states the membership test: `a repo in which pyproject.toml
exists at the root`. Each H3 beneath it is a rule bound under that
condition.

Heading levels are the whole of the mark. An H2 with no H3 beneath it
is a rule that binds every member. An H2 with H3s beneath it is a
condition, and its H3s are the rules. There is nothing deeper. The
reader's map of a long Standard is its `description`, so a heading
that only groups rules for navigation, `Voice` or `Mechanics`, is
written as neither: a lint would read it as a condition.

## The document's own why

A block of the same form, `> **Why.**` to the next heading, sitting
after the prose between the H1 and the first rule or condition: the
argument for the Standard as a whole, not any one rule's. A Standard
may have none.

## Everything else

Content that is not the population, a condition, a rule, or a why
has its home in another document: procedure and a writer's
heuristics in a guide, since each does a second thing
([System Legibility](/docs/system-legibility.md#standing-principles)).

## Where a Standard lives

A Standard is `standards/<name>/<topic>.md`, typed `Standard`, in a
directory that holds at least one such file; the tree's rule is one
directory, one standard, and the rule and its lint are
[Directory layout](/standards/standard/tree.md#directory-layout). A
Standard with special cases, the files that add rules for one kind of
its member, is a directory `standards/<name>/<topic>/` holding the
general Standard as `<topic>.md` and one file per special case,
`documentation-sets/documentation-sets.md` and
`documentation-sets/working-documentation-sets.md` for a nested pair.
That the type sits under `standards/` is the doc-type's rule, in
[definition.md](/doc-types/standard/definition.md#where-a-standard-lives).

## Naming

A filename under `standards/`, directory or file alike, is kebab-case
and names its topic as a noun: a plain noun (`conventions.md`,
`records.md`, `distribution/`), a noun compound (`cache-gate.md`,
`context-content.md`), or a gerund compound (`linking-issues.md`) —
never a bare verb (`skill-write.md`). `index.md` is a
fixed role name, named for what the file is in its directory rather
than for a topic; a special-case directory's general Standard is
named for its topic like any other
(`documentation-sets/documentation-sets.md`), never `standard.md`,
which would overload the word. When a directory has an established
family prefix, a new sibling on the same subject keeps it.

## The catalog

Each repo that carries Standards has its own catalog at
`standards/index.md`; in dev-playbook that is
[standards/index.md](/standards/index.md). Its membership and order are
[The catalog](/standards/standard/tree.md#the-catalog).
