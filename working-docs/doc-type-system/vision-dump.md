---
type: General-Sheet
title: Vision Dump
description: The raw, fragmented source material for the product vision of the doc-type system, the fact base, and the viewer — the user's ideas as spoken, unordered, unpolished, kept as the quarry the vision document is cut from
---

# Vision Dump

Raw. Fragmented. Stochastic on purpose. The user's ideas from one
conversation on 2026-09-15, thrown down before any of them is shaped
for a reader. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md). The
vision document that comes from this is a sales pitch: calling the
shot, admitting nothing is built, pointing at the prototypes that fit
together. This file is the quarry. Nothing here is for a reader.

## Files read

The exact files read before this conversation, so a fresh session
reads the same ones. Plus `standards/index.md` per the global rules.

- `docs/system-legibility.md`
- `docs/working-in-loops.md`
- `working-docs/doc-type-system/ROOT.md`
- `working-docs/doc-type-system/doc-type-system/ROOT.md`
- `working-docs/doc-type-system/doc-type-system/reference-model.md`
- `working-docs/doc-type-system/doc-type-system/specification/doc-type.md`
- `working-docs/doc-type-system/doc-type-system/personal-notes.md`
- `working-docs/doc-type-system/doc-type-system/ontology-solvers.md`
- `working-docs/doc-type-system/doc-type-system/writing-predicates.md`
- `working-docs/doc-type-system/fact-base/ROOT.md`
- `working-docs/doc-type-system/fact-base/fact-base.md`
- `working-docs/doc-type-system/fact-base/precedent.md`
- `working-docs/doc-type-system/fact-base/deterministic-separation.md`
- `working-docs/doc-type-system/loop/ROOT.md`
- `working-docs/doc-type-system/loop/specifying-a-loop.md`
- `working-docs/doc-type-system/viewer/ROOT.md`
- `doc-types/doc-type.md`

Style model for the vision doc: `docs/system-legibility.md`. Draft in
progress: `working-docs/doc-type-system/vision.md`, branch `vision-doc`.

## The chain

doc-type system → fact base → viewer. That order. Each enables the
next. Loops are secondary, not the point. A loop is just a doc-type.
One of three.

CLOA is important. It is defined in
[System Legibility](/docs/system-legibility.md#the-cloa). The highest
level you can trust the AI, the lowest level it needs you. Too low:
rubber stamping. Too high: vibe coding.

## The slop trench

Open here. Deep in it. What it is like. Describe it.

- More output than can be read. Piles of text and code. Greppable by
  AI, illegible to the user.
- Fixes consumed once, turn by turn. Next dispatch, same slop.
- Intent debt accumulating. Don't know if the system matches intent
  because don't comprehend the system.
- Specs as code: failure. Just more slop. And I don't understand it
  either. Spec-driven development led me astray.

## Everyone knows the fix

Embed determinism within your system. This is the way. Everyone knows.

Examples, other than markdown, because the doc-type system isn't
revealed yet:

- types and type checkers
- schemas, JSON Schema, Pydantic at the door
- linters, formatters
- tests
- database migrations, constraints, foreign keys
- contracts, interfaces
- CI gates
- state machines

## Markdown is now code

Markdown is code. A fuzzy random form of it. The LLM is the stochastic
compiler. AI creates more code and documentation than we can possibly
look at directly.

User understanding of their system is more important than ever. More
system, less time, more at stake.

One way of understanding: point an AI at it. "Describe this system."
Slow. Expensive. Random. Different answer each time. Can't trust it.

## Coders solved this long ago

Deterministically generated CLOA objects:

- call graphs
- import graphs
- class hierarchies, class diagrams
- dependency graphs
- control flow graphs
- the call stack in a debugger
- coverage maps
- type signatures, API docs from source
- database ER diagrams
- the file tree itself

Define CLOA here. The correct level of abstraction. A view of the
system derived deterministically from structure embedded in the files.
Cheap. Fast. Identical until the checkout changes. Trustworthy because
deterministic.

## Mourn our craft

Too bad we can't write code anymore. "Mourn our craft." The well-known
post, the phrase going around.

Back to CLOA objects. How can we generate these now that code is a
mixture of code and markdown? Call graphs don't reach into prose.

Man I wish we could still program. Too bad we're not allowed to
program anymore.

Programming was fun. I could construct precise creations in my
imagination and then make them reality. The compiler would make it
happen. All the beautiful things:

- inheritance
- composition
- interfaces
- invariants
- types
- encapsulation
- abstraction
- polymorphism
- contracts

Too bad we can't program anymore. AI has taken it away.

Or has it????

## The doc-type system is the answer

Back to embedding deterministic structure in our system. Embed
deterministic structure IN YOUR MARKDOWN, based on the doc-type system
you PROGRAMMED.

A doc-type is more than sugar sprinkled on the markdown. It's linted.
It's encoded. It's deterministically guaranteed with an ontology
solver.

Key pushback to preempt: this isn't "making things up." It's 100%
backed by deterministic code all the way down, and a defined ontology
validated deterministically. Not vibes. Not a metaphor. A parser, a
lint, a solver.

The terms, from the working set
([Terms](/working-docs/doc-type-system/ROOT.md#terms)), used when
the system is introduced:

- doc-type: gives markdown what code has, structure, a contract, an
  API, a type
- instance: one file of that type
- primitive: one named element of a vocabulary, `reads`, `contains`
- vocabulary: the closed set of primitives one doc-type owns
- operation, verb: a doc-type's verbs, read, write, do, hold, act,
  check, yield
- part: a class nested inside a doc-type, an Edge, a Rule
- encoding: the map from written form to rows, the grammar
- extractor: the function the encoding defines, file to rows
- predicate, rule, specification, target state
- population: what a Standard ranges over
- residual: what the primitives can't express, the ledger
- the doc-type build loop: re-express, record the residual, propose a
  primitive
- reference model and specification, the witness and the set

Three doc-types today: Runbook is invoked, Standard is held to, Loop
drives. Ten verbs. The pseudocode in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md).

## Turtles all the way up

Thus we can PROGRAM, UPWARDS UP THE ABSTRACTION LADDER, with
deterministic scaffolding holding our AI creations stable as we move
up.

"It's turtles all the way up."

Examples of climbing the ladder. Each rung deterministic, each rung
holds the one above:

- git tree → file nodes, contains edges
- markdown links → links-to edges
- frontmatter → attributes
- a runbook's reference chain → reads, writes, does edges with order
  and condition
- a Standard's rules → predicates with ids and kinds, verifiers
- a loop → acts, checks, yields over runbooks and standards
- a fact base → all of it, one object per checkout
- a view → a selection

The bedrock of determinism, from System Legibility. The doc-type
system stacks declared abstractions on it. Stochasticity is a scale
per file, not a line between file kinds. The residual is what's
outside the declared structure.

## The fact base, then the viewer

Pivot. The agent is constrained to operating within the things you
programmed with the doc-type system. Good. But also: how do we
describe and view our system? Call back to the call graph, the class
diagram.

The fact base. The doc-type system, programmed ephemerally in markdown,
becomes concrete through the ontology, lands in the fact base. One
deterministic object of nodes and edges per checkout. Every row with a
receipt: the extractor and the line that produced it.

Now fast, efficient, deterministic code constructs any view of the
system. A view is a selection. It drops rows, never adds one.

Name the main views planned
([Views are selections](/working-docs/doc-type-system/fact-base/fact-base.md#views-are-selections)):

- containment tree: how is it organized
- catalog: what exists
- dependency graph: how do parts relate
- control flow: what happens in what order
- data flow: what is produced and consumed
- cross-reference matrix: which X take part in which Y
- interface card: how one thing is used

The viewer draws them. cloa-viewer. Local. Browser. No model token
spent to put anything on screen.

CLOA communication with the agent: the agent is constrained by what
you programmed, and you see the system through what you programmed.
Same structure both ways. The vocabulary API.

## Examples: this repo

After the fact base and viewer are introduced. dev-playbook's own
doc-types:

- Runbook: skills and agents. Reference chain: what it reads, writes,
  does, reports. The software factory as a graph of does edges.
- Standard: population and rules. The commit gate as a boundary
  naming rule ids.
- Loop: acts, checks, yields. The Ralph loop, hand-simulated, nineteen
  nodes, forty-one edges.

## Examples: wild, imaginary, other repos

Doc-types are general and customizable, the same way code is. As
general as programming, which is to say very general.

- A web page repo: a Page doc-type, a Component, a Route. Views: the
  route tree, which component reaches which API.
- My niece's lemonade stand: Recipe, Shift, Supplier, Price. A loop
  that checks the ledger against the recipe. A view: what each shift
  consumed.
- Studying for school: Topic, Source, Flashcard, Session. A Standard
  holding every flashcard to one source. A view: which topics have no
  source.
- A job search: Job, Company, Application, Interview. Already in
  [Ontology Solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md#two-ontologies).

Document ontology once, in dev-playbook. Domain ontology per repo.

## The people this is for

People who enjoyed programming. Who enjoyed thinking at these levels
of abstraction and detail. Smart people like us. We can think this
way; not everyone can.

This stuff can still be fun. Even when we move up the stack and AI
takes the bottom. We still have value at this higher level. The
precise imagined creation, made real, is still available. The compiler
is now a lint, an encoding, a solver, a fact base.

## What this document is

A sales pitch. Calling our shot. Acknowledging we haven't built it
yet. Pointing via workspace links to the prototypes we think fit
together:

- the doc-types built: [doc-types/](/doc-types/index.md)
- the reference model and specification, in the working set
- the Ralph fact base, hand-simulated
- cloa-viewer, two loops built, the room and the vertical slice
- chaingen, rulegen, loop-lint, the extractors that exist today

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **LLM** — Large Language Model.
- **API** — Application Programming Interface.
- **ER** — Entity-Relationship.
