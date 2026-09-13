---
type: General-Sheet
title: Cells and Rulesets Encoding
description: The layer below the shape — how a card's cells encode pointers for cardgen, how a ruleset writes its population, rules, and conditions for rulegen, where each file sits, how it is named, and the catalog that lists it
---

# Cells and Rulesets Encoding

The layer below [the shape](/doc-types/standard/contract-shape.md): the
form a card's cells take so `scripts/cardgen` reads every pointer
deterministically, the form a ruleset takes so `scripts/rulegen` reads
the population, every rule, and every condition the same way, where
each file sits, what it is named, and the catalog that lists every
Standard. Both generators slice; neither interprets. The cut points are
the bullet marker, the spaced em dash, the first link, a bold mode
name, one frontmatter key, the heading levels, and the first paragraph
under a heading. Doc Conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place)
states the same cut for a reader: each rule lives in the lead sentence
of its section.

## Cells

A cell is a bullet list, one pointer per bullet, or the single bullet
`none`. The cut points are the bullet marker, the first spaced em dash
(` — `), the first markdown link before that dash, and, in Enforce, the
bold mode name.

- **The lead.** A bullet's text up to its first ` — ` is the lead.
  Everything after the dash is annotation: carried in the card, never
  read by the generator.
- **Define, Audit, Adopt.** The pointer is the target of the first link
  in the lead. A lead with no link is the pointer verbatim — the form
  for a third-party detector cited by its pin (`ruff`, `mypy`,
  `shellcheck`, `shfmt`), whose home is a pin, not a file in this
  repository.
- **Enforce.** A bullet names its mode in bold, exactly one per bullet,
  wherever it sits: a gate, `**commit gate**`, `**push gate**`, or
  `**CI gate**`, the three names fixed by
  [Gates](/standards/standard/gates.md#three-rungs), or `**on demand**`.
  At a gate the pointer is the gate name. On demand the pointer is the
  target of the first link in the lead, the tool invoked.
- **none.** A cell with nothing to point at holds the one bullet
  `none`, optionally followed by a colon and the reason. It renders as
  one `none` row.
- **Prose.** A paragraph in a cell that is not a bullet is opaque:
  cardgen carries nothing from it. A remark that is not a pointer — a
  chosen gap, what sits outside every gate — goes there, never in a
  bullet.

A bullet that breaks the form — a Define bullet with no link, an
Enforce bullet naming no mode or two, or on demand with no link, a
`none` beside other bullets — fails the generator: a card that cannot
be sliced cannot be viewed.

## The population

The ruleset's frontmatter key `population` holds the population as one
phrase: the class, then `, except` and its exclusions when it has them.

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
  ruleset.
- **The predicate.** The first paragraph under the heading. It states
  the check whole: a reader with only that paragraph can apply it.
- **The body.** Everything after the first paragraph: the definition,
  the exemptions, the action, the examples, the reason. Carried, never
  read.

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
reader's map of a long ruleset is its `description` and the view, so a
heading that only groups rules for navigation, `Voice` or `Mechanics`,
is written as neither: the view would print it as a condition.

## Everything else

Content that is not the population, a condition, a rule, or a rule's
reason has its home in another document: procedure and a writer's
heuristics each do a second thing
([System Legibility](/docs/system-legibility.md#standing-principles)).
A reason stays only where the rule would look wrong without it, one
concrete fact that stops a reader from undoing the rule.

## Where a Standard lives

A Standard is one directory under `standards/`. Its card is
`standards/<name>/card.md`, typed `Standard-Card`, and every immediate
subdirectory of `standards/` except `references/` holds one; the tree's
rule is one directory, one Standard, the card beside the rulesets it
points at. The rule and its lint are
[Directory layout](/standards/standard/cards.md#directory-layout).

A ruleset is `standards/<name>/<topic>.md`, typed `Standard-Ruleset`,
beside the card that points at it. A ruleset with special cases, the
rulesets that add rules for one kind of its member, is a directory
`standards/<name>/<topic>/` holding the general ruleset as
`<topic>.md` and one file per special case, the card pattern one level
down. The card column of the view is the first directory, the standard
column the path beneath it without `.md`,
`documentation-sets/documentation-sets` and
`documentation-sets/working-documentation-sets` for a nested pair, and
the population the frontmatter. That both kinds sit under `standards/`
is the doc-type's rule, in
[definition.md](/doc-types/standard/definition.md#where-a-standard-lives).

## Naming

A filename under `standards/`, directory or ruleset alike, is
kebab-case and names its topic as a noun: a plain noun
(`conventions.md`, `records.md`, `distribution/`), a noun compound
(`cache-gate.md`, `context-content.md`), or a gerund compound
(`linking-issues.md`) — never a bare verb (`skill-write.md`). `card.md`
and `index.md` are the fixed role names, named for what the file is in
its directory rather than for a topic; a special-case directory's
general ruleset is named for its topic like any other
(`documentation-sets/documentation-sets.md`), never `standard.md`,
which would overload the word. When a directory has an established
family prefix, a new sibling on the same subject keeps it.

## The catalog

Each repo that carries Standards has its own catalog at
`standards/index.md`; in dev-playbook that is
[standards/index.md](/standards/index.md). Its membership and order are
[The catalog](/standards/standard/cards.md#the-catalog).

## The generators

`scripts/cardgen` reads every file typed `Standard-Card` under
`standards/` and writes the `card, cell, pointer` relation to
`doc-types/standard/cards.txt`. `scripts/rulegen` reads every file typed
`Standard-Ruleset` under `standards/` and writes the two ruleset tables
to `doc-types/standard/standards.txt`. Each takes `--check`, which diffs
and fails on drift. A ruleset that cannot be sliced fails rulegen: a
`population` that is not double-quoted, a rule or condition heading
with no paragraph beneath it or with a list, table, quote, or fence as
its first block, two headings with one slug in one ruleset, an H3 with
no H2 above it, or a heading below H3, or no `population` key at all.
