---
type: General-Sheet
title: Turtles All the Way Up
description: The product vision for the doc-type system, the fact base, and the viewer — why programming did not end, and how it moves one level up the stack
---

# It's Turtles All the Way Up

> This draft was written by Claude from the user's notes. Apologies
> for the Claude-ish. The user will write it themselves soon.

## The slop trench

The AI writes faster than we can read. We correct it turn by turn.
Each correction is consumed once, and the next dispatch makes the same
slop. We tried writing the spec first. The spec was more text, written
by the same AI, and we understood it no better than the code it
described. Two hours at the keyboard, we look up, and we do not
remember what we were doing or why.

Some people call this AI psychosis. We call it the **slop trench**.
The system grows; our understanding of it does not. We cannot say
whether it matches what we meant, because we no longer comprehend it.
That gap is **intent debt**.

Will you work more? Read the code even harder? Might as well not use
AI.

## Deterministic backpressure

Everyone knows the way out. Embed determinism in the system.

Programmers have done it for decades. Types. Schemas. Tests. Linters.
CI gates. That is **deterministic backpressure**.

Too bad none of it reaches us now. Our instructions are markdown and
natural language. There is no type checker for a paragraph.

## Markdown is code now

A markdown file an agent obeys is a program. Its interpreter is a
language model: fuzzy, random, a different result every run. Still
code. Our systems are now half the old kind and half the new, and the
AI writes more of both than anyone can read.

We could point the AI at it and say "describe this system." Slow.
Expensive. Random. Can't trust it.

## The CLOA

Programmers solved this long ago. Call graphs. Import graphs. Class
hierarchies. The call stack. Coverage maps. Deterministic objects, each
generated from the source, each answering one question.

Each one sits at the **correct level of abstraction**, the CLOA: the
highest level at which we can trust the picture, and the lowest at
which the picture still needs us. Too low, we stop looking: *rubber
stamping*. Too high, we think we understand and we don't: *vibe
coding*.

Those objects are read out of structure the compiler put in the
source. Half our source is prose now. There is no call graph for a
prompt.

## Mourn our craft

And programming was fun! We held a precise thing in our heads, wrote
it down, and the compiler made it real. Types. Inheritance.
Composition. Interfaces. Invariants. The whole toolkit for building
something exact out of ideas. AI took the keyboard, and the toolkit
went with it.

Or did it?

## Objects of our own creation

Programming was never the language. It was the objects. A language
fixes the primitives: its types, its operators, its control
structures, its rules for composition. On top of those the programmer
declares the things a system is made of, the relations between them,
and the operations each one answers to. Then a type checker, a
compiler, and a test suite hold the declarations to account. The
language was fixed. The objects were ours.

The doc-type system is the same act with the language no longer
fixed. We declare the primitives too. A **doc-type** is a type we
define: its verbs, its parts, the rule for where its instances live,
and an encoding that says which marks in a markdown file carry which
primitive. A lint rejects a file that breaks the encoding. An
extractor reads the file into rows. A solver checks the rows against
the declared types. That is a type checker, a compiler, and a test
suite for a language we made up.

We have three doc-types today. A Runbook is invoked. A Standard is
held to. A Loop drives. Ten verbs across the three. The whole system
fits in
[one page of pseudocode](/working-docs/doc-type-system/doc-type-system/reference-model.md),
and the predicates every doc-type satisfies fit in
[another](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md).

This is not making things up. Every declaration is held by
deterministic code all the way down, and the declarations together
form an ontology a solver validates. Same as a program.

## Turtles all the way up

Each rung is deterministic, and each rung holds the one above it. The
git tree gives files. Markdown gives links. Frontmatter gives
attributes. A runbook's encoding gives what it reads, writes, and
does. A Standard's encoding gives rules with ids. A loop's encoding
gives acts, checks, and yields over the other two. We stopped
programming at the bottom and started programming above it.

## So what?

We declared some types and wrote some markdown against them. Who
cares. What does it do?

Go back to the CLOA. We could ask the AI to describe the system.
Slow, expensive, random, can't trust it. But what if the objects were
generated deterministically, by a system we programmed ourselves, and
we understood every step of how they were generated? We could trust
that, couldn't we.

## The fact base

That is the fact base. One object per checkout: a set of nodes and a
set of edges, written by deterministic code, every row carrying a
receipt that names the extractor and the line it came from. The
doc-types we declared are the schema. The extractors their encodings
define are the only code that touches a file.

Every view is a selection from it. A view drops rows; it never adds
one. The views we plan:

- **containment tree** — how is it organized
- **catalog** — what exists
- **dependency graph** — how do parts relate
- **control flow** — what happens in what order
- **data flow** — what is produced and consumed
- **cross-reference matrix** — which X take part in which Y
- **interface card** — how one thing is used

The call graph, the import graph, the class hierarchy. For a system
that is half prose.

## The viewer

cloa-viewer draws them, in a browser, from files on disk. No model
token is spent to put anything on screen.

This closes the loop. The agent is constrained to the objects we
programmed. We see the system through the same objects. The
vocabulary the agent obeys and the vocabulary on our screen are one
vocabulary, and we wrote it.

## As general as programming

In this repo: a Runbook's reference chain shows what a skill reads,
writes, and does. The software factory is a graph of does-edges.
A Standard's rules have ids, and the commit gate names the ids it
runs. A Loop's acts, checks, and yields draw as a graph.

Elsewhere, anything. A web app: Page, Component, Route, and a view of
which route reaches which API. A lemonade stand: Recipe, Shift,
Supplier, and a loop that checks the ledger against the recipe. A
semester: Topic, Source, Flashcard, and a Standard holding every card
to one source. A job search: Job, Company, Application, Interview.
Doc-types are as general as programming, which is to say very.

## Who this is for

People who liked programming. Who liked holding an exact structure in
their head and making it real. Not everyone thinks this way. The ones
who do are not obsolete. The fun moved up a level, and so did the
value.

## Calling the shot

None of this is finished. The pieces that exist:

- [The three doc-types](/doc-types/index.md), with their encodings
  and residual ledgers.
- [The reference model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
  and [the specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md).
- [Ontology solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md),
  the route from pseudocode to a solver.
- [The Ralph fact base](/working-docs/doc-type-system/fact-base/fact-base-ralph.md),
  one subsystem simulated by hand: nineteen nodes, forty-one edges,
  every row with a receipt.
- [cloa-viewer](/working-docs/doc-type-system/viewer/ROOT.md), two
  loops built, the tree and the file panel on screen.
- The extractors that exist today: `chaingen`, `rulegen`, `loop-lint`.

We think they fit together. We have not proven it. That is the shot.

We thought we lost programming. We didn't. It moved one level up
the stack, and the stack is deterministic underneath us. It's
turtles all the way up.
