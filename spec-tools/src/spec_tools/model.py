"""In-memory model of SDD spec artifacts."""

from dataclasses import dataclass

import networkx


@dataclass(frozen=True)
class ItemId:
    """Spec-item identifier: artifact type, name, and revision."""

    artifact_type: str
    name: str
    revision: int

    def __post_init__(self) -> None:
        """Reject negative revisions."""
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


class SpecGraph:
    """Indexed view of a list of SpecItems with coverage-graph traversal."""

    def __init__(self, items: list[SpecItem]) -> None:
        """Build the ID index from `items`."""
        self._items: dict[ItemId, SpecItem] = {item.id: item for item in items}

    def find(self, id: ItemId) -> SpecItem | None:
        """Return the item with `id`, or None if absent."""
        return self._items.get(id)

    def upstream(self, id: ItemId) -> list[SpecItem]:
        """Return the items that the item with `id` covers.

        Raises KeyError if `id` or any of its covers is absent from the graph.
        """
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
        digraph = networkx.DiGraph()
        for item in self._items.values():
            digraph.add_node(item.id)
            for upstream_id in item.covers:
                digraph.add_edge(item.id, upstream_id)
        return digraph
