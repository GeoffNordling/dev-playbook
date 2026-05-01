"""sdd-atlas: full body of every dsn across the project, keyed by dimension.

Same discovery and dimension-grouping as ``sdd-index``, but emits each item's
full body (description, keyword fields, Interface/AgentReview entries) instead
of a one-line summary. Use when the catalog view from ``sdd-index`` is not
enough and the reader needs the prose.

Exit codes:
    0 -- success
    2 -- tool-level error (missing or malformed [tool.pytest-sdd] config)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sdd_tools.config import find_project_root, load_config_from_root
from sdd_tools.models import DIMENSION_NAMES, SpecItem
from sdd_tools.parse.markdown import group_by_dimension, parse_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdd-atlas",
        description=(
            "Emit the full body of every dsn item in the project, grouped "
            "by dimension. Reads [tool.pytest-sdd] config from pyproject.toml."
        ),
    )
    parser.add_argument(
        "--root",
        dest="root",
        metavar="DIR",
        type=Path,
        help="project root directory (default: auto-detect from cwd)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root or find_project_root()

    try:
        config = load_config_from_root(root)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if config is None:
        print(
            "Error: no [tool.pytest-sdd] section found in pyproject.toml",
            file=sys.stderr,
        )
        return 2

    files = parse_project(config.spec_dirs)
    groups = group_by_dimension(files)

    sys.stdout.write(render_atlas(groups, root))
    return 0


def render_atlas(
    groups: dict[str, list[SpecItem]],
    root: Path,
) -> str:
    """Render the grouped items as markdown with full bodies per dsn."""
    parts: list[str] = ["# Spec Atlas", ""]
    for dim in DIMENSION_NAMES:
        parts.append(f"## {dim}")
        parts.append("")
        dsn_items = [
            item for item in groups.get(dim, []) if item.doctype == "dsn"
        ]
        for item in dsn_items:
            parts.append(render_atlas_item(item, root))
        if not dsn_items:
            # Preserve the explicit "nothing here" signal for the section.
            pass
    return "\n".join(parts).rstrip() + "\n"


def render_atlas_item(item: SpecItem, root: Path) -> str:
    """Render one item's body as markdown."""
    try:
        rel = item.source_file.relative_to(root)
    except ValueError:
        rel = item.source_file

    parts: list[str] = []
    if item.title:
        parts.append(f"### {item.title}")
    parts.append(f"`{item.id}`")
    if item.status:
        parts.append(f"Status: {item.status}")
    parts.append(f"Source: {rel}:{item.source_line}")
    parts.append("")

    if item.description:
        parts.append(item.description)
        parts.append("")

    if item.rationale:
        parts.append("Rationale:")
        parts.append(item.rationale)
        parts.append("")

    if item.covers:
        parts.append("Covers:")
        for c in item.covers:
            parts.append(f"- {c}")
        parts.append("")

    if item.needs:
        parts.append(f"Needs: {', '.join(item.needs)}")
        parts.append("")

    for iface in item.interfaces:
        parts.append(f"Interface: {iface}")
    if item.interfaces:
        parts.append("")

    for ar in item.agent_reviews:
        parts.append(f"AgentReview: {ar}")
    if item.agent_reviews:
        parts.append("")

    return "\n".join(parts).rstrip() + "\n\n"


if __name__ == "__main__":
    raise SystemExit(main())
