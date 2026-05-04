# Deserialize

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
