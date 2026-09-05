---
type: General-Sheet
title: Registry Refactor
description: The decisions aligned on for the document-type registry refactor — the rejection axis, the abstractions, the software factory's position — and the work that remains
---

# Registry Refactor

The decisions the user and Claude aligned on for the registry refactor,
and the work that remains. Member of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).

A decision is written only once it is aligned on. Where a question was
raised and not settled, it sits under Deferred with no lean.

## Goal

Refactor the document-type registry before building any new doc-type:
settle what a Standard is, what a Guide is, and how the kinds are
organized. The settling happens at one level, parsimonious and precise
enough to show on screen. Decisions are made at that level; everything
below it is implementation, audit, and enforcement.

The end product is a
[CLOA object](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#terms)
for the standards: a view, generated
by deterministic code from the standard files, that the user and an
agent read at the same level. What that view is, is settled under
Decisions.

## Done when

Every area of the repository's documentation is covered, in one of two
ways: excluded explicitly in the registry as not important, or
expressed reliably, precisely, and parsimoniously as high-level
abstract pseudocode, deterministically connectable to CLOA objects
that connect to
[the bedrock of determinism](/docs/system-legibility.md#the-bedrock-of-determinism).
None of it needs to be
implemented in code yet. The high-level abstract objects must be
complete, with low residuals.

## Planned

- **The parked rationale.** What the ports evicted sits in
  [Parking Lot](/no-more-slop-branch-working-files/PARKING-LOT.md).
  Decide what becomes of it.

## Completed

- **rulegen's missing-population failure.** A Standard with no
  `population` fails rulegen, now that the last one, the instruments
  Standard, is on the encoding. The generator is a first draft: a port
  that fails it may change the script or widen the encoding, and which
  one is decided at the failure. What the encoding cannot carry today
  sits in [the residual ledger](/doc-types/standard/residual-ledger.md).
- **Guide's registry sentence.** The registry's Guide row
  ([document-types.md](/standards/knowledge-organization/document-types.md))
  carries the Guide decision.
- **The card loop.** `doc-types/` became `standard-card/`,
  `standard/`, and `runbook/`, and `scripts/cardgen` writes
  `doc-types/standard-card/cards.txt` from the cut points the cards
  already had.
- **The Standard loop's design.** `doc-types/standard/` holds the
  definition, the two-table contract shape, the encoding, and the
  residual ledger.
- **The Standard loop's code.** `scripts/rulegen` writes the two
  tables to `doc-types/standard/standards.txt` and fails on drift.
- **The ports.** Build, Prose, Knowledge Organization, Tracking,
  Shell, Python, Testing, Modules, Decisions, Semantic Validation,
  Harness, the Meta-Standard, and Instruments, so every card is on
  the Standard encoding.
- **The port review.** Every ported Standard read file by file and
  scrubbed against the encoding.

## Deferred

Questions raised and not settled, none with a lean recorded. A deferred
question is answered when a port needs it, not before.

- **General-Sheet's replacement.** What replaces `General-Sheet`, which
  the user named a cop-out, and what type working-set files carry.
- **The doc-type family's own type.** The type the doc-type family's
  own files carry.
- **Guide as the procedure kind.** Whether Guide is the kind a
  procedure carries. The two `consuming.md` are typed `Standard` and
  describe themselves as recipes; Bootstrap and Tracker Operations, the
  same shape, are typed `Guide`.
- **Where exclusions are written.** Whether a population's exclusions
  are written in the population mark or in the file's prose.

## Decisions

**The axis.** Can a reviewer or a lint cite the document to reject work?
Yes is a Standard. No is something else: possibly a Guide, possibly a
file type not yet defined.

**Object.** A thing with a state readable at one moment: a file, a tree,
a pull request, an issue, a label set.

**Process.** Actions by actors over time, consuming and producing
objects. A process is described for a reader or executed by an agent.

Object and Process are provisional: it is not settled that either
needs defining precisely.

**State, never process.** "Reject", based on a Standard, means the state of an object at one
moment. Standards govern objects. A process is never audited by its
trace; it is checked only through the objects it produces. Auditing that
an agent followed a documented process step for step, and rejecting the
result on a deviation, is the wrong kind of audit and the wrong kind of
enforcement.

**Standard-Card.** The doc-type of the cards under `standards/`. The
shape, the cells, and the lint belong to the card, not to the Standard
it points at.

**Standard.** The kind a card's Define cell points at. One object class
as its population, plus named rules, each a predicate over that class's
state. The files typed `Standard` are this kind's population.

**Three collections, computed correspondence.** Think of it as code: a
collection of rules, a collection of audits, a collection of
enforcements. No rule states whether an audit or an enforcement
corresponds to it. Whether one does is a computation over the three
collections, and drift is what that computation finds.

**Rule IDs as atoms.** The rule ID already in the code,
`knowledge-organization.type-location` being one, is the atom that
joins the collections. Lean into it wherever it makes sense; sometimes
a judgment call is required instead.

**Every object becomes a doc-type.** Once the high-level pseudocode
objects are aligned on, each becomes a doc-type. That is the
innovation of doc-type: complex documentation expressed as simple,
precise pseudocode, which lets it all be scaffolded by 100%
deterministic code rising from the bedrock of determinism.

**Guide.** Explanation of a process or a system, read to understand it.
Never cited to reject.

**Location.** Cards stay flat under `standards/`, Standards stay under
`standards/<name>/`, and both lints stay. The documents a card points at
may live anywhere. A Define cell points only at Standards; a Guide is
linked from a Standard's prose, never from a card.

**The software factory.** Its current documentation is not worth
reorganizing around, and it is not the long-term state. It stays typed
`Guide` for now, knowingly mislabeled, and the factory needs no card
until its rules exist: the card `standards/software-factory.md` is
deleted, since every file its Define cell pointed at was a Guide, and a
card returns when a Standard exists to point at. The intended split,
when the rewrite comes:
object-state rules (the pull request body's sections, the cycle header,
the label four-tuple) become a Standard under
`standards/software-factory/`; the two regions and the moves between
them become a Guide where they are; the `gh` mechanics move into the
review runbooks. Rules that link to no standard are acceptable.

**The level.** A kind is expressed as a class with typed fields and
rules over its own state, one screen. A constraint on what a field may
hold goes in its type hint, not in a separate rule; a rule the type
hints already imply is dropped. Pseudocode is a thinking aid for
seeing the shape, not a target: no markdown is being translated to
Python. The rows of a Standard, the lint rule IDs, and any repo-level
binding object are below the level and stay out. Each doc-type's
class lives in its own `contract-shape.md`, every doc-type alike. The
model of the level:

```python
class StandardCard(Object):
    """One card per standard. Points; never restates."""

    question: str                       # "Governs how ..." — one breath

    # four cells; a cell is a list of pointers, or the literal word "none"
    define:  list[Pointer[Standard]]                # required, at least one
    audit:   list[Pointer[Audit]]    | None
    enforce: list[Pointer[Gate]]     | None         # Gate = commit | push | CI
    adopt:   list[Pointer[Adoption]] | None

    # rules: each a predicate over one card's state
    location    = path == f"standards/{name}.md"            # flat, never nested
    frontmatter = type == "Standard-Card" and description == question
    layout      = h2s == ["Define", "Audit", "Enforce", "Adopt"]
```

Defining the Audit and Adoption kinds is deferred.

**Only existing kinds.** The kinds expressed are the ones that exist:
Standard-Card, Standard, Runbook. Nothing new is invented until a port
needs it.

**Standard's shape.** Two primitives roll into Standard: ObjectClass,
the one class of thing with its exclusions, and Rule, name × condition ×
predicate. A condition narrows the member set, the way layer membership
does in the build standard and the kind of document does in the prose
standard; None means every member. A Standard carries no pointer back
to its card, which the path derives, and no rationale field. A rule
delegating to another Standard was considered and dropped: the other
Standard's population already binds the same object.

**The CLOA object of the standards is two tables.** A Standard is a
collection, not a sequence, so its view is a relation: unordered rows,
sorted for stable diffs, greppable, joinable. One generated file holds
the whole workspace:

```
standards
card    standard              population
build   canonical-artifacts   a repo's copy of one canonical file
build   skeleton              a repo's tracked tree
prose   conventions           an authored document, except type: Reference and exempt paths

rules
standard              rule                        when
canonical-artifacts   ci-yml-identical            —
canonical-artifacts   makefile-targets-present    python
conventions           no-first-person             harness-loaded
conventions           no-second-person            declarative
skeleton              pyproject-required          python
skeleton              readme-required             —
```

The view shows which rules exist, which Standard holds each, and which
card points at each Standard. Card to Standard is the standards table;
every other question is a grep. A third table, rule to lint, joins on
the rule column later, and drift is a set difference; no redesign.

**The CLOA object is not the complete system.** If it were, the tables
would be stored and everything beneath deleted. Rules keep their
markdown, examples, agents, and scripts beneath the view. The object's
job is to let the user and the agent operate at the same level in a
structured way; the system stays more complex underneath.

**Two determinisms.** The focus is deterministic construction of CLOA
objects, the way chaingen parses runbook spans into chains.
Deterministic linting is wanted wherever it comes free and is not
required: the branch can merge without a new linter.

**Greenfield license.** Every standard file may be rewritten entirely:
restructured, split, merged, moved between files, new files made.
Preserved: what each rule means, and what each existing lint checks.
Headings, tables, and file boundaries in today's files are not
constraints.

**A document does one thing.** The standing principle in
[System Legibility](/docs/system-legibility.md#standing-principles),
and the guide for every representation and encoding invented from
here: a document does one thing, predictably, in a structured way, and
the thing and its structure are fixed at the CLOA by the document's
type. A Standard's one thing is one population and its rules. Content
found in an existing file that cannot sit in a Standard without
breaking this moves to the parking lot.

**The parking lot.** One location, under the greenfield license, for
what is important but belongs elsewhere: evicted rationale,
heuristics, anything a port cannot place. It exists so nothing is
forgotten while a port moves fast; sorting it is its own item under
Planned.

**Condition, not guard.** One word serves both doc-types, defined in the
root's terms bucket
([No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#terms));
"guard" is not used.

**One encoding.** One written form for the population, one for a rule
with its name, one for a condition, designed for the parser and made
once in the Standard doc-type's encoding file. Everything unmarked is opaque
prose the parser carries but never reads, so examples, definitions,
and rationale sit wherever the writer wants them.

**Rule ids follow the card.** A lint rule's prefix is the card whose
Audit cell cites the detector, which standards-lint's rule matrix
holds; a rule that moves to another card takes that card's prefix.
The Build port's pin and dogfood rules became `distribution.pin` and
`distribution.dogfood` this way.

**The slug is the anchor.** A rule's id in the view is its heading's
GitHub slug, the anchor a link to the section uses and the one
ref-lint resolves. A condition's `when` value is the same slug. No
second naming rule.

**Enforce has two modes.** Audit reports and never mutates, which is
what the English word means, so a tool that rewrites an object into
conformance is not an audit. Enforce is what compels conformance, by
refusal at a gate or by rewrite on demand, a script or skill the user, a
schedule, or a process step invokes. An Enforce bullet marks its mode in
bold, a rung name or `on demand`. Adopt is first pickup only: a
scaffold, a template, a migration, a recipe. No fifth cell. A formatter
is a detector by its check mode, `shfmt -d`, and Enforcement by its
write mode at the gate, so shfmt keeps its Audit row on the Shell card.

**Standard's build follows Runbook's.** Definition, contract shape (the
two tables), encoding, generator with a drift check, ports, residual
ledger.

**`doc-types/` is three.** `standard-card/`, `standard/`, `runbook/`
— one directory per doc-type, each holding that doc-type's definition,
contract shape, encoding, residual ledger, and generated view.

**Instruments.** On the encoding like every other card, ported with
the smallest change that slices, so the generator has no special case.
The user does not stand behind instruments in their current form and
plans to remake them, so the port relaxes where the file does not fit
rather than inventing, and nothing in this refactor is built on them.

## The rule/procedure split

Located, because the user wanted to remember where it is. One home:
[File Roles](/standards/knowledge-organization/file-roles.md). The
imperative-versus-declarative voice rule is two conditioned rules in Doc
Conventions,
[Imperative and second person](/standards/prose/conventions.md#imperative-and-second-person)
and [Third person](/standards/prose/conventions.md#third-person).

## Out of scope

Judgments. The user is not happy with them and may delete them soon. No rule in this refactor is checked by a judgment, and no
shape is designed to hold one. `judgments/docs-match-code.yaml` holds
the four judgments the branch leaves.

## Acronyms

None.
