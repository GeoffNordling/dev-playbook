"""Filter traceability chains by various criteria."""

from __future__ import annotations

import fnmatch

from .oft_xml import SpecItem


def filter_chains(
    chains: list[list[SpecItem]],
    *,
    id_pattern: str | None = None,
    doctype: str | None = None,
    source_file: str | None = None,
    feature: str | None = None,
) -> list[list[SpecItem]]:
    """Filter chains based on the given criteria.

    Args:
        chains: All chains to filter.
        id_pattern: Keep chains containing an item whose full_id matches
            this glob pattern (e.g. ``*auth*``, ``req~meta.*``).
        doctype: Keep chains containing at least one item of this type
            (e.g. ``req``, ``dsn``).
        source_file: Keep chains containing an item whose source file
            path contains this substring.
        feature: Keep only chains rooted at a feat item matching this
            glob pattern (e.g. ``*user-auth*``).

    Returns:
        Filtered list of chains.
    """
    result = chains

    if feature is not None:
        result = [
            c
            for c in result
            if c and c[0].doctype == "feat" and fnmatch.fnmatch(c[0].full_id, feature)
        ]

    if id_pattern is not None:
        result = [
            c
            for c in result
            if any(fnmatch.fnmatch(item.full_id, id_pattern) for item in c)
        ]

    if doctype is not None:
        result = [c for c in result if any(item.doctype == doctype for item in c)]

    if source_file is not None:
        result = [
            c for c in result if any(source_file in item.source_file for item in c)
        ]

    return result
