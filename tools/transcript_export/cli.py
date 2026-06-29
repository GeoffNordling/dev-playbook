"""Command-line entry for transcript-export.

Selects sessions, renders each to XML, and writes one `<out_dir>/<id>.xml` file
per session — re-running overwrites (idempotent regenerate). Three selection
modes, exactly one per invocation: explicit ids, `--recent N` (the N
most-recently-active sessions), or `--all` (every top-level session AgentsView
lists). Selection reads the `session list` payload; rendering recurses through
the AgentsView client. See PLAN.md for the authoritative design.
"""

import argparse
import subprocess
from collections.abc import Callable
from pathlib import Path

from transcript_export.client import session_list
from transcript_export.transcript import render_session


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse argv and validate that exactly one selection mode was given."""
    parser = argparse.ArgumentParser(
        prog="transcript-export",
        description="Export Claude Code sessions to XML transcripts.",
    )
    parser.add_argument("out_dir", help="directory to write <id>.xml files into")
    parser.add_argument(
        "session_ids",
        nargs="*",
        metavar="SESSION_ID",
        help="explicit session ids to export",
    )
    parser.add_argument(
        "--recent",
        type=int,
        metavar="N",
        help="export the N most-recently-active sessions",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="export every top-level session AgentsView lists",
    )
    args = parser.parse_args(argv)
    modes = [bool(args.session_ids), args.recent is not None, args.all]
    if sum(modes) != 1:
        parser.error(
            "select sessions exactly one way: explicit ids, --recent N, or --all"
        )
    if args.recent is not None and args.recent <= 0:
        parser.error("--recent N requires a positive integer")
    return args


def select_session_ids(
    explicit_ids: list[str],
    recent: int | None,
    select_all: bool,
    runner: Callable = subprocess.run,
) -> list[str]:
    """Resolve a selection mode to the ordered list of session ids to export.

    Explicit ids pass straight through (no daemon call). `--recent N` and
    `--all` read the `session list` payload — already newest-first — and take
    the first N or all of them. The three modes are mutually exclusive; the
    caller validates that, so here exactly one is active.
    """
    if explicit_ids:
        return explicit_ids
    ids = [session["id"] for session in session_list(runner=runner)["sessions"]]
    if recent is not None:
        return ids[:recent]
    return ids


def main(
    argv: list[str],
    runner: Callable = subprocess.run,
    render: Callable = render_session,
) -> int:
    """Select sessions, render each to XML, write `<out_dir>/<id>.xml`."""
    args = _parse_args(argv)
    session_ids = select_session_ids(
        args.session_ids, args.recent, args.all, runner=runner
    )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for session_id in session_ids:
        path = out_dir / f"{session_id}.xml"
        path.write_text(render(session_id, runner=runner), encoding="utf-8")
        print(path)
    return 0
