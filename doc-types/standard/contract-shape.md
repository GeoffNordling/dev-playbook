---
type: General-Sheet
title: Cells and Rulesets
description: Standard's contract shape — four cells, one per verb, each a pointer list, with the ruleset a Define pointer reaches, one population and its rules — in prose, one screen of pseudocode, and the relations every Standard collapses to
---

# Cells and Rulesets

Four cells and the rulesets they point at are Standard's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Standard's
contract takes. Returning to a topic months later should not require
re-deriving shared understanding over several turns of conversation.
Each Standard therefore has a **card**: a small fixed-format record
that tells a user or agent where to look, one cell per verb, so a
thought that originates at the abstract level ("how do we do X here?")
resolves to concrete files in one hop. Below the card sit its
**rulesets**, the files that describe the state the Standard holds its
population to.

## The shape

The card first, then the ruleset beneath its Define cell.

### The card

A card is a markdown file at `standards/<name>/card.md` with
`type: Standard-Card` frontmatter: a heading, one sentence naming the
governed question, then exactly four cells as sections. That sentence
opens `Governs how`, names the territory its Define cell covers, and
runs about a breath; the frontmatter `description` repeats it verbatim
less the period, so the catalog row and the card state the same remit;
the rule and its lint are
[The question sentence](/standards/standard/cards.md#the-question-sentence).
Each cell holds pointers, annotated where the annotation carries a fact
nothing else holds; an empty cell states an explicit "none" so gaps stay
visible. Cards are thin — often just a handful of pointers — and never
restate the content of their targets.

- **Define.** The rulesets: documents typed `Standard-Ruleset`, each
  one population and its rules, the link alone with no annotation,
  since the directory's index carries each ruleset's description
  ([Define points only at rulesets](/standards/standard/cards.md#define-points-only-at-rulesets)).
- **Audit.** Read-only deviation detection: the detectors that report
  nonconformance without blocking anything. A formatter is a detector
  by its check mode
  ([Detectors](/standards/standard/detectors.md#a-formatter-is-a-detector-by-its-check-mode)).
  This is the cell a Loop's check composes
  ([Loop](/doc-types/loop/contract-shape.md)), never the gate.
- **Enforce.** What compels conformance, in one of two modes. At a
  gate: the rung where nonconformance stops the path to main, cited by
  fixed name (**commit gate**, **push gate**, **CI gate**), defined in
  [Gates](/standards/standard/gates.md). A cell cites the single rung
  where the detector is stationed — where its wiring lives (pre-commit
  hooks → the commit gate; tools that run only inside `make check` →
  the push gate); the hook pattern in Gates implies the echoes at the
  other rungs. On demand: a script or skill the user, a schedule, or a
  process step invokes, which rewrites the object into conformance and
  leaves the result for review, marked **on demand** beside its link. A
  code review is a one-time checkpoint, never an Enforce pointer.
- **Adopt.** What brings a repository into conformance the first
  time: a scaffold, a template, a migration procedure, a first-pickup
  recipe. Often "none": the generic path is an agent reading the Define
  cell and fixing the repository.

The composition rule at the card: exactly one of each cell, in that
order, each holding any number of pointers. The cards themselves are
the examples: [Build](/standards/build/card.md) and
[Meta-Standard](/standards/standard/card.md) — the latter is the card
of the Standard that governs cards, since the meta-standard is an
instance of the format it defines.

### The ruleset

A ruleset is a markdown file at `standards/<name>/<topic>.md` with
`type: Standard-Ruleset` frontmatter, and it describes a state.

- **Population.** The one class of object the ruleset binds, with its
  exclusions: `an authored document, except type: Reference and the
  paths in .prose-lint-exempt`. Every rule is a predicate over a member
  of this class.
- **Rule.** A name, a condition, and a predicate. The name is the
  rule's identity inside its ruleset, the atom later tables join on.
  The predicate is the check, in English or in a lint; a reviewer
  citing it satisfies the axis.
- **Condition.** What must hold of a member for the rule to bind it,
  named as a subset of the population: `python`, for a rule that holds
  only in a repo with a `pyproject.toml`; `harness-loaded agent
  instructions`, for a rule over runbook and context files only. A
  rule with no condition binds every member. The word is shared with
  Runbook, where an edge's condition is what must hold for it to fire,
  and with Loop, where it is what must hold for an act or check to
  fire.

The composition rule at the ruleset: exactly one population, any number
of rules, unordered. A ruleset is a collection, so its shape is a
relation, and every ruleset owns a distinct rule set. A ruleset carries
no pointer to its card and no rationale field: the path names the card,
and rationale is another document's thing
([System Legibility](/docs/system-legibility.md#standing-principles)).

The whole shape in pseudocode:

```python
class Standard(Object):
    """One card and its rulesets. Defined, audited, enforced, adopted; binds state, never process."""

    operations = {define, audit, enforce, adopt}                    # one cell each, below

    question: str                       # "Governs how ..." — one breath

    # four cells, one per verb; a cell is a list of pointers, or the literal word "none"
    define:  list[Pointer[Ruleset]]                 # required, at least one
    audit:   list[Pointer[Detector]] | None         # what a Loop's check composes
    enforce: list[Pointer[Gate | OnDemand]] | None  # Gate = commit | push | CI; OnDemand = a tool that rewrites
    adopt:   list[Pointer[Runbook | Loop]] | None

    # rules: each a predicate over one card's state
    location    = path == f"standards/{name}/card.md"       # beside its rulesets
    frontmatter = type == "Standard-Card" and description == question
    layout      = h2s == ["Define", "Audit", "Enforce", "Adopt"]


class Ruleset(Object):
    """One population and its rules. What a Define pointer reaches."""

    operations = Standard.operations                                # a file kind of Standard, not a doc-type

    population: ObjectClass         # one class, exclusions included
    rules: set[Rule]                # any number, unordered

    location    = path == f"standards/{card}/{topic}.md"    # beside its card
    frontmatter = type == "Standard-Ruleset" and population is not None


class Rule:
    name:      str                  # unique within its ruleset
    condition: Condition | None     # a named subset of the population; None binds every member
    predicate: str                  # English or a lint, checked against one member at one moment
```

## The view

Every Standard collapses to rows of three relations. The card gives one,
`card, cell, pointer`; `scripts/cardgen` writes the whole catalog to
`doc-types/standard/cards.txt` and, with `--check`, fails on drift:

```
card     cell     pointer
build    define   /standards/build/canonical.md
build    audit    /scripts/repo-lint
build    enforce  commit gate
modules  audit    none
```

A Define, Audit, or Adopt pointer is the file a bullet leads with, or
the bare name of a third-party detector cited by its pin. An Enforce
pointer is one of the three gate names, or the file of a tool marked
on demand. An empty cell is one `none` row, so the gap stays visible in
the view as it does in the card. Cards sort alphabetically, cells keep
the card's order, and pointers keep their bullet order. The annotation
after each pointer stays below the collapse, in the card.

The rulesets give two, `standards` and `rules`, in one file.
`scripts/rulegen` writes the whole tree to
`doc-types/standard/standards.txt` and, with `--check`, fails on drift:

```
standards
card   standard     population
build  skeleton     a governed repo's tree, except standards/build/canonical/ in dev-playbook
prose  conventions  an authored document, except type: Reference and the paths in .prose-lint-exempt

rules
card   standard     rule                           when
build  skeleton     required-files                 —
build  skeleton     tests-present                  python-source
build  skeleton     uvlock-and-python-version      python
prose  conventions  declarative-present-tense      —
prose  conventions  imperative-and-second-person   harness-loaded-agent-instructions
```

Rows of the generated files, excerpted.

Card and standard together key both ruleset tables, because a stem
repeats across cards: `standards/prose/conventions.md` and
`standards/shell/conventions.md`. The card column is the path's first
directory, never a pointer in the file. A rule with no condition shows
`—`. Rows sort by card, standard, then rule, so the file diffs stably.

The three relations join on the card column: which Standards exist,
which rulesets and detectors each points at, which rules each ruleset
holds. Every other question is a grep. A fourth table, rule to lint,
joins on the rule column later, and drift is a set difference.
