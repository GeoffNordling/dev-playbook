"""sdd-review: inventory every dsn with AgentReview: fields.

Reporting tool, not validation. Emits a structured markdown record for each
dsn that carries one or more ``AgentReview:`` fields, listing the dsn id,
source location, dimension section, and every review prose entry. The
``sdd-review`` skill reads this output and dispatches a review agent per
record.

Exit codes:
    0 -- success (records emitted, or empty inventory)
    2 -- tool-level error (missing or malformed [tool.pytest-sdd] config)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from sdd_tools.config import find_project_root, load_config_from_root
from sdd_tools.models import SpecFile, SpecItem
from sdd_tools.parse.markdown import parse_project


@dataclass
class _ReviewRecord:
    item: SpecItem
    section_header: str | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdd-review",
        description=(
            "Inventory every dsn carrying AgentReview: fields. Reporting tool, "
            "not validation — run `pytest -m spec -k lint` for AgentReview "
            "well-formedness. Reads [tool.pytest-sdd] from pyproject.toml."
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
    records = _collect_records(files)
    sys.stdout.write(render_review(records, root))
    return 0


def _collect_records(files: list[SpecFile]) -> list[_ReviewRecord]:
    records: list[_ReviewRecord] = []
    for sf in files:
        for section in sf.sections:
            for item in section.items:
                if item.doctype == "dsn" and item.agent_reviews:
                    records.append(
                        _ReviewRecord(item=item, section_header=section.header)
                    )
    return records


def render_review(records: list[_ReviewRecord], root: Path) -> str:
    """Render the inventory as markdown.

    Every record gets its own ``## `dsn~...``` heading; the skill parses
    these as discrete review targets.
    """
    if not records:
        return "# AgentReview Inventory\n\nNo AgentReview: fields found.\n"

    parts: list[str] = ["# AgentReview Inventory", ""]
    for record in records:
        parts.append(_render_record(record, root))
    return "\n".join(parts).rstrip() + "\n"


def _render_record(record: _ReviewRecord, root: Path) -> str:
    item = record.item
    try:
        rel = item.source_file.relative_to(root)
    except ValueError:
        rel = item.source_file

    title = item.title or item.name
    section_label = record.section_header or "(no section)"

    lines: list[str] = []
    lines.append(f"## `{item.id}` — {title}")
    lines.append(f"Source: {rel}:{item.source_line}")
    lines.append(f"Section: {section_label}")
    lines.append("")
    lines.append("Reviews:")
    for review in item.agent_reviews:
        lines.append(f"- {review}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
