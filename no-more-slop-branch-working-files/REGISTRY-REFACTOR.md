---
type: General-Sheet
title: Registry Refactor
description: The decisions aligned on for the document-type registry refactor — the rejection axis, the abstractions, the software factory's position, and the open questions
---

# Registry Refactor

The decisions the user and Claude aligned on in the 2026-09-02 sessions
that opened the registry refactor. Member of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md). The
file counts and per-file readings behind these decisions are the audit
record, [Registry Audit](/no-more-slop-branch-working-files/REGISTRY-AUDIT.md);
nothing there is a decision.

Only what was said in those sessions is written here. Where a question
was raised and not settled, it sits under Open questions with no lean.

## Goal

Refactor the document-type registry before building any new doc-type:
settle what a Standard is, what a Guide is, and how the kinds are
organized. The settling happens at one level, parsimonious and precise
enough to show on screen. Decisions are made at that level; everything
below it is implementation, audit, and enforcement.

The end product is a CLOA object for the standards: a view, generated
by deterministic code from the standard files, that the user and an
agent read at the same level. What that view is, is settled below.

## Decisions

**The axis.** Can a reviewer or a lint cite the document to reject work?
Yes is a Standard. No is something else: possibly a Guide, possibly a
file type not yet defined.

**State, never process.** "Reject", based on a Standard, means the state of an object at one
moment. Standards govern objects. A process is never audited by its
trace; it is checked only through the objects it produces. Auditing that
an agent followed a documented process step for step, and rejecting the
result on a deviation, is the wrong kind of audit and the wrong kind of
enforcement.

**Object.** A thing with a state readable at one moment: a file, a tree,
a pull request, an issue, a label set.

**Process.** Actions by actors over time, consuming and producing
objects. A process is described for a reader or executed by an agent.

Object and Process are provisional: it is not settled that either
needs defining precisely.

**Standard-Card.** What the built doc-type today named Standard actually
is: its own definition file says the family is the population of cards
under `standards/`, so the shape, the cells, and the lint belong to the
card. Rename it.

**Standard.** The kind a card's Define cell points at, and the doc-type
not yet built. One object class as its population, plus named rules,
each a predicate over that class's state. Today's 38 files typed
`Standard` are this kind's population.

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
Never cited to reject. The registry's sentence "not to be measured
against" is retired and replaced by what a Guide is.

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
the whole workspace in two tables:

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
forgotten while the ports move fast; sorting it is its own action
item, after the ports.

**Condition, not guard.** The member subset a rule binds is its
condition, the word Runbook already uses for what must hold for an
edge to fire; one word serves both doc-types, and "guard" is not used.
A rule with no condition binds every member.

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

**Standard's build follows Runbook's.** Definition, contract shape (the
two tables), encoding, generator with a drift check, ports, residual
ledger.

**`doc-types/` becomes three.** Today it holds `standard/` and
`runbook/`, and `standard/` is Standard-Card's files under Standard's
name. It becomes `standard-card/`, `standard/`, `runbook/`.

## Findings from two readings

Readings, not decisions. Each proposal below is evaluated file by file
when its port happens; the reading was one pass, and the agent doing
the port checks that each move still makes sense in the moment.

**Build, the structural reading.** Nine files under `standards/build/`,
all pointed at by the Build card through two Define pointers. They hold
rules over three object classes, plus a definition of the Gate kind, a
distribution channel, a procedure, and rationale. The proposed port:

- Skeleton stays: layers.md merged into skeleton.md. Population: a
  repo's tracked tree. Layer membership becomes the conditions, read from
  facts on disk; each entry is a presence rule, required, optional, or
  forbidden. Layers is not a Standard of its own.
- Canonical Artifacts stays: canonical.md absorbs ci.md, make.md's
  target table, and python.md's pyproject section. Population: a
  repo's copy of one canonical file, with the compare mode as
  per-member data. The files under `canonical/` are the content.
- Python Project stays: python.md less the pyproject pins, the
  Rationale, and Initial setup. Population: the root Python project.
  It sits on the boundary with the Python card; lean Build, since it
  is layout.
- Enforcement leaves for the Meta-Standard card. Its gate table is the
  definition of the Gate kind, the thing a card's Enforce cell points
  at. Its Map is the hand-written form of the computed join and is
  retired. Its one rule over a pull request, a red CI run is never
  merged, goes with the pull request rules.
- Distribution becomes its own card. Its question is how dev-playbook's
  checks reach the governed repos. Populations: the hook manifest, the
  roster in workspace-lint's source, a publisher's own config. The
  consumer-side pin is already a row of the canonical pre-commit
  config.
- Bootstrap leaves Define. It is two procedures; it stays under Adopt,
  retyped, since the enable-repo-governance runbook shadows it.
- Rationale in python, ci, make, and distribution leaves the
  Standards. A Standard boils down to its rules and the specific ways
  they are enforced, and rationale is neither. It moves to a parking
  lot; what becomes of it is its own action item, and it is not a
  Guide, because it guides nothing. The pyproject rationale is worth
  keeping.
- make.md's judgment-cache and per-machine paragraphs belong to
  Semantic Validation and machines.md.

**Prose, the prose reading.** Two files under `standards/prose/`.
Population: an authored document, except `type: Reference` mirrors and
the paths a repo lists in `.prose-lint-exempt`; that declaration is
conventions.md's opening paragraph. Roughly thirty rules across
conventions.md and slop-tics.md. Most predicates are English and will
stay English; a reviewer citing them satisfies the axis. Person of
address is one rule with two conditions, harness-loaded and declarative.
Each tic's definition and before-and-after examples stay in the body,
below the collapse, like a runbook's fine steps. "How to decide between
section formats" read as a writer's heuristics on its heading alone;
each of its bullets is a predicate over a block as it stands, so it
stays as a rule under a stateful heading, Block form fits its
content. The lint
rule names do not match today's headings: `prose.banned-word` sits
under "Terminology: the person is the user"; renaming happens at port
time.

## The rule/procedure split

Located, because the user wanted to remember where it is. One home:
[File Roles](/standards/knowledge-organization/file-roles.md). A rule
binds every actor who touches the thing, whatever job that actor is
doing; a procedure binds one actor for the length of one run. The split
is declared "a general aim, not a strict gate". The
imperative-versus-declarative voice rule is two conditioned rules in Doc
Conventions,
[Imperative and second person](/standards/prose/conventions.md#imperative-and-second-person)
and [Third person](/standards/prose/conventions.md#third-person).

## Open questions

Raised, not settled. No lean recorded.

- What replaces `General-Sheet`, which the user named a cop-out, and
  what type working-set files carry.
- The type the doc-type family's own files carry.
- The files typed `Standard` that describe themselves as recipes, the
  two `consuming.md`. Bootstrap was the third; the Build port retyped it
  `Guide`, and whether Guide is the kind a procedure carries is not
  settled.
- Whether a population's exclusions are written in the population mark
  or in the file's prose.
- Which of this file's decisions move to a permanent home in the
  repository, and where. Some will; not all; which is not yet known.
- Edge cases not yet examined.

## Out of scope

The instrument, the instrument spec, and anything to do with
instruments. The user is not happy with the current implementation and
does not want to delete it either. Set aside; not thought about in this
refactor.

Judgments, the same way. The user is not happy with them and may delete
them soon. No rule in this refactor is checked by a judgment, and no
shape is designed to hold one.

## Done when

Every area of the repository's documentation is covered, in one of two
ways: excluded explicitly in the registry as not important, or
expressed reliably, precisely, and parsimoniously as high-level
abstract pseudocode, deterministically connectable to CLOA objects
that connect to the bedrock of determinism. None of it needs to be
implemented in code yet. The high-level abstract objects must be
complete, with low residuals.

## Next steps

In order. Each kind runs one loop: design, then the files, then the
code that reads them. For the Standard loop the code moves up: it
comes after the first port, Build, so every later port is checked
against a generator, the way cardgen checked the cards. The first
draft of the generator is not locked in; a port that fails it may
change the script or widen the encoding, and which one is decided at
the failure.

Done: `doc-types/` is three, `standard-card/`, `standard/`, `runbook/`,
and the card loop is closed. The Standard-Card files sit under their
real name, `doc-types/standard-card/`; its encoding names the cut
points a cell's bullets already had, the lead, the spaced em dash, the
first link, and the bold gate; `scripts/cardgen` prints
`card, cell, pointer` to `doc-types/standard-card/cards.txt` and fails
on drift. Four bullets in four cards moved to fit the encoding, meaning
kept.

Done: the Standard loop's design, reviewed and committed.
`doc-types/standard/` holds the definition, the contract shape with
its two-table view, the encoding, and an empty residual ledger; the
encoding is the authority on the marks. Doc Conventions is the one
Standard in the encoding, and the parking lot,
[Parking Lot](/no-more-slop-branch-working-files/PARKING-LOT.md),
exists and is empty. Permanent files carry the design and no progress
notes; what is ported, what is built, and what remains is tracked only
here.

Done: the Standard loop's first port, Build, reviewed and committed.
Nine files became five Standards across three cards: File Skeleton,
Canonical Artifacts, and The Python Project under Build; Distribution
Channel under the new Distribution card; Gates under the Meta-Standard.
Bootstrap is a Guide under Adopt. The rule ids that changed cards
changed prefix. Two calls were reviewed and stand: required files are
one rule at repo-lint's grain, and a rule's id is its heading's GitHub
slug. Residuals are in `doc-types/standard/residual-ledger.md`, evicted
rationale and heuristics in the parking lot.

Done: the Standard loop's code. `scripts/rulegen` writes the standards
and rules tables to `doc-types/standard/standards.txt` and fails on
drift; the six encoded Standards slice clean. A first draft, open to
change. A Standard with no `population` key is named on every run and
skipped; when the last port lands, that skip becomes the failure the
class's frontmatter rule states.

Done: the Prose port. Slop Tics is one rule of Doc Conventions, No
slop tics, pointing at the catalog the way Canonical Artifacts points
at its files. The catalog is typed `General-Sheet` until the open
question on that type is settled, and the document-remove-tics skill
is the Prose card's Adopt pointer, since it mutates and is not gated.

1. The Standard loop, remaining ports. Every other card, each read and
   split in the moment the way Build was, with cards added, merged, or
   removed as the reading demands, and each checked by rulegen before
   review.
3. Decide what becomes of the parked rationale.
4. Then the remaining open questions.

## Acronyms

None. CLOA is defined in the root, [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#acronyms).
