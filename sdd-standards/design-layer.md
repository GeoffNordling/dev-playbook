# Design Layer

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this document are to be interpreted as described in RFC 2119, following the vocabulary conventions in [writing.md](writing.md).

## Purpose

Functional requirements describe behavior; design items (`dsn`) record the decisions that shape the code fulfilling that behavior. A `dsn` is written after the behavior is settled.

A `dsn` records a **commitment** — a decision whose chosen option some other part of the system will rely on: callers, tests, downstream code. Decisions inside a module's private boundary (internal helpers, file layout, local control flow) are not commitments and belong to the green agent.

## Decision Dimensions

A `dsn` commits decisions across one or more of four dimensions:

1. **Data** — the fundamental abstractions the system is built around. Entities, fields, relationships, containment, ownership. These abstractions exist in both the design spec and the implementation code; they are the nouns the system manipulates.
2. **API Shape** — signatures of public callables, classes, and methods. What callers name, invoke, and receive.
3. **Algorithms** — the exact operations that produce outputs from inputs. Sum, fold, filter, derive. A system typically commits several.
4. **Composition** — how operations combine. Sequencing, dependency, data flow, fan-out, fan-in.

At the project level, any dimension `MAY` be null: a pure-data library may have no Algorithms or Composition; a single-function tool may have no Composition; a CLI wrapper may have thin Algorithms. Every individual `dsn`, however, `SHALL` commit to at least one dimension.

Error semantics fold into API Shape (raises are part of the contract) and Algorithms (failure paths). Data-structure choice folds into API Shape when the signature pins it (e.g., `-> list[Event]`), or into the green agent's territory when the signature abstracts it (e.g., `-> Iterable[Event]`).

## Dimension Section Organization

Every `dsn` spec file `SHALL` organize its items under four markdown section headers, one per dimension, in this order:

    ## Data
    ## API Shape
    ## Algorithms
    ## Composition

Every `dsn` item `SHALL` appear under exactly one of these four headers. Items that float above or between section headers are errors.

A file where a dimension has no commitments `SHALL` still include the header with an empty section. The empty header is the explicit signal "considered, nothing to commit here." A missing header is not equivalent to an empty section; the header makes the absence deliberate.

## Verification Fields

[overview.md](overview.md#coverage-chain) establishes the general rule that every requirement ties off with a verification mechanism. For `dsn` items, this rule takes a specialized form: every `dsn` `SHALL` carry at least one of three verification fields. A single `dsn` `MAY` combine any subset — one design decision often commits multiple aspects simultaneously, and forcing separate items per field would inflate the `dsn` count and artificially split closely related commitments.

| Field | Origin | Purpose | Verified by |
|---|---|---|---|
| `Needs: utest, itest` | OFT standard | Behavioral commitment | pytest run |
| `Interface:` | Workspace extension | Structural contract | Interface validator at pytest collection time |
| `AgentReview:` | Workspace extension | Non-test commitment | `sdd-review` skill on invocation |

Format details for `Interface:` and `AgentReview:` live in [writing.md](writing.md#interface-declarations) alongside the other spec keywords.

**Example: one `dsn`, multiple verification fields.**

    Needs: utest
    Interface: myapp.parser.Parser.parse(path: pathlib.Path) -> myapp.session.Session
    AgentReview: Log output from Parser.parse follows the human-readable format specified in docs/log-format.md.

**Example: non-testable commitment.** Some requirements cannot be deterministically tested — e.g., "the agent `SHALL NOT` attempt polite conversation for no reason." The `dsn` terminates its chain with `AgentReview:` alone:

    dsn~agent.no-polite-conversation~1
        Enforcement via system prompt directive.
        AgentReview: The agent's system prompt at src/prompts/agent.md should contain
                     a directive discouraging filler or polite conversation.

No `Needs:`, no `Interface:` — the review skill is what verifies the commitment.
