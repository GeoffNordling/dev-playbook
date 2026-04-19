"""Command-line interface for sdd-chain-text."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pytest_sdd.config import load_config_from_root

from .chains import build_chains
from .filtering import filter_chains
from .formatter import format_chains
from .oft_xml import load_spec_items


def _find_project_root() -> Path:
    """Walk up from cwd to find a directory with pyproject.toml."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    return cwd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdd-chain-text",
        description=(
            "Display spec traceability chains with full body text. "
            "Reads [tool.pytest-sdd] config from pyproject.toml."
        ),
    )
    parser.add_argument(
        "--id",
        dest="id_pattern",
        metavar="PATTERN",
        help="Show chains containing an item matching this glob (e.g. '*auth*')",
    )
    parser.add_argument(
        "--type",
        dest="doctype",
        metavar="TYPE",
        help="Show chains containing an item of this type (e.g. 'req', 'dsn')",
    )
    parser.add_argument(
        "--file",
        dest="source_file",
        metavar="SUBSTRING",
        help="Show chains with items from files matching this substring",
    )
    parser.add_argument(
        "--feature",
        dest="feature",
        metavar="PATTERN",
        help="Show only chains rooted at a feat item matching this glob",
    )
    parser.add_argument(
        "--root",
        dest="root",
        metavar="DIR",
        type=Path,
        help="Project root directory (default: auto-detect from cwd)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = args.root or _find_project_root()
    config = load_config_from_root(root)
    if config is None:
        print(
            "Error: No [tool.pytest-sdd] section found in pyproject.toml",
            file=sys.stderr,
        )
        sys.exit(1)

    items = load_spec_items(config.oft_jar, config.spec_dirs)
    chains = build_chains(items)
    chains = filter_chains(
        chains,
        id_pattern=args.id_pattern,
        doctype=args.doctype,
        source_file=args.source_file,
        feature=args.feature,
    )

    if not chains:
        print("No chains found.", file=sys.stderr)
        return

    output = format_chains(chains, root)
    sys.stdout.write(output)
