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
        help="comma-separated owner/name list; default scans repos owned by "
        "the authenticated user (user:@me — not org or collaborator repos)",
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
    args.repos = None
    if args.repo is not None:
        args.repos = [repo.strip() for repo in args.repo.split(",")]
        if not all(args.repos):
            parser.error("--repo contains an empty element")
    args.issues = None
    if args.issue is not None:
        numbers = [n.strip() for n in args.issue.split(",")]
        if not all(numbers):
            parser.error("--issue contains an empty element")
        if not all(n.isdigit() for n in numbers):
            parser.error("--issue contains a non-numeric element")
        args.issues = [int(n) for n in numbers]
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
        # Bulk runs silently omit untriaged/stale-labeled issues, but an
        # explicitly requested number that the fetch never returned is an
        # error — a typo or an issue outside the canonical workflow.
        missing = sorted(set(args.issues) - {issue.number for issue in issues})
        if missing:
            raise SystemExit(
                f"error: requested issue(s) not returned by the fetch: "
                f"{', '.join(map(str, missing))} (nonexistent, untriaged, or "
                f"outside the canonical workflow)"
            )
        issues = [issue for issue in issues if issue.number in args.issues]
    records = [
        record
        for issue in issues
        if (record := build_record(issue, now=now)) is not None
    ]
    output: object = live_view(records) if args.live else records
    print(json.dumps(output, indent=2))
    return 0
