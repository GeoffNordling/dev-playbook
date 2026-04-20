"""sdd-chain: render full spec traceability chains with body text.

Reads ``[tool.pytest-sdd]`` config from the project's ``pyproject.toml``,
runs the OFT JAR's ``convert`` command to extract all spec items as XML,
builds coverage chains, and prints them with the full body text at every
layer. Test layers are excluded from chain output.

Exit codes:
    0 -- success (chains rendered, or no chains found)
    2 -- tool-level error (missing config, JAR, or Java)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sdd_tools.chains import build_chains
from sdd_tools.config import find_project_root, load_config_from_root
from sdd_tools.filtering import filter_chains
from sdd_tools.formatter import format_chains
from sdd_tools.oft import load_spec_items


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdd-chain",
        description=(
            "Render spec traceability chains with full body text. "
            "Reads [tool.pytest-sdd] config from pyproject.toml."
        ),
    )
    parser.add_argument(
        "--id",
        dest="id_pattern",
        metavar="PATTERN",
        help="show chains containing an item matching this glob (e.g. '*auth*')",
    )
    parser.add_argument(
        "--type",
        dest="doctype",
        metavar="TYPE",
        help="show chains containing an item of this type (e.g. 'req', 'dsn')",
    )
    parser.add_argument(
        "--file",
        dest="source_file",
        metavar="SUBSTRING",
        help="show chains with items from files matching this substring",
    )
    parser.add_argument(
        "--feature",
        dest="feature",
        metavar="PATTERN",
        help="show only chains rooted at a feat item matching this glob",
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
    parser = build_parser()
    args = parser.parse_args(argv)

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

    try:
        items = load_spec_items(config.oft_jar, config.spec_dirs)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

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
        return 0

    sys.stdout.write(format_chains(chains, root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
