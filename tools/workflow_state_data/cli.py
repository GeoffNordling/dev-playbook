"""Selector parsing and JSON emission for the workflow-state-data CLI."""

import argparse
import json
from collections.abc import Callable
from datetime import UTC, datetime

from workflow_state_data.core import IssueData, build_record, live_view
from workflow_state_data.github import fetch_issues


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse and validate CLI selectors into repos/issues lists."""
    parser = argparse.ArgumentParser(
        prog="workflow-state-data",
        description="Derive workflow metrics and live issue states from GitHub.",
    )
    parser.add_argument(
        "--repo",
        help="comma-separated owner/name list; default is account-wide",
    )
    parser.add_argument(
        "--issue",
        help="comma-separated issue numbers; requires exactly one --repo",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="emit open issues grouped by current phase",
    )
    args = parser.parse_args(argv)
    args.repos = args.repo.split(",") if args.repo else None
    if args.repos is not None and not all(args.repos):
        parser.error("--repo contains an empty element")
    if args.issue is not None and not all(args.issue.split(",")):
        parser.error("--issue contains an empty element")
    args.issues = [int(n) for n in args.issue.split(",")] if args.issue else None
    if args.issues is not None and (args.repos is None or len(args.repos) != 1):
        parser.error("--issue requires exactly one --repo")
    return args


def main(
    argv: list[str],
    fetch: Callable[[list[str] | None], list[IssueData]] = fetch_issues,
    now: datetime | None = None,
) -> int:
    """Fetch, reconstruct, and print issue records (or the live view) as JSON."""
    args = _parse_args(argv)
    now = now if now is not None else datetime.now(UTC)
    issues = fetch(args.repos)
    if args.issues is not None:
        issues = [issue for issue in issues if issue.number in args.issues]
    records = [
        record
        for issue in issues
        if (record := build_record(issue, now=now)) is not None
    ]
    output: object = live_view(records) if args.live else records
    print(json.dumps(output, indent=2))
    return 0
