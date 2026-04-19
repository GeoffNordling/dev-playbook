"""Format traceability chains as human-readable text output."""

from __future__ import annotations

import io
from pathlib import Path

from .oft_xml import SpecItem


def format_chains(chains: list[list[SpecItem]], root: Path) -> str:
    """Format a list of chains into the output text format."""
    buf = io.StringIO()

    for i, chain in enumerate(chains, 1):
        chain_label = " > ".join(item.full_id for item in chain)
        buf.write(f"=== Chain {i}: {chain_label} ===\n")

        for item in chain:
            source = _relative_path(item.source_file, root)
            buf.write(f"\n[{item.doctype}] {item.full_id}\n")
            buf.write(f"Title: {item.title}\n")
            buf.write(f"File: {source}:{item.source_line}\n")
            buf.write("\n")
            _write_body(buf, item)

        buf.write("\n")

    return buf.getvalue()


def _relative_path(source_file: str, root: Path) -> str:
    """Make a source file path relative to root."""
    return str(Path(source_file).relative_to(root))


def _write_body(buf: io.StringIO, item: SpecItem) -> None:
    """Write the body text of a spec item, reconstructing structural fields."""
    if item.status:
        buf.write(f"  Status: {item.status}\n\n")

    if item.description:
        for line in item.description.splitlines():
            buf.write(f"  {line}\n" if line else "\n")
        buf.write("\n")

    if item.rationale:
        buf.write("  Rationale:\n")
        for line in item.rationale.splitlines():
            buf.write(f"  {line}\n" if line else "\n")
        buf.write("\n")

    if item.covers:
        buf.write("  Covers:\n")
        for ref in item.covers:
            buf.write(f"    - {ref}\n")
        buf.write("\n")

    if item.needs:
        buf.write(f"  Needs: {', '.join(item.needs)}\n")
