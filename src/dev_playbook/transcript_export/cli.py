"""Command-line entry for transcript-export.

Selects sessions, renders each to XML, and writes one `<out_dir>/<id>.xml` file
per session — re-running overwrites (idempotent regenerate). Four selection
modes, exactly one per invocation: explicit ids, `--find PATTERN` (the sessions
whose content matches), `--recent N` (the N most-recently-active), or `--all`
(every top-level session AgentsView lists, paged to exhaustion). Rendering
recurses through the AgentsView client.

`--find` exists so a caller never has to reach past this tool to the `agentsview`
CLI: finding the session is the step that needs a daemon URL, a `--server` flag,
and a dedup over per-message matches, and none of that is the caller's problem.

An unreachable daemon, and an ambiguous or empty `--find`, are each reported as
one line on stderr rather than a traceback: all three are routine, and the caller
needs the reason and the next move, not our call stack.
"""

import argparse
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from dev_playbook.transcript_export.client import (
    AgentsViewError,
    session_list,
    session_search,
)
from dev_playbook.transcript_export.transcript import render_session

EPILOG = """\
selecting a session:
  this session   transcript-export out/ "$CLAUDE_CODE_SESSION_ID"
  by content     transcript-export out/ --find 'the auth bug'
  most recent    transcript-export out/ --recent 3
  by id          transcript-export out/ 9c0c13d6-1f4e-4a02-bd11-3c9f0e7a5d81

$CLAUDE_CODE_SESSION_ID names the running session; it is set in every Claude
Code session, so the first form needs nothing else.

For filters --find does not expose (--project, --date-from, --regex), query the
daemon directly and pass the ids through. Note that agentsview requires
--server: without it the CLI auto-starts a rival daemon, which then dies on the
write lock the running one holds.

  agentsview --server http://127.0.0.1:8080 session search 'x' --json
"""


class SelectionError(Exception):
    """A selection that named no session, or too many to be unambiguous."""


def _parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse argv and validate that exactly one selection mode was given."""
    parser = argparse.ArgumentParser(
        prog="transcript-export",
        description="Export Claude Code sessions to XML transcripts.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("out_dir", help="directory to write <id>.xml files into")
    parser.add_argument(
        "session_ids",
        nargs="*",
        metavar="SESSION_ID",
        help="explicit session ids to export",
    )
    parser.add_argument(
        "--find",
        metavar="PATTERN",
        help="export the sessions whose message or tool content matches PATTERN",
    )
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="with --find, export at most N matching sessions (newest first)",
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
    modes = [
        bool(args.session_ids),
        args.find is not None,
        args.recent is not None,
        args.all,
    ]
    if sum(modes) != 1:
        parser.error(
            "select sessions exactly one way: explicit ids, --find PATTERN, "
            "--recent N, or --all"
        )
    if args.recent is not None and args.recent <= 0:
        parser.error("--recent N requires a positive integer")
    if args.limit is not None:
        if args.find is None:
            parser.error("--limit N applies only to --find PATTERN")
        if args.limit <= 0:
            parser.error("--limit N requires a positive integer")
    return args


def _search_session_ids(
    pattern: str,
    limit: int | None,
    runner: Callable = subprocess.run,
) -> list[str]:
    """Resolve a `--find` pattern to the distinct sessions whose content matches.

    One `session search` call answers up to `SEARCH_MATCH_CAP` per-message
    matches, many of them sharing a session; dedup keeps the daemon's order
    (newest first). A bare pattern matching several sessions is ambiguous, not a
    licence to export all of them, so it fails loud and names the next move. A
    truncated match set bounds the session count only from below, and the message
    says "at least" rather than assert a total it never saw.
    """
    payload = session_search(pattern, runner=runner)
    session_ids: list[str] = []
    for match in payload["matches"]:
        if match["session_id"] not in session_ids:
            session_ids.append(match["session_id"])
    if not session_ids:
        raise SelectionError(f"no session matched {pattern!r}")
    if limit is None and len(session_ids) > 1:
        at_least = "at least " if payload.get("next_cursor") else ""
        raise SelectionError(
            f"{pattern!r} matched {at_least}{len(session_ids)} sessions; "
            f"narrow the pattern or pass --limit N"
        )
    # `limit is None` here means exactly one match, and [:None] is the whole list.
    return session_ids[:limit]


def select_session_ids(
    explicit_ids: list[str],
    recent: int | None,
    select_all: bool,
    find: str | None = None,
    limit: int | None = None,
    runner: Callable = subprocess.run,
) -> list[str]:
    """Resolve a selection mode to the ordered list of session ids to export.

    Explicit ids pass straight through (no daemon call). `--find` searches
    message and tool content. `--recent N` and `--all` read `session list`,
    already newest-first, and `session_list` asks the daemon for only the rows
    the mode needs — `--recent 3` fetches three, not the whole archive. The four
    modes are mutually exclusive; the caller validates that, so here exactly one
    is active. `select_all` is that fourth mode, expressed as `recent is None`.
    """
    if explicit_ids:
        return explicit_ids
    if find is not None:
        return _search_session_ids(find, limit, runner=runner)
    return [session["id"] for session in session_list(limit=recent, runner=runner)]


def main(
    argv: list[str],
    runner: Callable = subprocess.run,
    render: Callable = render_session,
) -> int:
    """Select sessions, render each to XML, write `<out_dir>/<id>.xml`.

    A daemon failure or an unusable `--find` aborts the whole export with one
    stderr line and a nonzero exit — loud, but legible. Nothing is half-written
    on the way out: selection resolves before the first file is opened.
    """
    args = _parse_args(argv)
    try:
        session_ids = select_session_ids(
            args.session_ids,
            args.recent,
            args.all,
            args.find,
            args.limit,
            runner=runner,
        )
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for session_id in session_ids:
            path = out_dir / f"{session_id}.xml"
            path.write_text(render(session_id, runner=runner), encoding="utf-8")
            print(path)
    except (AgentsViewError, SelectionError) as exc:
        print(f"transcript-export: {exc}", file=sys.stderr)
        return 1
    return 0
