"""The software factory's append-only run ledger.

The `ledger` table sits beside the hook-capture `events` table in the same
SQLite store, and this module is the only code that touches it. Rows are
appended and never changed: state is derived by reading which records exist
and which are absent.
"""

import json
import sqlite3
from collections.abc import Iterator, Mapping
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

DB_PATH = Path("~/.local/share/claude-measure/events.db").expanduser()

# Concurrent traverses write to one database. WAL lets their readers and
# writers coexist, and the busy timeout makes a collision queue rather than
# fail.
BUSY_TIMEOUT_SECONDS = 5.0
WAL = "wal"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY,
    received_at TEXT,
    kind TEXT,
    repo TEXT,
    issue INTEGER,
    node TEXT,
    session_id TEXT,
    payload TEXT
)
"""

INSERT = """
INSERT INTO ledger (received_at, kind, repo, issue, node, session_id, payload)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

# Every read selects these, in this order; `_decode` reads a row back by that
# order into a `LedgerRow`.
COLUMNS = "id, received_at, kind, repo, issue, node, session_id, payload"

# Sequencing is by `id` throughout: it is the only order the ledger guarantees.
# `received_at` is there for wall-clock accounting and is never compared here.
#
# A job is live while it has been launched and nothing has since ended it: no
# report for its session, no newer launch of the same node taking its place,
# and its traverse window still open. A window closes at `traverse-end` or at
# the next `traverse-start` for the same repo and issue -- never at
# `traverse-escalation`, which is followed by the `traverse-end` that does
# close it. That holds because every `traverse_issue` exit, escalated exits
# included, writes `traverse-end` as its last record (epic standing ruling 4).
LIVE_JOBS = f"""
SELECT {COLUMNS} FROM ledger AS l
WHERE l.kind = 'job-launch'
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS reported
      WHERE reported.kind = 'job-report'
        AND reported.session_id = l.session_id
        AND reported.id > l.id
  )
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS relaunched
      WHERE relaunched.kind = 'job-launch'
        AND relaunched.repo = l.repo
        AND relaunched.issue = l.issue
        AND relaunched.node = l.node
        AND relaunched.id > l.id
  )
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS closer
      WHERE closer.kind IN ('traverse-end', 'traverse-start')
        AND closer.repo = l.repo
        AND closer.issue = l.issue
        AND closer.id > l.id
  )
  AND (:repo IS NULL OR l.repo = :repo)
  AND (:issue IS NULL OR l.issue = :issue)
ORDER BY l.id
"""

# The rows `awaiting_merge` is about to match: each repo and issue's newest
# `traverse-end`, minus those an issue has since been closed out of. What a
# superseded end said is dead history, and a closed-out issue's end is spent --
# neither is consulted, so neither can brick the read with a malformed payload.
AWAITING_MERGE = f"""
SELECT {COLUMNS} FROM ledger AS l
WHERE l.kind = 'traverse-end'
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS newer
      WHERE newer.kind = 'traverse-end'
        AND newer.repo = l.repo
        AND newer.issue = l.issue
        AND newer.id > l.id
  )
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS closed
      WHERE closed.kind = 'closeout'
        AND closed.repo = l.repo
        AND closed.issue = l.issue
        AND closed.id > l.id
  )
  AND (:repo IS NULL OR l.repo = :repo)
ORDER BY l.id
"""

# The one payload value this module reads. Everything else in a payload is the
# launcher's business and passes through uninterpreted.
#
# The vocabulary is closed and this module owns it: a `traverse-end` carries the
# status `traverse_issue` exited with, and those are the two terminal statuses
# the graph has. A candidate carrying anything else -- a missing key, a value
# that is not a string, a string nobody here recognises -- is a row this cannot
# judge, and it says so rather than dropping it. Adding a terminal status is an
# edit here, which is the point: the ledger is where a launcher's typo surfaces.
#
# A tuple, not a set: membership on a tuple compares rather than hashes, so an
# unhashable stored status -- a list, an object -- is judged unrecognised
# instead of raising `TypeError` out of the guard meant to catch it.
STATUS = "status"
PR_READY = "pr-ready"
ESCALATED = "escalated"
STATUSES = (PR_READY, ESCALATED)


class LedgerRow(NamedTuple):
    """One ledger row read back, with its payload decoded."""

    id: int
    received_at: str
    kind: str
    repo: str
    issue: int
    node: str | None
    session_id: str | None
    payload: dict[str, object]


class LedgerError(Exception):
    """The ledger is broken — the one thing a caller catches, `sqlite3` unimported.

    Three kinds of trouble raise it:

    - A **storage failure** — the store unwritable, connect, the DDL, an INSERT
      or SELECT, a busy timeout expiring — chained from the `sqlite3.Error` or
      `OSError` beneath it.
    - A **store that will not take WAL**, unchained: there is no underlying
      error, because SQLite reports a declined journal mode by returning the
      one it kept.
    - A **stored row this module cannot use**, naming the row id: a payload
      that will not decode (chained from the decode error), a payload that
      decodes into something other than a JSON object, a row with an empty
      promoted column that no query can therefore match, or a `traverse-end`
      candidate whose payload carries no `status` from the closed vocabulary
      at `STATUSES`. Only the first of these has an error to chain from; the
      rest are the store disagreeing with itself, not an operation failing.

    A caller's own bug is deliberately none of these — telling the operator
    their store is unusable would send them to check a disk that is fine. Each
    surfaces as itself, with nothing written: a payload that will not serialize
    raises `TypeError`, a job-grain write missing its node or session id raises
    `ValueError`, and a column argument SQLite cannot bind raises
    `sqlite3.ProgrammingError` or `sqlite3.InterfaceError`.
    """


def _require_wal(connection: sqlite3.Connection, db_path: Path) -> None:
    """Put the store in WAL journal mode, and refuse it when it will not go.

    `PRAGMA journal_mode=WAL` does not raise when the request is declined — it
    returns the mode it kept instead, which is what a network filesystem or a
    container overlay mount does. Carrying on would silently drop the
    concurrency the factory's parallel traverses run on, and surface much later
    as lock errors under exactly the load WAL exists to survive. So the refusal
    is raised here, at the connection, rather than degraded past.

    The pragma is persistent, so only the first connection of a database's life
    changes anything; every later one reads back the mode already set.
    """
    (mode,) = connection.execute("PRAGMA journal_mode=WAL").fetchone()
    if mode != WAL:
        raise LedgerError(
            f"run ledger at {db_path} would not take WAL journal mode and is in "
            f"{mode!r} mode, so concurrent traverses would collide"
        )


@contextmanager
def _ledger(db_path: Path) -> Iterator[sqlite3.Connection]:
    """The store, open with the table present, WAL on, and the busy timeout set.

    Every storage failure in the block — the store unwritable, connect, the
    DDL, the caller's own INSERT or SELECT, a busy timeout expiring — arrives
    here and leaves as `LedgerError`. Nothing is caught, retried, or degraded:
    the factory must hear that its ledger is broken.

    A caller's own bug is the one thing not converted. `sqlite3` raises
    `ProgrammingError` and `InterfaceError` for API misuse — a column argument
    it cannot bind, most likely — and telling the operator their store is
    unusable would send them to check a disk that is fine. Those leave as
    themselves, the same line `_append` draws one field over for a payload that
    will not serialize.
    """
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(
            sqlite3.connect(db_path, timeout=BUSY_TIMEOUT_SECONDS)
        ) as connection:
            _require_wal(connection, db_path)
            connection.execute(SCHEMA)
            yield connection
    # Two exception types, not one bound to a name: PEP 758, new in 3.14, which
    # this package requires. It reads character-for-character like Python 2's
    # `except X, name:` and is nothing of the sort. The parentheses that would
    # settle it on sight cannot be written here — `ruff format` strips them from
    # an unbound tuple and keeps them on the bound one below, which is the whole
    # reason these two lines disagree.
    except sqlite3.ProgrammingError, sqlite3.InterfaceError:
        raise
    except (sqlite3.Error, OSError) as error:
        raise LedgerError(f"run ledger at {db_path} is unusable: {error}") from error


def _append(
    kind: str,
    repo: str,
    issue: int,
    node: str | None,
    session_id: str | None,
    payload: Mapping[str, object],
    db_path: Path,
) -> None:
    """Append one row of any kind, stamping `received_at` as it goes.

    The payload is encoded before the store is touched, so a payload that will
    not serialize is a caller bug that raises with nothing written.

    `json.dumps` serializes `dict` alone, not the `Mapping` protocol, so the
    payload is copied into one first — otherwise the most natural immutable
    payloads, a `MappingProxyType` or a `ChainMap`, would be refused as
    unserializable despite being nothing of the sort.
    """
    encoded = json.dumps(dict(payload))
    received_at = datetime.now(UTC).isoformat(timespec="microseconds")
    with _ledger(db_path) as connection:
        connection.execute(
            INSERT, (received_at, kind, repo, issue, node, session_id, encoded)
        )
        connection.commit()


def _append_traverse(
    kind: str, repo: str, issue: int, payload: Mapping[str, object], db_path: Path
) -> None:
    """Append one traverse-grain row, whose `node` and `session_id` are NULL.

    Every traverse-grain writer goes through here, so the two job-grain columns
    are NULL by construction rather than by each writer remembering to pass
    nothing.
    """
    _append(kind, repo, issue, None, None, payload, db_path)


def _append_job(
    kind: str,
    repo: str,
    issue: int,
    node: str,
    session_id: str,
    payload: Mapping[str, object],
    db_path: Path,
) -> None:
    """Append one job-grain row, refusing one whose grain columns are missing.

    Both job-grain columns are load-bearing for `live_jobs`, and a NULL in
    either is worse than an error. SQL three-valued logic makes
    `report.session_id = launch.session_id` neither true nor false when both
    are NULL, so a launch written without a session id can never be closed --
    not by its own report, not by anything -- and shows as running work
    forever, with nothing raised anywhere. A launcher whose session-id minting
    returns None on some path would strand every job it starts.

    So the missing value is refused here, at the write, before it can reach a
    store nothing can repair it in. This is a caller bug and surfaces as one:
    `LedgerError` would send the operator to check a store that is perfectly
    healthy.
    """
    if node is None or session_id is None:
        raise ValueError(
            f"a {kind} needs both a node and a session id, and was given "
            f"node={node!r}, session_id={session_id!r}"
        )
    _append(kind, repo, issue, node, session_id, payload, db_path)


# --- traverse-grain writers ---


def traverse_start(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the invocation's first record, at `traverse_issue` entry."""
    _append_traverse("traverse-start", repo, issue, payload, db_path)


def phase_transition(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written beside a label move."""
    _append_traverse("phase-transition", repo, issue, payload, db_path)


def verdict(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written at a review-loop verdict point."""
    _append_traverse("verdict", repo, issue, payload, db_path)


def traverse_escalation(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written right before `traverse_issue` returns escalated."""
    _append_traverse("traverse-escalation", repo, issue, payload, db_path)


def traverse_end(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append every invocation's last record, escalated exits included.

    A traverse window closes here or at the next `traverse-start` for the same
    repo and issue — never at `traverse-escalation`, which is why an escalated
    exit still writes this.
    """
    _append_traverse("traverse-end", repo, issue, payload, db_path)


def closeout(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the issue's terminal record, at `teardown_issue`."""
    _append_traverse("closeout", repo, issue, payload, db_path)


# --- job-grain writers ---


def job_launch(
    repo: str,
    issue: int,
    node: str,
    session_id: str,
    payload: Mapping[str, object],
    *,
    db_path: Path = DB_PATH,
) -> None:
    """Append the pre-spawn record, right after the session id is minted."""
    _append_job("job-launch", repo, issue, node, session_id, payload, db_path)


def job_report(
    repo: str,
    issue: int,
    node: str,
    session_id: str,
    payload: Mapping[str, object],
    *,
    db_path: Path = DB_PATH,
) -> None:
    """Append the job's single terminal record, written as the child exits."""
    _append_job("job-report", repo, issue, node, session_id, payload, db_path)


# --- reads ---


def _select(
    query: str, filters: Mapping[str, object], db_path: Path
) -> list[LedgerRow]:
    """Run one named query and decode its rows.

    A filter left None matches everything, which each query spells out as
    `:name IS NULL OR column = :name` -- so the filters conjoin and passing
    none of them reads the whole machine.
    """
    with _ledger(db_path) as connection:
        rows = connection.execute(query, dict(filters)).fetchall()
    return [_decode(row) for row in rows]


# What a `COLUMNS` select yields, before the payload is parsed.
StoredRow = tuple[int, str, str, str, int, str | None, str | None, str]

# The two job-grain kinds. Their rows carry a node and a session id; every
# other kind is traverse-grain and carries neither.
JOB_KINDS = frozenset({"job-launch", "job-report"})

# What a stored row must carry to be readable. `repo` and `issue` key every
# supersession, window and closeout test in both queries, and a job row's
# `node` and `session_id` key the rest -- so an empty one is unmatchable under
# SQL's three-valued logic, and the row stands in every answer forever rather
# than being superseded, reported or closed out of it. `received_at` is matched
# on by nothing and is here because `LedgerRow` promises a string.
KEY_COLUMNS = ("received_at", "repo", "issue")
JOB_KEY_COLUMNS = ("node", "session_id")


def _decode(stored: StoredRow) -> LedgerRow:
    """One raw row as a `LedgerRow`, its payload text parsed back into a dict.

    A stored row this module cannot use leaves as `LedgerError` naming the row
    — the same shape as the `awaiting_merge` guard, and for the same reason. A
    caller who catches `LedgerError` to mean "the ledger is broken" would
    otherwise walk straight past a bare `json` error, or take a row that lies
    about its own contents for a sound one.

    A **payload** fails two ways, and the second is not the first: text that
    will not parse at all, and text that parses into something other than an
    object. `null`, a number and a list are all valid JSON, so they clear the
    parse and are still not the `dict` a payload is — left alone they ride out
    of here inside a `LedgerRow` that lies about its own type, and surface much
    later as a `TypeError` from whatever first treats one as a mapping. The
    sibling `measure-event` draws the same line for the same reason.

    A **promoted column** fails one way, by being empty. The writers refuse
    that at the door, so such a row got into the store some other way, and it
    is the worse failure of the two: nothing raises anywhere, because a NULL
    key simply never matches, so the row cannot be superseded, reported or
    closed out and stands in every answer for good. It is refused here instead,
    naming what it lacks, and an operator repairs the row the error names.

    The columns are unpacked positionally rather than named one by one: adding
    a column to `COLUMNS` then breaks the constructor loudly, where eight
    hand-written indices would quietly slide and hand back a `node` holding a
    session id.
    """
    try:
        payload = json.loads(stored[-1])
    except (TypeError, ValueError) as error:
        raise LedgerError(
            f"run ledger row {stored[0]} has a payload that will not decode: {error}"
        ) from error
    if not isinstance(payload, dict):
        raise LedgerError(
            f"run ledger row {stored[0]} has a payload that is not a JSON object "
            f"but a {type(payload).__name__}"
        )
    row = LedgerRow(*stored[:-1], payload=payload)
    required = KEY_COLUMNS + JOB_KEY_COLUMNS if row.kind in JOB_KINDS else KEY_COLUMNS
    missing = [name for name in required if getattr(row, name) is None]
    if missing:
        raise LedgerError(
            f"run ledger row {row.id} is a {row.kind} carrying no "
            f"{', '.join(missing)}, so no query can match it and it would stand "
            f"in every answer until the row is repaired"
        )
    return row


def live_jobs(
    *,
    repo: str | None = None,
    issue: int | None = None,
    db_path: Path = DB_PATH,
) -> list[LedgerRow]:
    """Every job still running, as the ledger's records and silences imply.

    A launch counts as live until one of three things ends it: a `job-report`
    for its session id, a later `job-launch` of the same node at the same repo
    and issue superseding it, or its traverse window closing. Filters conjoin,
    and passing none of them reads the whole machine.
    """
    return _select(LIVE_JOBS, {"repo": repo, "issue": issue}, db_path)


def awaiting_merge(
    *, repo: str | None = None, db_path: Path = DB_PATH
) -> list[LedgerRow]:
    """Every issue whose traverse ended `pr-ready` and has not been closed out.

    The one place the module reads inside a payload, and it reads exactly one
    key. That key's vocabulary is closed and stated at `STATUSES`: a candidate
    carrying anything outside it — no `status` at all, a `status` that is not a
    string, a string nobody here recognises — is a row this cannot judge, and
    it raises `LedgerError` naming that row rather than dropping it. There is
    no reading under which a launcher's `"PR-Ready"` or `"pr_ready"` quietly
    means no.

    Only candidates are judged — the newest `traverse-end` per repo and issue,
    minus the closed-out. A superseded or spent end is dead history the query
    never consults, so a malformed row that is no longer in play cannot brick
    this read; one that *is* in play stops the read until it is repaired, which
    is a direct `UPDATE` on the row the error names. Append-only is this
    module's writing discipline, not a limit on the operator.
    """
    candidates = _select(AWAITING_MERGE, {"repo": repo}, db_path)
    unjudgeable = [
        row.id for row in candidates if row.payload.get(STATUS) not in STATUSES
    ]
    if unjudgeable:
        raise LedgerError(
            f"run ledger at {db_path} has traverse-end rows whose payload "
            f"{STATUS!r} is not one of {STATUSES}: {unjudgeable}"
        )
    return [row for row in candidates if row.payload[STATUS] == PR_READY]
