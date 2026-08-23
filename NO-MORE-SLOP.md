---
type: General-Sheet
title: No More Slop
description: The branch plan — goal, principles, the two tracks, and the current step
---

# No More Slop

The plan and state of the `no-more-slop` branch, deleted when the branch
merges. Material drains out of this file as it settles into the appropriate
long-term location.

This file is speculative, and the doc conventions' declarative voice does
not apply to it: a guess is written as a guess, an open question sits
inline next to its topic, and a sentence is settled only when it says so.

## Goal

The user can understand this repository without reading all of it. Today
they cannot: the repo sits in the slop trench — nominal ownership of a
system whose details have outpaced inspection. The
[System Legibility](/standards/legibility.md) card states the goal. This
branch works the documentation track; the code track waits.

What slop is precisely is still being worked out. So far, it breaks into:

- **Low quality** — divergence from the user's latent intent for action and
  preference for style. For the AI this operationalizes as divergence from
  the stated standards, which are themselves ill-defined in places.
- **Not understood** — contains critical information at the CLOA, but the
  user cannot or will not read it, whatever its quality. Note: this does
  not include critical information below the CLOA; the user never needs to
  understand every line of code, for example.

## Levels

Understanding happens at multiple levels, for code and documentation alike:

- **One file, opened.** The user zooms in on a single file and can read it.
  What serves this level changes the file itself — wording, shape, length —
  never its meaning.
- **Above the file.** The user cannot read every file, so understanding at
  the higher levels has to come some other way. What those levels are and
  what serves each one is not yet worked out. Code has established tools
  up here; documentation is the open question.

Across the levels runs an abstraction/detail axis with a latent optimal
point neither party knows a priori. Too low — too much detail — and the
user wastes time or stops paying attention; too high and the user is
fooled into thinking they understand, but really doesn't; both ends
produce slop. Pre-AI interfaces
were forcing functions: pandas and git impose their abstractions, and a
wrong mental model does not survive contact with them. Natural language
imposes no level at all and never pushes back, so the operating point
drifts unless the CLOA is engineered deliberately.

## Principles

These apply to both tracks.

- **The CLOA** (Correct Level of Abstraction) — the level of abstraction
  where the AI and the user communicate in the exact same terminology.
  `CONTEXT.md` is the anchor: the user understands it 100%, the AI uses
  its terms in all communication, and a missing term is added on the spot
  and approved by the user. Zero vibe coding in that file. The terms form
  a **vocabulary API** — an API between the user and the AI, designed the
  way a library designs its public surface, with the internals below it
  AI-owned. Escalation discipline is its behavioral half: the AI raises
  questions in vocabulary terms, proposing a new term when one is
  missing. A default, toggleable — some modes of talk need to leave the
  vocabulary. The bets per track: `CONTEXT.md` carries the CLOA for
  documentation and communication, and the acceptance tier (code track)
  carries it for code.
- **Deterministic backpressure preferred over stochastic functions.**
  Stochastic functions — prompts, models, agents — are powerful but
  expensive. Deterministic backpressure — detectors, linters, gates, and
  plain contact with reality — is inviolable and efficient. Prefer it
  wherever it can reach, but admit that it can't do everything. Keep
  agentic backpressure tools simple and loop friendly: simple status codes
  can be better than detailed reports.
- **Move slowly in decision space.** Past failures were planning too much
  and leaping too far. Small iterative steps, with backpressure from
  reality at each one; what stays small is how much is committed before
  reality answers back.
- **Constrain to optimize understanding.** A constraint on form seems to
  earn its keep several ways: it amortizes reading (learn the shape once,
  read every instance fast), it makes location and absence meaningful (a
  fact has one place it can live), and it turns a taste question into a
  lintable rule.
- **Use what exists.** Before building anything, check what the repo has
  and prefer improving or modifying in place.

## The pandas standard

The target state, named for where the user lived it: years of pandas
fluency — which objects exist, which methods fit which task, how they
compose — without ever reading inside a pandas method. The internals
belonged to the pandas maintainers; here they belong to the AI. The
fluency came from being the caller: the user learned pandas, git, and the
software factory by operating them daily.

The [Standard](/standards/standard/format.md) card system is the in-repo
exemplar: the user holds primitives — define, audit, enforce, adopt — and
predicts every card's behavior without having memorized the rule prose, the
scripts, or the judges.

## Documentation track — active

**Completed**

- **Deslop rewrite.** Every prose document rewritten in place against
  [Slop Tics](/standards/prose/slop-tics.md). Productionized as the
  `/document-deslop` skill, which the user invokes manually.
- **Documentation defines behaviors; skills and agents never define one.**
  Written into the knowledge-organization standard as
  [file-roles.md](/standards/knowledge-organization/file-roles.md), the
  renamed and rebuilt `bundle.md`. Two axes — role (concept document /
  harness-owned file) and content (behavior / procedure) — and the rule is
  the grid's one empty cell: a rule of the system is never written only in
  a skill body or an agent definition.

  Nothing checks it. No detector can, and the card carries no judgment for
  it, so conformance across the existing skills and agents is unmeasured.
  Two violations are confirmed by reading: `commit` and `doc-format` both
  define behaviors that have no document to point at, so each needs a
  document written before the skill can shrink.

**Raw ideas, none designed**

- **Markdown complexity detectors.** No specifics yet on how to measure the
  complexity of a document, but surely something is measurable — the goal
  is a file the user can read without checking out on opening.
- **Doc linters, re-aimed.** The existing linters are pedantic — they check
  that certain headings are present. Decide what is actually worth linting
  for and design toward that.
- **Reference chains.** Skills as signatures, OKF traces, and the OKF
  graph converged into one object — a doc unit's reference chain, declared
  rather than discovered, lintable. Moved to
  [the abstraction loop](/ABSTRACTION-LOOP.md) as its first target.
- **Deslop regression gate.** Something must keep a rewritten document from
  sliding back into slop. Deterministic rules cannot judge prose quality;
  the judgments machinery may fit here.
- **Vocabulary change discipline.** A process that forces a conscientious
  decision on every term added to or removed from `CONTEXT.md`. Without one,
  terms accrete unexamined.
- **CLOA change discipline.** A process that forces a conscientious
  decision on every term used within a CLOA communication. Without one,
  vocabulary changes willy-nilly.
The core problem of this track: documentation needs far more reading by the
user than code does. Code is deterministic and can be pinned down by tools;
documentation can only be taken so far by them, so something has to keep it
a pleasure to read.

## Code track — parked

**Adopt**

- **ruff `C901`** — over-complex functions fail lint; no new dependency.
- **mypy, tightened** — exact flags undecided, not necessarily full
  `--strict`.
- **import-linter** — a declared contract over module dependencies
  ("`config` must not import `cli`"), failing CI when an import crosses a
  forbidden line.
- **Rendered API surface** — public signatures plus docstrings, the
  read-a-module-at-a-glance view. `griffe-outline` exists; evaluate it
  before reaching for mkdocstrings or pdoc.
- **`tests/acceptance/`** — see the tiers below.

**Undecided**

- **Hypothesis** — one readable property can replace fifty example tests.
- **Gherkin / BDD** — the most readable acceptance tests; worth
  remembering, not worth shoehorning in.
- **Mermaid sequence diagrams** — cheap to generate when tracing one
  operation.
- **coverage.py** — as a detector, not a percentage: uncovered code is code
  nothing forces to be correct.

**Rejected**

- **radon / xenon** — `C901` covers this in a running tool.
- **vulture** — dead code is not a priority.
- **pyright** — one type checker is enough.

**Notes**

- **Two testing tiers.** The unread tier: the existing thousand-odd unit
  tests, machine-written, judged by passing. The acceptance tier:
  `tests/acceptance/`, small and capped, written in `CONTEXT.md`
  terminology, one test per behavior the user could state in a sentence,
  read 100%. The deterministic gate that keeps the acceptance tier from
  bloating is undesigned — a size cap, naming rules, or a rule that every
  public module has at least one.
- **Gray modules.** If the user understands a module's tests and the tests
  pass, the user has an approximate understanding of the code beneath.
- **Import graph and call graph.** The import graph (modules, dozens of
  nodes) sits at the CLOA and import-linter can enforce rules on it; the
  call graph (functions, hundreds of nodes) sits below it, for tracing one
  operation. They disagree at type-only imports, callbacks and plugins, and
  `__init__.py` re-export hubs.
- **Docstrings.** The ruff `D` gate is live (pep257, `D401` off, `tests/`
  exempt) in pre-commit and `make check`. `D` checks presence and format
  only; docstring quality stays stochastic with the review agents, which is
  the right assignment.

## New terms

Candidates to document somewhere:

- CLOA (Correct Level of Abstraction)
- unread tier, acceptance tier
- gray module
- slop
- constrain to optimize understanding
- the pandas standard

## Now

Run [the abstraction loop](/ABSTRACTION-LOOP.md) — the offshoot where the
CLOA abstractions are constructed one change at a time. First target: one
skill chain. Its results merge back here or the offshoot terminates.