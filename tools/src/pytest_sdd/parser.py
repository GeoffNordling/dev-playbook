"""Parse OFT Requirement-Enhanced Markdown files into SpecItem lists.

A spec file is a markdown document containing one or more specification items
separated by horizontal rules (---). Each spec item has the structure:

    ### Title
    `type~name~revision`
    Status: approved

    Description text...

    Rationale:
    Why this requirement exists.

    Covers:
      - req~area.name~1

    Needs: dsn, utest

Items are separated by horizontal rules. Non-item segments (introductory prose,
H2-only sections, index files) are ignored without error.
"""

import re
from pathlib import Path

from pytest_sdd.models import (
    COVERS_RE,
    H3_RE,
    HRULE_RE,
    NEEDS_RE,
    SPEC_ID_RE,
    STATUS_RE,
    SpecItem,
)


def parse_spec_file(path: Path) -> list[SpecItem]:
    """Parse all spec items from an OFT markdown file.

    Returns an empty list for files with no spec items (index files, prose-only
    sections). Does not raise on missing fields — missing Status or Needs are
    captured as empty strings/lists and flagged by the linter.
    """
    text = path.read_text(encoding="utf-8")
    segments = HRULE_RE.split(text)
    items: list[SpecItem] = []
    line_offset = 0

    for segment in segments:
        id_match = SPEC_ID_RE.search(segment)
        if id_match:
            item = _parse_segment(segment, id_match, path, line_offset)
            items.append(item)
        line_offset += segment.count("\n") + 1  # +1 for the consumed --- line

    return items


def _parse_segment(
    segment: str,
    id_match: "re.Match",
    path: Path,
    line_offset: int,
) -> SpecItem:
    """Extract a SpecItem from a single text segment containing an ID match."""
    item_type = id_match.group(1)
    name = id_match.group(2)
    revision = int(id_match.group(3))
    spec_id = f"{item_type}~{name}~{revision}"

    # Line number of the ID within the file
    id_line_in_segment = segment[: id_match.start()].count("\n")
    line_number = line_offset + id_line_in_segment

    # Title: last ### heading that appears before the ID line in this segment
    pre_id = segment[: id_match.start()]
    h3_matches = list(H3_RE.finditer(pre_id))
    title = h3_matches[-1].group(1).strip() if h3_matches else ""

    # Status
    status_match = STATUS_RE.search(segment)
    status = status_match.group(1).strip().lower() if status_match else ""

    # Needs (inline comma-separated: "Needs: dsn, utest")
    needs: list[str] = []
    needs_match = NEEDS_RE.search(segment)
    if needs_match:
        needs = [n.strip() for n in needs_match.group(1).split(",") if n.strip()]

    # Covers block
    covers: list[str] = []
    covers_match = COVERS_RE.search(segment)
    if covers_match:
        for line in covers_match.group(1).splitlines():
            ref = line.strip().lstrip("-*+").strip()
            if ref:
                covers.append(ref)

    return SpecItem(
        id=spec_id,
        item_type=item_type,
        name=name,
        revision=revision,
        title=title,
        status=status,
        body=segment,
        needs=needs,
        covers=covers,
        source_file=str(path),
        line_number=line_number,
    )
