"""Filter traceability chains by id pattern, type, source file, or feature root."""

from __future__ import annotations

import fnmatch

from sdd_tools.models import SpecItem


def filter_chains(
    chains: list[list[SpecItem]],
    *,
    id_pattern: str | None = None,
    doctype: str | None = None,
    source_file: str | None = None,
    feature: str | None = None,
) -> list[list[SpecItem]]:
    """Return a filtered subset of chains.

    id_pattern -- glob; chain kept if any item's id matches.
    doctype    -- chain kept if any item is of this doctype.
    source_file -- substring; chain kept if any item's source file contains it.
    feature    -- glob; chain kept only if its root is a feat item that matches.
    """
    result = chains

    if feature is not None:
        result = [
            c
            for c in result
            if c
            and c[0].doctype == "feat"
            and fnmatch.fnmatch(c[0].id, feature)
        ]

    if id_pattern is not None:
        result = [
            c
            for c in result
            if any(fnmatch.fnmatch(item.id, id_pattern) for item in c)
        ]

    if doctype is not None:
        result = [c for c in result if any(item.doctype == doctype for item in c)]

    if source_file is not None:
        result = [
            c
            for c in result
            if any(source_file in str(item.source_file) for item in c)
        ]

    return result
