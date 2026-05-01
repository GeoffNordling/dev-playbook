"""sdd-index: one-line catalog of every dsn across the project, keyed by dimension.

Scans the project's spec directories, parses every ``.md`` file via the
markdown-tier parser, and emits a compact markdown catalog grouped by the four
design dimensions (``Data``, ``API Shape``, ``Algorithms``, ``Composition``).
Each entry names the dsn id, title, and source location — enough for a human
or an agent to decide which bodies are worth reading.

Exit codes:
    0 -- success (catalog emitted)
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
        prog="sdd-index",
        description=(
            "Emit a per-dimension one-line catalog of every dsn item in "
            "the project. Reads [tool.pytest-sdd] config from pyproject.toml."
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

    sys.stdout.write(render_index(groups, root))
    return 0


def render_index(
    groups: dict[str, list[SpecItem]],
    root: Path,
) -> str:
    """Render the grouped items as markdown keyed by dimension header."""
    lines: list[str] = ["# Spec Index", ""]
    for dim in DIMENSION_NAMES:
        lines.append(f"## {dim}")
        lines.append("")
        for item in groups.get(dim, []):
            if item.doctype != "dsn":
                continue
            lines.append(_format_entry(item, root))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _format_entry(item: SpecItem, root: Path) -> str:
    try:
        rel = item.source_file.relative_to(root)
    except ValueError:
        rel = item.source_file
    title = item.title or item.name
    return f"- `{item.id}` — {title} ({rel}:{item.source_line})"


if __name__ == "__main__":
    raise SystemExit(main())
