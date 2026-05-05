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

### In-memory specs written to disk
`req~serialize.disk-write~0`

Description:
The serializer `SHALL` write a list of in-memory SpecItems to a
caller-specified path as a markdown file.

Rationale:
Round-trip workflows — discover, parse, modify, save — need a
disk-write operation symmetric to deserialize's `parse(path)`. A
module-level entry point that matches Python stdlib idiom
(`json.dump`, `pickle.dump`) saves every consumer from composing
primitives.

Covers:
- feat~serialize~0

Needs:
- dsn
