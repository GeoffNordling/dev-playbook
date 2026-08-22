---
type: General-Sheet
title: Scratch
description: Where the slop reduction stands — the CLOA, the code toolbox, and the open documentation work
---

# Scratch

What I decided on the day I stopped digging, and why.

## The problem

Six months of building this way has produced a lot of slop. Almost everything in
this repository was written by Claude from intent I gave in a conversation.
Claude then produced documentation and code that I cringe at, that I do not have
the mental energy to read, that confuse me when I do try to read them, and that
I would not hold up as my own work. I do not understand how much of it works. I
have a vague memory of what I told Claude to do, but I rarely look at the code.
I have mostly stopped reading the documentation, because Claude's writing style
annoys me.

Too much of this repository is slop.

The best thing to do when you find yourself in a hole is to stop digging. Let's climb out.

## The Correct Level of Abstraction (CLOA)

The CLOA is the level of abstraction where the AI and the user communicate with
each other using the exact same terminology.

`CONTEXT.md` is the anchor. I have not embraced it the way I should. We engineer
it deliberately, so that it focuses both the user and the AI on the correct
shared terminology at the CLOA.

- I read this file directly, and I hold a 100% understanding of everything in it.
- The AI uses terminology from `CONTEXT.md` in all of its communication.
- When the AI needs a term that is not in the file, it adds it on the spot, and I
  review, understand, and approve the addition.

There is zero vibe coding in this file. For slop reduction, it is the most
important file on the machine.

Matt Pocock, who originated this file, has a methodology for making it
hierarchical. I have not explored it and will not now, because that is premature
optimization.

## Stochastic functions and deterministic backpressure

Working with AIs combines two things:

- **Stochastic functions** — prompts, models, agents. Focused, but not
  repeatable.
- **Deterministic backpressure** — detectors, linters, enforcement gates. Fixed
  and repeatable. This also includes plain contact with reality during
  implementation: running the thing and seeing what happens.

Use deterministic backpressure wherever we can. Sometimes stochastic functions
are required — that is the power of AI.

These tools exist to hide complexity behind deterministic code and give me a
simple interface onto it. So the ones worth adopting fail the build with a
one-line message, the way ruff names a file, a line, and a rule id. A tool that
produces something to look at instead, such as a call-graph HTML page, needs me
to read it. I will read one when I need to, but it is much more work than a
one-line message and much less useful to the AI.

## Move slowly in decision space

The past failure was planning too much and trying to move too far in one leap. So
we take smaller iterative steps and take backpressure from reality at each one.
What must stay small is how much we commit to before reality answers back.

## The code toolbox

### Adopt

- **ruff** — already running. Add `C901` so that over-complex functions fail
  lint. No new dependency.
- **mypy, tightened** — raise strictness above its current settings. Exact flags
  undecided; full `--strict` is not automatically the answer.
- **import-linter** — a declared contract over module dependencies, for example
  "`config` must not import `cli`". Fails CI when an import crosses a forbidden
  line.
- **Rendered API surface** — `mkdocstrings` or `pdoc`, both built on `griffe`.
  Public signatures plus docstrings, which is the read-a-module-at-a-glance view.
- **Import graphs and call graphs** (`pydeps`, `code2flow`) — read side by side.
  See "Import graph and call graph" below.
- **ruff `D` rules** — already in place. See "Docstrings" below.
- **`tests/acceptance/`** — see "Tests in two tiers" below.

### Undecided

- **Hypothesis** (property-based testing) — state one invariant, and the library
  generates hundreds of inputs and shrinks any failure to a minimal example. One
  readable property can replace fifty example tests, which compresses reading.
- **Gherkin / BDD** — the most readable form of acceptance tests. Uncle
  Bob spoke well of it on a podcast I enjoyed. Worth remembering, not worth
  shoehorning in.
- **Sequence diagrams** (Mermaid) — lifelines down the page, calls left to right,
  returns back. Cheap to generate from text when tracing one operation.
- **coverage.py** — not as a percentage to chase. As a detector: uncovered code
  is code that nothing forces to be correct.

### Rejected

- **radon / xenon** — `C901` covers this inside a tool we already run.
- **vulture** — whole-program dead-code detection. Dead code is not a priority.
- **pyright** — one type checker is enough, and we have mypy.

## Docstrings

- **The gate.** `pyproject.toml` selects ruff's pydocstyle `D` family, with
  `convention = "pep257"`, `D401` disabled to keep the noun-phrase voice, and
  `tests/` exempt. It runs in pre-commit and in `make check`. A missing docstring
  fails the commit.
- **The prose.** `standards/python/style.md` states the rule and explicitly
  delegates enforcement to ruff.
- **The gap.** `D` checks presence and format only. "Does the thing" passes.
  Docstring *quality* stays stochastic, held by the review agents. That is the
  right assignment.

## Gray modules

Matt Pocock's term. If I understand a module's tests and the tests pass, I have
an approximate understanding of the code beneath. The module is not a black box.
It is gray.

## Two testing tiers

I intended to read all my tests. I abandoned that, because there are a thousand
of them and a good number are surely slop.

The failure was having one undifferentiated tier.

- **The unread tier.** The existing thousand-odd unit tests. Machine-written and
  machine-maintained. Judged by passing, never by my eyes.
- **The acceptance tier.** `tests/acceptance/`. Small and capped. Written in
  `CONTEXT.md` terminology. One test per behavior I could state in a sentence. I
  read 100% of these. This tier is to tests what `CONTEXT.md` is to docs.

This is the orthodox test pyramid. Undesigned so far: the deterministic gate that
keeps the acceptance tier from bloating back into a swamp — a size cap, naming
rules, or a rule that every public module has at least one.

## Import graph and call graph

- **Import graph.** Nodes are modules, edges are `import` statements. Four to a
  few dozen nodes. This is at the CLOA: I can hold it in my head, and
  `import-linter` can enforce rules against it.
- **Call graph.** Nodes are functions, edges are calls. Hundreds of nodes. Below
  the CLOA, so it is for tracing one operation rather than for holding the whole
  codebase in mind.

Collapse a call graph up to module level and you get roughly the import graph.
The two disagree here:

- **Imports with no calls** — `from .types import Config` for a type annotation,
  a constant, or an exception class.
- **Calls with no import** — a callback passed in as an argument, or a plugin
  loaded by name. Static tools usually miss these entirely.
- **Re-exports** — `__init__.py` importing everything to expose it creates a hub
  the call graph knows nothing about.

Only `import-linter` fails the build, and it checks the import graph against
rules I write.

## The documentation toolbox

Not yet examined. Raw material only.

- `CONTEXT.md` discipline, as described in the CLOA section.
- **OKF graphs.** One is implemented but has not been used in a while and may
  need updating. A heavy HTML file may be the wrong format.
- **OKF traces.** If we have an OKF graph, then an operation can be expressed as
  markdown instructions that trace a path through it.
- **Markdown complexity detectors.** No specifics yet on how to measure the
  complexity of a document, but surely something is measurable.
- **Doc linters.** We have them, and in their current form they are pedantic —
  they check that certain headings are present. I am not using them as well as I
  could. We could decide what is actually worth linting for and design linters for
  that.
- **The core problem.** Documentation needs far more reading by the user than code
  does. Code is deterministic and can be pinned down by the tools above.
  Documentation can only be taken so far by deterministic tools; a lot of the
  time it just has to be read. I am incapable of reading Claude's slop-filled
  style, so something has to keep the documentation a pleasure to read.

## New terms

Candidates for `CONTEXT.md`:

- **CLOA** (Correct Level of Abstraction)
- **Deterministic backpressure** and **stochastic function**
- **Unread tier** and **acceptance tier**
- **Gray module**
- **Slop**

Writing standards and the named tics are in
[slop-tics.md](/standards/prose/slop-tics.md).
