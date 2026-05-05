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
`SpecItem.__init__` `SHALL` raise `ValueError` if `heading` or
`description` is empty, if `rationale` or `comment` is the empty
string rather than `None`, or if any entry in `needs`, `tags`,
`interface`, or `agent_review` is the empty string. These cases
would otherwise yield non-conformant render output, since the
deserializer rejects empty headings and empty keyword bodies.

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
`ItemId` triple of artifact type, name, and revision.
`ItemId.__init__` `SHALL` raise `ValueError` on any violation of
the ID-form rules in §3 of the workspace spec standard:
`artifact_type` must be one of `feat`, `req`, `dsn`, `utest`, or
`itest` (per §4); `name` must start with a letter and contain
only letters, digits, `.`, `_`, or `-`, with no consecutive dots
(per §3.2); `revision` must be a non-negative integer (per §3.3).

Rationale:
Structured access to id components lets downstream consumers
filter, group, and compare items by type or name without parsing
the id string. The triple mirrors the standard's defined id form.
Construction-time validation prevents callers from building
ItemIds that would render to non-conformant text and fail to
parse.

Covers:
- req~deserialize.fidelity~0

Needs:
- utest

Interface: model.ItemId(artifact_type: str, name: str, revision: int) -> None

AgentReview: `ItemId.__post_init__` enforces the ID-form rules in §3 of sdd-standards/spec-standard.md — artifact_type whitelist from §4, name charset and lead-character rule from §3.2, no consecutive dots in name from §3.2, non-negative integer revision from §3.3.

### Spec graph
`dsn~model.graph~0`

Description:
The model `SHALL` expose a `SpecGraph` type that wraps a list of
SpecItems and exposes ID lookup and coverage-graph traversal.
`upstream(id)` returns the items that the given item covers (the
items its `Covers:` line names); `downstream(id)` returns the
items that cover the given item. `as_digraph()` returns a
`networkx.DiGraph` view of the coverage relationships, with nodes
keyed by `ItemId` and edges directed from each downstream item to
the upstream items it covers.
If the input list contains two items with the same `ItemId`, an
item whose `Covers:` references an `ItemId` not present in the
list, or a coverage cycle, `SpecGraph.__init__` `SHALL` raise
`ValueError`.

Rationale:
A typed graph type centralizes the lookup and traversal logic that
analysis tools would otherwise duplicate. Wrapping a caller-supplied
list rather than owning storage lets callers choose when to pay for
indexing — modules that only need to iterate items keep working
with plain lists. Exposing the coverage relationships as a
`networkx.DiGraph` lets analysis tools run standard graph
algorithms (shortest paths, cycle detection, topological sort)
directly; algorithm logic lives in the analysis tools that need it,
keeping `SpecGraph` focused on storage and lookup.

Covers:
- req~model.navigation~0

Depends:
- dsn~model.spec-item~0
- dsn~model.item-id~0

Needs:
- utest

Interface: model.SpecGraph(items: list[model.SpecItem]) -> None
Interface: model.SpecGraph.find(self, id: model.ItemId) -> model.SpecItem | None
Interface: model.SpecGraph.upstream(self, id: model.ItemId) -> list[model.SpecItem]
Interface: model.SpecGraph.downstream(self, id: model.ItemId) -> list[model.SpecItem]
Interface: model.SpecGraph.as_digraph(self) -> networkx.DiGraph
