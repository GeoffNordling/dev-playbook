"""In-memory model of SDD spec artifacts."""

import re
from dataclasses import dataclass

import networkx

_ARTIFACT_TYPES = frozenset({"feat", "req", "dsn", "utest", "itest"})
_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class ItemId:
    """Spec-item identifier: artifact type, name, and revision."""

    artifact_type: str
    name: str
    revision: int

    def __post_init__(self) -> None:
        """Enforce the ID-form rules from §3 of the workspace spec standard."""
        if self.artifact_type not in _ARTIFACT_TYPES:
            raise ValueError(
                f"artifact_type must be one of {sorted(_ARTIFACT_TYPES)}, "
                f"got {self.artifact_type!r}"
            )
        if not _NAME_PATTERN.match(self.name):
            raise ValueError(
                "name must start with a letter and contain only "
                f"letters, digits, '.', '_', or '-', got {self.name!r}"
            )
        if ".." in self.name:
            raise ValueError(
                f"name must not contain consecutive dots, got {self.name!r}"
            )
        if self.revision < 0:
            raise ValueError(
                f"revision must be a non-negative integer, got {self.revision}"
            )


@dataclass
class SpecItem:
    """A single SDD spec item with all standard-defined fields."""

    heading: str
    id: ItemId
    description: str
    rationale: str | None
    comment: str | None
    covers: list[ItemId]
    depends: list[ItemId]
    needs: list[str]
    tags: list[str]
    interface: list[str]
    agent_review: list[str]

    def __post_init__(self) -> None:
        """Reject field values that would yield non-conformant render output."""
        # `not s` on a `str` field rejects only "" (the sole falsy str value).
        if not self.heading:
            raise ValueError("heading must be a non-empty string")
        if not self.description:
            raise ValueError("description must be a non-empty string")
        # `== ""` on `str | None` fields rejects "" while leaving None
        # untouched; `not s` would wrongly reject None too.
        if self.rationale == "":
            raise ValueError("rationale must be None rather than the empty string")
        if self.comment == "":
            raise ValueError("comment must be None rather than the empty string")
        for field_name in ("needs", "tags", "interface", "agent_review"):
            if any(not entry for entry in getattr(self, field_name)):
                raise ValueError(f"{field_name} must not contain empty-string entries")


class SpecGraph:
    """Indexed view of a list of SpecItems with coverage-graph traversal."""

    def __init__(self, items: list[SpecItem]) -> None:
        """Build the ID index from `items`.

        Raises ValueError on duplicate ids, a `Covers:` reference to an id
        absent from the list, or a coverage cycle.
        """
        index: dict[ItemId, SpecItem] = {}
        for item in items:
            if item.id in index:
                raise ValueError(f"duplicate ItemId in items: {item.id}")
            index[item.id] = item
        for item in items:
            for upstream_id in item.covers:
                if upstream_id not in index:
                    raise ValueError(
                        f"item {item.id} covers {upstream_id}, "
                        "which is not in the graph"
                    )
        digraph = networkx.DiGraph()
        for item in items:
            digraph.add_node(item.id)
            for upstream_id in item.covers:
                digraph.add_edge(item.id, upstream_id)
        try:
            cycle = networkx.find_cycle(digraph)
        except networkx.NetworkXNoCycle:
            cycle = None
        if cycle is not None:
            raise ValueError(f"coverage cycle: {cycle}")
        self._items = index
        self._digraph = digraph

    def find(self, id: ItemId) -> SpecItem | None:
        """Return the item with `id`, or None if absent."""
        return self._items.get(id)

    def upstream(self, id: ItemId) -> list[SpecItem]:
        """Return the items that the item with `id` covers."""
        item = self._items[id]
        return [self._items[c] for c in item.covers]

    def downstream(self, id: ItemId) -> list[SpecItem]:
        """Return the items that cover the item with `id`."""
        return [item for item in self._items.values() if id in item.covers]

    def as_digraph(self) -> networkx.DiGraph:
        """Return a networkx.DiGraph of the coverage relationships.

        Nodes are keyed by ItemId; edges run from each downstream item to the
        upstream items it covers.
        """
        return self._digraph.copy()
