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

`line` is 1-indexed against the source file. `rule_violated` is one
of the following stable string ids; callers dispatch on it to route
or format errors by category:

- `id-syntax` — the ID triple is missing or malformed (e.g., wrong
  number of tilde-separated parts, whitespace in `name`, negative
  revision).
- `missing-keyword` — a required keyword is absent (e.g., an item
  with a heading and ID but no `Description:`).
- `unknown-keyword` — a `Foo:` line names a keyword not defined by
  §6 of the workspace spec standard.
- `duplicate-keyword` — a single-occurrence keyword appears more
  than once within one item (e.g., two `Description:` blocks).
- `malformed-body` — a keyword's content does not match the form
  required for that keyword (e.g., a `Covers:` line followed by
  non-bullet content, an empty `Tags:` line).

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

AgentReview: The deserializer's `rule_violated` taxonomy — recognized-keyword set, required-keyword set, and per-keyword body forms — matches the keyword definitions in §6 of sdd-standards/spec-standard.md.

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
