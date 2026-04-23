# Design Layer

This file is about the *semantics* of design items (`dsn`) — what a design
commitment is and which dimensions it can commit across. The mechanical
rules for organizing and verifying `dsn` items (section headers, the
three verification fields) live in [extensions.md](extensions.md).

Obligation verbs in this document follow [rfc2119.md](rfc2119.md).

## Purpose

Functional requirements describe behavior; design items record the decisions
that shape the code fulfilling that behavior. A `dsn` is written after the
behavior is settled.

A `dsn` records a **commitment** — a decision whose chosen option some other
part of the system will rely on: callers, tests, downstream code. Decisions
inside a module's private boundary (internal helpers, file layout, local
control flow) are not commitments and belong to the implementation phase, not
to the design item.

Two tests for whether something is a commitment:

- **Would another part of the system change if the decision flipped?** If
  yes, it is a commitment. If it is purely internal to one module, it is not.
- **Could a reviewer or test observe the decision?** If the decision is
  visible at a public boundary — signature, data schema, error semantic,
  ordering of effects — it is a commitment.

## Decision dimensions

A `dsn` commits decisions across one or more of four dimensions. Every `dsn`
`SHALL` commit to at least one dimension; a `dsn` with no dimensional
commitment is not a design decision — it is narrative.

### Data

The fundamental abstractions the system is built around. Entities, fields,
relationships, containment, ownership. These abstractions exist in both the
design spec and the implementation code; they are the nouns the system
manipulates.

Examples: the `Session` entity and its owned `Event` children; the
`ParserConfig` record; the distinction between a raw `Frame` and a
derived `Segment`.

### API Shape

Signatures of public callables, classes, and methods. What callers name,
invoke, and receive.

Examples: a function returning `list[Event]` vs. `Iterable[Event]`; a class
exposing `parse(path)` vs. a free function `parse(path, config)`; raising
`ValidationError` vs. returning `Result[Session, Error]`.

Error semantics (which exceptions are raised, under what conditions) fold
into API Shape — raises are part of the contract.

Module layout (where a symbol lives — `myapp.parser.SessionParser` vs.
`myapp.session.Parser`) folds into API Shape; the fully-qualified symbol
path encodes the placement.

Data-structure choice folds into API Shape when the signature pins it (e.g.,
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

Two designs with identical Data, API Shape, and Algorithms can still commit
to different Compositions and produce different integration-test outcomes.
Composition is a first-class dimension, not a byproduct of the others.

## Dimensions may be null at the project level

A pure-data library may have no Algorithms or Composition. A single-function
tool may have no Composition. A CLI wrapper may have thin Algorithms. That
is fine at the project level — the dimension table covers what a given
project happens to need.

Every individual `dsn`, however, `SHALL` commit to at least one dimension.
Within the file organization rules (see
[extensions.md](extensions.md#dimension-section-organization)), each `dsn`
is placed under the single dimension it primarily commits to; if it
genuinely spans multiple dimensions, it is a candidate for being split.

## Related rules in extensions.md

These mechanical rules apply to every `dsn` but are not themselves
design-semantic decisions; they live with our other workspace-level
conventions:

- [Dimension section organization](extensions.md#dimension-section-organization)
  — the four `##` headers required in every `dsn` file.
- [Verification coverage](extensions.md#verification-coverage--extension) —
  every `dsn` `SHALL` carry at least one of `Needs:`, `Interface:`, or
  `AgentReview:`.
- [`Interface:` keyword](extensions.md#extension-keyword-interface) —
  structural commitment format.
- [`AgentReview:` keyword](extensions.md#extension-keyword-agentreview) —
  non-testable commitment format.
