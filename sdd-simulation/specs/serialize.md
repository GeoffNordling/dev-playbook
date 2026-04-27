# Serialize

Simulated specs for the `spec-tools` serialize module. See
[../README.md](../README.md) for the simulation's purpose.

## Feature

### Spec Serialization
`feat~serialize~0`

Description:
The serializer `SHALL` write an in-memory spec model to disk as
Markdown that conforms to the workspace spec standard.

Rationale:
Programmatic edits are only useful if they survive a write. The
serializer is the guarantee that any in-memory change can be
persisted as a conformant spec file.

Needs:
- req

## Requirements

### Output conforms to the spec standard
`req~serialize.conformance~0`

Description:
When the serializer writes a spec item, the output `SHALL` conform
to the workspace spec standard.

Rationale:
Non-conformant output breaks the next parse and is useless to
humans reading specs directly.

Covers:
- feat~serialize~0

Needs:
- dsn

