# Deserialize

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
