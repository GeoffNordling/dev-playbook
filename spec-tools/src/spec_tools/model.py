from dataclasses import dataclass

import networkx


@dataclass(frozen=True)
class ItemId:
    artifact_type: str
    name: str
    revision: int

    def __post_init__(self) -> None:
        if self.revision < 0:
            raise ValueError(
                f"revision must be a non-negative integer, got {self.revision}"
            )


@dataclass
class SpecItem:
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
    def __init__(self, items: list[SpecItem]) -> None:
        self._items = list(items)

    def find(self, id: ItemId) -> SpecItem | None:
        for item in self._items:
            if item.id == id:
                return item
        return None

    def upstream(self, id: ItemId) -> list[SpecItem]:
        item = self.find(id)
        if item is None:
            return []
        return [
            covered
            for covered_id in item.covers
            if (covered := self.find(covered_id)) is not None
        ]

    def downstream(self, id: ItemId) -> list[SpecItem]:
        return [item for item in self._items if id in item.covers]

    def as_digraph(self) -> networkx.DiGraph:
        digraph = networkx.DiGraph()
        for item in self._items:
            digraph.add_node(item.id)
        for item in self._items:
            for upstream_id in item.covers:
                digraph.add_edge(item.id, upstream_id)
        return digraph
