# Serialize

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

## Design

### Render to conformant markdown
`dsn~serialize.render~0`

Description:
The serializer's public `render` function `SHALL` produce markdown
that conforms to the workspace spec standard, for any well-formed
list of SpecItems. Conformance holds by construction at output
time.

Rationale:
A pure list-to-string transformation isolates the conformance
concern from disk I/O. Conformance is established by render's
logic at construction time — every output it produces is
standard-conformant by definition.

Covers:
- req~serialize.conformance~0

Depends:
- dsn~model.spec-item~0

Needs:
- utest

Interface: serialize.render(items: list[model.SpecItem]) -> str

### Write rendered output to disk
`dsn~serialize.write~0`

Description:
The serializer's public `write` function `SHALL` persist a
rendered spec file to a caller-specified path. Its behavior
`SHALL` be equivalent to `path.write_text(render(items))`.

Rationale:
A module-level write function is the natural Python stdlib idiom
(`json.dump`, `pickle.dump`, `yaml.dump`). Exposing it gives
callers one obvious entry point for the common case of writing a
complete spec file, while render remains the testable
transformation core.

Covers:
- req~serialize.disk-write~0

Depends:
- dsn~serialize.render~0

Needs:
- utest

Interface: serialize.write(items: list[model.SpecItem], path: pathlib.Path) -> None
