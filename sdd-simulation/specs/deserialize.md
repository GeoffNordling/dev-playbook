# Deserialize

Simulated specs for the `spec-tools` deserialize module. See
[../README.md](../README.md) for the simulation's purpose.

## Feature

### Spec Deserialization
`feat~deserialize~0`

Description:
The deserializer `SHALL` read SDD spec files from disk and return
an in-memory representation faithful to the on-disk content as
defined by the workspace spec standard.

Rationale:
Every other spec-tools capability — analysis, programmatic edits,
re-serialization — assumes the in-memory model fully reflects the
source. Losses or distortions at this layer propagate silently into
every downstream operation.

Needs:
- req

## Requirements

### Lossless parse of standard-defined fields
`req~deserialize.fidelity~0`

Description:
When the deserializer parses a spec item, it `SHALL` preserve every
standard-defined field — heading, ID triple, all keyword fields — in
the in-memory model without loss, ordering changes, or semantic
normalization.

Rationale:
Round-tripping (deserialize → manipulate → serialize) must be
information-preserving on standard-defined content; anything dropped
at parse time is invisible to downstream code.

Covers:
- feat~deserialize~0

Needs:
- dsn

### Structured errors on malformed input
`req~deserialize.errors~0`

Description:
When a spec file does not conform to the workspace spec standard,
the deserializer `SHALL` fail fast and loud, surfacing a structured
error that identifies the file, the line, and the rule violated.

Rationale:
Silent drops produce an in-memory model that disagrees with the
source. Structured errors give callers (lint, IDEs, agent tooling) a
machine-readable handle to act on.

Covers:
- feat~deserialize~0

Needs:
- dsn

## Design

### Spec parse error
`dsn~deserialize.parse-error~0`

Description:
The deserializer `SHALL` raise a `SpecParseError` exception on each
violation of the workspace spec standard, with the following typed
fields:

- path: pathlib.Path
- line: int
- rule_violated: str
- message: str

`line` is 1-indexed against the source file. `rule_violated` is a
stable string id naming the standard rule (e.g., `"id-syntax"`,
`"missing-keyword"`); callers dispatch on this id to route or
format errors by category.

Rationale:
A typed exception with structured fields gives callers (lint, IDEs,
agent tooling) a machine-readable handle on the error. Stable rule
ids drive routing and category-level formatting; the free-form
`message` field carries the human-readable detail.

Covers:
- req~deserialize.errors~0

Needs:
- utest

Interface: deserialize.SpecParseError(path: pathlib.Path, line: int, rule_violated: str, message: str) -> None

### Public parse entry point
`dsn~deserialize.parse~0`

Description:
The deserializer `SHALL` expose a public `parse` function that
takes a spec file path and returns the SpecItems contained in that
file in source order. On the first violation of the workspace spec
standard, `parse` `SHALL` raise `SpecParseError` and abort.

Rationale:
A single public entry point gives every caller a uniform contract
for reading a spec file. Aborting on the first violation matches
the req-level "fail fast and loud" obligation: each call either
returns the full SpecItem list or raises a single error — a binary
contract for callers.

Covers:
- req~deserialize.fidelity~0
- req~deserialize.errors~0

Depends:
- dsn~model.spec-item~0
- dsn~deserialize.parse-error~0

Needs:
- utest

Interface: deserialize.parse(path: pathlib.Path) -> list[model.SpecItem]
