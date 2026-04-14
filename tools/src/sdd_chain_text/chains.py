"""Enumerate linear traceability chains from OFT coverage links.

Each SpecItem carries ``covers`` (upstream references) provided by OFT.
This module walks those links to produce maximal root-to-leaf paths,
excluding test layers (utest, itest).
"""

from __future__ import annotations

from .oft_xml import SpecItem

# Test artifact types excluded from chain output
_TEST_TYPES = frozenset({"utest", "itest", "stest"})


def build_chains(items: list[SpecItem]) -> list[list[SpecItem]]:
    """Build all linear traceability chains from the given spec items.

    Returns a list of chains, where each chain is a list of SpecItems
    ordered from root (upstream) to leaf (downstream). Branching produces
    separate chains; shared upstream items repeat across chains.

    Test layers (utest, itest) are excluded from chains.
    """
    # Index items by full_id
    by_id: dict[str, SpecItem] = {item.full_id: item for item in items}

    # Filter out test-type items
    non_test_items = [i for i in items if i.doctype not in _TEST_TYPES]

    # Build adjacency: upstream_id -> list of downstream items
    children: dict[str, list[SpecItem]] = {}
    has_parent: set[str] = set()

    for item in non_test_items:
        for covered_id in item.covers:
            if covered_id in by_id:
                children.setdefault(covered_id, []).append(item)
                has_parent.add(item.full_id)

    # Roots: non-test items that are not covered by anything upstream
    roots = [i for i in non_test_items if i.full_id not in has_parent]

    # DFS to enumerate all root-to-leaf paths
    chains: list[list[SpecItem]] = []

    def _dfs(item: SpecItem, path: list[SpecItem]) -> None:
        path.append(item)
        downstream = children.get(item.full_id, [])
        if not downstream:
            chains.append(list(path))
        else:
            for child in downstream:
                _dfs(child, path)
        path.pop()

    for root in roots:
        _dfs(root, [])

    return chains
