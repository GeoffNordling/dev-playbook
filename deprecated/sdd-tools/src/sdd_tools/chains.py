"""Enumerate linear traceability chains from OFT coverage links.

Each SpecItem carries ``covers`` (upstream references) supplied by the OFT
JAR. This module walks those links to produce maximal root-to-leaf paths,
excluding test layers (utest, itest, stest) from the chain output.
"""

from __future__ import annotations

from sdd_tools.models import SpecItem

_TEST_TYPES = frozenset({"utest", "itest", "stest"})


def build_chains(items: list[SpecItem]) -> list[list[SpecItem]]:
    """Build all linear traceability chains from the given spec items.

    Each chain is a list of SpecItems ordered root → leaf. Branching produces
    separate chains; shared upstream items repeat across chains. Test layers
    are excluded.
    """
    by_id: dict[str, SpecItem] = {item.id: item for item in items}
    non_test = [i for i in items if i.doctype not in _TEST_TYPES]

    children: dict[str, list[SpecItem]] = {}
    has_parent: set[str] = set()
    for item in non_test:
        for covered_id in item.covers:
            if covered_id in by_id:
                children.setdefault(covered_id, []).append(item)
                has_parent.add(item.id)

    roots = [i for i in non_test if i.id not in has_parent]

    chains: list[list[SpecItem]] = []

    def _dfs(item: SpecItem, path: list[SpecItem]) -> None:
        path.append(item)
        downstream = children.get(item.id, [])
        if not downstream:
            chains.append(list(path))
        else:
            for child in downstream:
                _dfs(child, path)
        path.pop()

    for root in roots:
        _dfs(root, [])

    return chains
