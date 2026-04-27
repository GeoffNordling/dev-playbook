# Model

Simulated specs for the `spec-tools` model module. See
[../README.md](../README.md) for the simulation's purpose.

## Feature

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

## Requirements

### Programmatic construction and navigation
`req~model.navigation~0`

Description:
The model `SHALL` allow callers to construct items in memory,
locate items by ID, and traverse coverage relationships
(`Covers:`, `Needs:`, `Depends:`) without requiring access to the
on-disk spec files.

Rationale:
Analysis and edit tools must operate on a self-contained in-memory
graph; round-trips through disk would couple every operation to
parse and render performance.

Covers:
- feat~model~0

Needs:
- dsn

## Design

### SpecItem shape
`dsn~model.spec-item~0`

Description:
The model `SHALL` represent each spec item as a single `SpecItem`
instance with the following typed fields:

- heading: str
- id: ItemId
- description: str
- rationale: str | None
- comment: str | None
- covers: list[ItemId]
- depends: list[ItemId]
- needs: list[str]
- tags: list[str]
- interface: list[str]
- agent_review: list[str]

Field names mirror the keyword names defined in the spec standard.

Rationale:
Typed accessors give every downstream consumer static help and a
stable contract. A single flat `SpecItem` keeps the model uniform
— consumers iterate items without type-switching.

Covers:
- req~deserialize.fidelity~0

Depends:
- dsn~model.item-id~0

Needs:
- utest

Interface: model.SpecItem(heading: str, id: model.ItemId, description: str, rationale: str | None, comment: str | None, covers: list[model.ItemId], depends: list[model.ItemId], needs: list[str], tags: list[str], interface: list[str], agent_review: list[str]) -> None

### ItemId triple
`dsn~model.item-id~0`

Description:
The model `SHALL` represent each spec-item identifier as an
`ItemId` triple of artifact type, name, and revision, with the
revision a non-negative integer.

Rationale:
Structured access to id components lets downstream consumers
filter, group, and compare items by type or name without parsing
the id string. The triple mirrors the standard's defined id form.

Covers:
- req~deserialize.fidelity~0

Needs:
- utest

Interface: model.ItemId(artifact_type: str, name: str, revision: int) -> None

### Artifact type lives only in id
`dsn~model.artifact-type-source~0`

Description:
The model `SHALL NOT` carry an `artifact_type` accessor on
`SpecItem` separate from the one reachable via
`SpecItem.id.artifact_type`. The id triple `SHALL` be the sole
in-memory source of an item's artifact type.

Rationale:
A duplicate `artifact_type` field on `SpecItem` could drift from
the id during construction or mutation. Pinning the id as the
single source of truth removes that class of bug entirely.

Covers:
- req~deserialize.fidelity~0

Depends:
- dsn~model.spec-item~0
- dsn~model.item-id~0

Needs:
- utest
