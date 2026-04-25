# Design Layer

## Purpose

Functional requirements describe what the system does, not how. The space
of correct implementations of any behavioral requirement is enormous — many
entity shapes, many public surfaces, many algorithms, many sequencings of
operations all satisfy the same requirement.

An agent writing code directly from a functional requirement picks
somewhere in that space. The pick is often not where a human with taste,
project context, and vision would have landed. Code that meets the
requirement but takes the wrong shape — wrong abstractions, wrong API,
wrong ordering — is technically correct and practically wrong.

The design layer is where the human narrows the space. A `dsn` encodes
intuition the agent does not have on its own — what reads well in this
codebase, what the project is converging toward, what trade-off this team
prefers, what other parts of the system already do. The agent reads the
`dsn` collection before writing code and treats each item as a constraint
on the implementation.

A `dsn` lives at the **public boundary** — what callers see, what
downstream code reads, what subsequent stages depend on. Decisions that
live entirely inside a module (internal helpers, local data structures,
file layout, control flow) belong to the implementation phase and stay
with the agent.

## Decision dimensions

### Data

The fundamental abstractions the system is built around. Entities, fields,
relationships, containment, ownership. These abstractions exist in both the
design spec and the implementation code; they are the nouns the system
manipulates.

Examples: the `Session` entity and its owned `Event` children; the
`ParserConfig` record; the distinction between a raw `Frame` and a
derived `Segment`.

### API-Shape

Signatures of public callables, classes, and methods. What callers name,
invoke, and receive.

Examples: a function returning `list[Event]` vs. `Iterable[Event]`; a class
exposing `parse(path)` vs. a free function `parse(path, config)`; raising
`ValidationError` vs. returning `Result[Session, Error]`.

Error semantics (which exceptions are raised, under what conditions) fold
into API-Shape — raises are part of the contract.

Module layout (where a symbol lives — `myapp.parser.SessionParser` vs.
`myapp.session.Parser`) folds into API-Shape; the fully-qualified symbol
path encodes the placement.

Data-structure choice folds into API-Shape when the signature pins it (e.g.,
`-> list[Event]`); when the signature abstracts it (e.g.,
`-> Iterable[Event]`), the structure choice drops below the public
boundary and belongs to the implementation phase.

### Algorithms

The exact operations that produce outputs from inputs. Sum, fold, filter,
derive. A system typically commits several algorithms — each one a stepwise
operation precise enough that two independent implementations would agree on
inputs and outputs.

Examples: "segment durations are summed to compute session length"; "the
validator folds over frames from earliest timestamp to latest";
"anomalies are derived as frames whose deviation exceeds three standard
deviations."

Failure paths (what happens when input is malformed) fold into Algorithms.

### Composition

How operations combine. Sequencing, dependency, data flow, fan-out, fan-in.

Examples: "parse, then validate, then persist — in that order"; "parsing
and checksumming run in parallel and their results are joined";
"validation errors short-circuit later stages."

Two designs with identical Data, API-Shape, and Algorithms can still commit
to different Compositions and produce different integration-test outcomes.
Composition is a first-class dimension, not a byproduct of the others.

## Using the dimensions

When sitting down to write a `dsn` collection, walk through each axis
in turn: what entities and shapes does this part of the system commit
to (`Data`)? what surfaces do callers see (`API-Shape`)? what
operations produce outputs from inputs (`Algorithms`)? how do those
operations combine (`Composition`)? Pivoting attention to one axis at
a time keeps the design from drifting into prose-shaped narrative.

Not every project commits on every axis. A pure-data library may have
no `Algorithms` or `Composition`. A single-function tool may have no
`Composition`. A CLI wrapper may have thin `Algorithms`. The framework
is a checklist, not an obligation.

`API-Shape` commitments often surface as `Interface:` declarations on
the same `dsn` — a fully-qualified, annotated signature is the
structural codification of an API-Shape decision. The two are not
parallel commitments; the `Interface:` field is how an API-Shape
decision is expressed when the human wants the agent bound to a
specific signature.

## Related keyword and chain rules

Mechanical rules that apply to every `dsn` but are keyword-level (not
design-semantic) live in [spec-standard.md](spec-standard.md):

- [Verification termination](spec-standard.md#54-verification-termination)
  — chains `SHOULD` terminate in a `utest`, an `itest`, or any item
  carrying `AgentReview:`.
- [`Interface:` keyword](spec-standard.md#68-interface) — design-phase
  structural commitment format.
- [`AgentReview:` keyword](spec-standard.md#69-agentreview) —
  non-testable verification format.
