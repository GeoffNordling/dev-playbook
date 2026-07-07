"""The impure boundary: AgentsView CLI access.

Thin wrappers over the `agentsview` CLI's three read commands — `session list`,
`session get`, `session messages`. Each shells out, parses the one JSON object
the command prints to stdout, and fails loud on a nonzero exit. The
deterministic parts (argument building, message paging) are separable and
tested with an injected fake runner; only the subprocess call itself is the
humble boundary.
"""

import json
import subprocess
from collections.abc import Callable
from typing import cast

DEFAULT_PAGE = 100
"""`session messages` returns at most this many rows per call (the CLI default),
so we always pass --limit and page on last_ordinal + 1."""

DAEMON_URL = "http://127.0.0.1:8080"
"""The always-running local agentsview daemon (its default listen address).

We pass this as `--server` on every command so the CLI acts as a pure *client*
of the daemon instead of auto-starting its own server. The auto-start path opens
the sqlite archive writable, which fails whenever the standing daemon already
holds the write lock (`~/.agentsview/db.write.lock`) — the exact spurious failure
tracked in issue #135. As a read-only client of the running daemon, we never
contend for that lock."""


class AgentsViewError(Exception):
    """Any agentsview CLI failure — fail loud, never partial output."""


class SessionNotFound(AgentsViewError):
    """The CLI reported the requested session id absent from the archive.

    Raised so callers can tell an unresolvable link — a session the daemon
    references but never ingested — apart from an infrastructure failure
    (daemon down, bad arguments), which stays a bare `AgentsViewError`.
    """


def _run(args: list[str], runner: Callable = subprocess.run) -> dict:
    """Run one agentsview command against the running daemon; parse its JSON stdout.

    Every command targets the standing daemon via `--server` (see `DAEMON_URL`)
    so the CLI never auto-starts a competing server. Fail loud on nonzero: a
    `not found` on stderr becomes `SessionNotFound`, any other nonzero exit a
    bare `AgentsViewError`. Matching on the stderr text is acceptable here
    because this module is explicitly the humble subprocess boundary.
    """
    result = runner(
        ["agentsview", "--server", DAEMON_URL, *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        message = (
            f"agentsview {' '.join(args)} failed (rc={result.returncode}): "
            f"{result.stderr.strip()[:300]}"
        )
        if "not found" in result.stderr:
            raise SessionNotFound(message)
        raise AgentsViewError(message)
    return cast(dict, json.loads(result.stdout))


def session_list(runner: Callable = subprocess.run) -> dict:
    """Return the `session list` payload: {sessions, next_cursor, total}.

    Sub-agent sessions are excluded by default — exactly the set we pick a
    top-level transcript from.
    """
    return _run(["session", "list", "--format", "json"], runner=runner)


def session_get(session_id: str, runner: Callable = subprocess.run) -> dict:
    """Return `session get` metadata for one session (the <session> header)."""
    return _run(["session", "get", session_id, "--json"], runner=runner)


def session_messages(
    session_id: str,
    page: int = DEFAULT_PAGE,
    runner: Callable = subprocess.run,
) -> list[dict]:
    """Return every message row for a session, in order, paging to exhaustion.

    `session messages` caps each response at `page` rows, so we page until a
    batch comes back empty. Ordinals are a sparse global index, so the cursor
    advances to the last ordinal + 1 each round; the `last + 1 <= frm` guard
    stops a non-advancing cursor from looping forever.
    """
    messages: list[dict] = []
    frm = 0
    while True:
        payload = _run(
            [
                "session",
                "messages",
                session_id,
                "--json",
                "--from",
                str(frm),
                "--limit",
                str(page),
            ],
            runner=runner,
        )
        batch = payload["messages"]
        if not batch:
            break
        messages.extend(batch)
        last = batch[-1]["ordinal"]
        if last + 1 <= frm:
            break
        frm = last + 1
    return messages
