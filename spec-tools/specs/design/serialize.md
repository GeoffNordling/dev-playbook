### Render to conformant markdown
`dsn~serialize.render~0`

Description:
The serializer's public `render` function `SHALL` produce markdown
that conforms to the workspace spec standard for any list of
SpecItem instances. Within each item, keywords appear in canonical
order: `Description:`, `Rationale:`, `Comment:`, `Covers:`,
`Depends:`, `Needs:`, `Tags:`, `Interface:`, `AgentReview:`.
Conformance holds by construction at output time.

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

AgentReview: The render function in `src/spec_tools/serialize.py` emits item sections in the canonical keyword order defined by §6 of `sdd-standards/spec-standard.md`, and the inline restatement of that order in this dsn's `Description:` matches §6 verbatim.

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
