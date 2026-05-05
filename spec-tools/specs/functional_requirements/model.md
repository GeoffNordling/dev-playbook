### In-memory Spec Model
`feat~model~0`

Description:
The model `SHALL` provide typed Python representations of spec
artifacts that callers can query, traverse, and modify in memory.

Rationale:
A typed model is the lingua franca for parse, render, and analysis
code. Without it, each module would invent its own ad-hoc dict shape
and round-tripping would be impossible.

Needs:
- req

### In-memory spec collection
`req~model.navigation~0`

Description:
The model `SHALL` provide an in-memory container that holds a set
of SpecItems and supports lookup by ID and traversal of coverage
relationships (`Covers:`, `Needs:`, `Depends:`) independent of the
on-disk spec files.

Rationale:
Analysis and edit tools must operate on a self-contained in-memory
graph; routing every query through disk would couple each operation
to parse and render performance.

Covers:
- feat~model~0

Needs:
- dsn

### Round-trip closure
`req~model.round-trip~0`

Description:
The model `SHALL` survive round-trip in both directions:
- A `SpecItem` serialized to text and deserialized `SHALL` equal the
  original `SpecItem`.
- Canonically-formatted spec text deserialized to `SpecItem`s and
  re-serialized `SHALL` produce the original text byte-for-byte.
"Canonically-formatted" means text produced by the serializer, or
hand-authored text that already conforms to the canonical form.

Rationale:
A model that cannot survive round-trip would silently lose
information when callers persist their changes. Closure under
round-trip is what makes the model usable as a programmable
representation of specs.

Covers:
- feat~model~0

Needs:
- itest
