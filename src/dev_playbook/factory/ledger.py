"""The software factory's append-only run ledger.

The `ledger` table sits beside the hook-capture `events` table in the same
SQLite store, and this module is the only code that touches it. Rows are
appended and never changed: state is derived by reading which records exist
and which are absent.
"""

import json
import sqlite3
from collections.abc import Callable, Iterator, Mapping
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

# The eight kinds, named once. Every query matches on one and every writer
# stamps one, so a bare literal on either side is a typo SQL answers with an
# empty result rather than an error, and no test elsewhere would notice.
TRAVERSE_START = "traverse-start"
JOB_LAUNCH = "job-launch"
JOB_REPORT = "job-report"
PHASE_TRANSITION = "phase-transition"
VERDICT = "verdict"
TRAVERSE_ESCALATION = "traverse-escalation"
TRAVERSE_END = "traverse-end"
CLOSEOUT = "closeout"

# The two job-grain kinds. Their rows carry a node and a session id; every
# other kind is traverse-grain and carries neither.
JOB_KINDS = frozenset({JOB_LAUNCH, JOB_REPORT})

# A traverse window opens at `traverse-start` and closes at the first of these
# to land for the same repo and issue: the `traverse-end` that every
# `traverse_issue` exit writes as its last record, the next `traverse-start`
# when a traverse died before writing one, or the `closeout` that makes the
# issue terminal.
#
# `traverse-escalation` is deliberately not among them: an escalated exit still
# writes `traverse-end` afterwards, and that is what closes the window (epic
# standing ruling 4).
WINDOW_CLOSERS = (TRAVERSE_END, TRAVERSE_START, CLOSEOUT)


def _quoted(values: tuple[str, ...]) -> str:
    """One of this module's vocabularies as a SQL literal list, for an `IN`."""
    return ", ".join(f"'{value}'" for value in values)


def _window_still_open(row: str) -> str:
    """The condition that nothing has closed this row's window since it landed.

    Both reads ask this of their own row and neither may answer it differently:
    a job is live only inside an open window, and a `traverse-end` speaks for
    its issue only until its own window shuts. So the rule is written once here
    and interpolated into both queries rather than spelled out by hand in each.
    Spelled twice it drifted, and the two reads then disagreed about one issue
    at one instant -- `awaiting_merge` calling it ready to merge while
    `live_jobs` showed a build rewriting its branch.
    """
    return f"""NOT EXISTS (
      SELECT 1 FROM ledger AS closer
      WHERE closer.kind IN ({_quoted(WINDOW_CLOSERS)})
        AND closer.repo = {row}.repo
        AND closer.issue = {row}.issue
        AND closer.id > {row}.id
  )"""


# A job is live while it has been launched and nothing has since ended it: no
# report for its session, no newer launch of the same node taking its place,
# and its traverse window still open.
LIVE_JOBS = f"""
SELECT {COLUMNS} FROM ledger AS l
WHERE l.kind = '{JOB_LAUNCH}'
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS reported
      WHERE reported.kind = '{JOB_REPORT}'
        AND reported.session_id = l.session_id
        AND reported.id > l.id
  )
  AND NOT EXISTS (
      SELECT 1 FROM ledger AS relaunched
      WHERE relaunched.kind = '{JOB_LAUNCH}'
        AND relaunched.repo = l.repo
        AND relaunched.issue = l.issue
        AND relaunched.node = l.node
        AND relaunched.id > l.id
  )
  AND {_window_still_open("l")}
  AND (:repo IS NULL OR l.repo = :repo)
  AND (:issue IS NULL OR l.issue = :issue)
ORDER BY l.id
"""

# The rows `awaiting_merge` is about to match: every `traverse-end` whose own
# window is still open, by `WINDOW_CLOSERS`. What an end outside its window
# said is dead history this never consults, so it can never brick the read
# with a malformed payload.
AWAITING_MERGE = f"""
SELECT {COLUMNS} FROM ledger AS l
WHERE l.kind = '{TRAVERSE_END}'
  AND {_window_still_open("l")}
  AND (:repo IS NULL OR l.repo = :repo)
ORDER BY l.id
"""

# The session ids more than one job holds. A session id is a job's identity --
# it is what a report closes its own launch by, and what joins the job to its
# rows in `events` -- so two jobs holding one is corrupt data no query can be
# written around: a report for either would retire both, and the join would
# answer with the wrong issue.
#
# `IS NOT` rather than `<>` so a NULL in an address column counts as different
# rather than as unknown; SQL's three-valued logic would otherwise let the one
# row a query can never match hide the collision as well.
COLLIDING_SESSIONS = """
SELECT l.session_id, group_concat(DISTINCT l.id)
FROM ledger AS l
JOIN ledger AS other ON other.session_id = l.session_id
WHERE l.session_id IS NOT NULL
  AND (
      other.repo IS NOT l.repo
      OR other.issue IS NOT l.issue
      OR other.node IS NOT l.node
  )
GROUP BY l.session_id
ORDER BY l.session_id
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


def _names(value: object) -> bool:
    """A repo slug, node or session id: a string with something in it."""
    return isinstance(value, str) and value != ""


def _numbers(value: object) -> bool:
    """A GitHub issue number: a whole positive `int`, and `bool` is not one."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


# The whole addressing rule, in one place. Every public call passes its address
# through `_gate` before anything else happens, so nothing below the gate
# re-checks an address: past it, the address is trusted.
#
# `repo`, `node` and `session_id` name things, and a name that is missing or
# empty breaks its row two ways. A NULL is unmatchable under SQL's three-valued
# logic, so the row can never be superseded, reported or closed out and stands
# in every answer for good. An empty string is worse company: it *does* match,
# so every caller that gets it wrong lands on one shared address and supersedes
# work it has nothing to do with.
#
# `issue` is what GitHub issues, and GitHub numbers issues from 1 -- so zero and
# negatives are not issue numbers and never arrive from live data. Type is
# checked as strictly as value, because SQLite's INTEGER affinity converts what
# looks numeric and stores the rest as it came: `"0"` lands on the zero address,
# `True` addresses issue #1 by subclassing `int`, and `"main"` sits in a column
# `LedgerRow` promises is an `int`.
ADDRESSES: dict[str, Callable[[object], bool]] = {
    "repo": _names,
    "issue": _numbers,
    "node": _names,
    "session_id": _names,
}


def _gate(**address: object) -> None:
    """Refuse an address the ledger cannot use, before the store is touched.

    A caller bug, raised as `ValueError` rather than `LedgerError`: the store is
    fine, and telling the operator otherwise would send them to check a disk
    that is not the problem.
    """
    unusable = [
        f"{name}={value!r}"
        for name, value in address.items()
        if not ADDRESSES[name](value)
    ]
    if unusable:
        raise ValueError(
            f"the run ledger cannot be addressed by {', '.join(unusable)}: a repo, "
            f"node and session id are each a non-empty string, and an issue is a "
            f"positive whole number"
        )


def _given(**address: object) -> dict[str, object]:
    """A read's filters, less the ones it left unset.

    The one difference between a read's address and a write's: `None` here is
    the caller declining to filter rather than a value, so it is what the gate
    never sees. Everything it does see, it judges by the one rule above.
    """
    return {name: value for name, value in address.items() if value is not None}


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

    Four kinds of trouble raise it:

    - A **storage failure** — the store unwritable, connect, the DDL, an INSERT
      or SELECT, a busy timeout expiring — chained from the `sqlite3.Error` or
      `OSError` beneath it.
    - A **store that will not take WAL**, unchained: there is no underlying
      error, because SQLite reports a declined journal mode by returning the
      one it kept.
    - A **stored row this module cannot use**, naming the row id: a payload
      that will not decode (chained from the decode error), a payload that
      decodes into something other than a JSON object, a promoted column that
      is empty or holds a type the queries cannot address by, or a `traverse-end`
      candidate whose payload carries no `status` from the closed vocabulary
      at `STATUSES`. Only the first of these has an error to chain from; the
      rest are the store disagreeing with itself, not an operation failing.
    - **Stored rows this module cannot tell apart**, naming them: one session
      id held by more than one job, which no read can resolve because a session
      id is what a job is addressed and joined by.

    A caller's own bug is deliberately none of these — telling the operator
    their store is unusable would send them to check a disk that is fine. Each
    surfaces as itself, with nothing written: a payload that will not serialize
    raises `TypeError`, an address `_gate` refuses raises `ValueError`, and a
    column argument SQLite cannot bind raises `sqlite3.ProgrammingError` or
    `sqlite3.InterfaceError`.
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

    Storage plumbing, and nothing else: the address arrives already judged by
    `_gate`, one level up.

    The payload is encoded before the store is touched, so a payload that will
    not serialize raises with nothing written.

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
    nothing, and the gate is the first thing each of them reaches.
    """
    _gate(repo=repo, issue=issue)
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
    """Append one job-grain row, which carries all four address columns.

    Every job-grain writer goes through here, so the gate judges the whole
    address — the two columns the traverse grain leaves NULL included.
    """
    _gate(repo=repo, issue=issue, node=node, session_id=session_id)
    _append(kind, repo, issue, node, session_id, payload, db_path)


# --- traverse-grain writers ---


def traverse_start(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the invocation's first record, at `traverse_issue` entry."""
    _append_traverse(TRAVERSE_START, repo, issue, payload, db_path)


def phase_transition(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written beside a label move."""
    _append_traverse(PHASE_TRANSITION, repo, issue, payload, db_path)


def verdict(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written at a review-loop verdict point."""
    _append_traverse(VERDICT, repo, issue, payload, db_path)


def traverse_escalation(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the record written right before `traverse_issue` returns escalated."""
    _append_traverse(TRAVERSE_ESCALATION, repo, issue, payload, db_path)


def traverse_end(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append every invocation's last record, escalated exits included.

    This is one of `WINDOW_CLOSERS`, which is why an escalated exit still
    writes it.
    """
    _append_traverse(TRAVERSE_END, repo, issue, payload, db_path)


def closeout(
    repo: str, issue: int, payload: Mapping[str, object], *, db_path: Path = DB_PATH
) -> None:
    """Append the issue's terminal record, at `teardown_issue`."""
    _append_traverse(CLOSEOUT, repo, issue, payload, db_path)


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
    _append_job(JOB_LAUNCH, repo, issue, node, session_id, payload, db_path)


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
    _append_job(JOB_REPORT, repo, issue, node, session_id, payload, db_path)


# --- reads ---


def _select(
    connection: sqlite3.Connection, query: str, filters: Mapping[str, object]
) -> list[LedgerRow]:
    """Run one named query on an open ledger and decode its rows.

    The connection is passed in rather than opened here so that a read and the
    guards it runs alongside see one snapshot of the store: opened separately
    they would not, and a write landing between them could slip past a guard
    into the answer it was meant to hold back.

    A filter left None matches everything, which each query spells out as
    `:name IS NULL OR column = :name` -- so the filters conjoin and passing
    none of them reads the whole machine.
    """
    return [_decode(row) for row in connection.execute(query, dict(filters))]


# What a `COLUMNS` select yields, before the payload is parsed.
StoredRow = tuple[int, str, str, str, int, str | None, str | None, str]

# What each promoted column must hold for a row to be readable. `repo` and
# `issue` key every supersession, window and closeout test in both queries, and
# a job row's `node` and `session_id` key the rest -- so a column holding
# nothing is unmatchable under SQL's three-valued logic and the row stands in
# every answer forever, while one holding the wrong type reaches a caller
# inside a `LedgerRow` that lies about itself. `received_at` is matched on by
# nothing and is here because `LedgerRow` promises a string.
COLUMN_TYPES: dict[str, type] = {
    "id": int,
    "received_at": str,
    "kind": str,
    "repo": str,
    "issue": int,
}

# The grain columns, by the kind that carries them. A traverse row's `None`s
# are its shape rather than something it lacks, so they are stated as the type
# they are instead of being left unchecked.
JOB_GRAIN_TYPES: dict[str, type] = {"node": str, "session_id": str}
TRAVERSE_GRAIN_TYPES: dict[str, type] = {"node": type(None), "session_id": type(None)}


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

    A **promoted column** fails two ways of its own, being empty or holding the
    wrong type, and both are worse than the payload's pair: nothing raises
    anywhere. A NULL key never matches, so the row cannot be superseded,
    reported or closed out and stands in every answer for good; and SQLite's
    column affinities convert only what already looks like the declared type,
    so an issue number that arrived as a branch name is stored and handed back
    as text. Each is refused here instead, naming the row and the column, and
    an operator repairs what the error names.

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
    grain = JOB_GRAIN_TYPES if row.kind in JOB_KINDS else TRAVERSE_GRAIN_TYPES
    unusable = [
        f"{name} holds {getattr(row, name)!r} where a {wanted.__name__} belongs"
        for name, wanted in (COLUMN_TYPES | grain).items()
        if not isinstance(getattr(row, name), wanted)
    ]
    if unusable:
        raise LedgerError(
            f"run ledger row {row.id} is a {row.kind} the queries cannot address: "
            f"{'; '.join(unusable)}. Repair the row before reading again."
        )
    return row


def _refuse_colliding_sessions(connection: sqlite3.Connection, db_path: Path) -> None:
    """Refuse a store where one session id stands for more than one job.

    Read whole rather than filtered: a session id is minted once and belongs to
    one job for the life of the store, so a collision is never dead history the
    way a superseded `traverse-end` is. It stops the read until an operator
    repairs the rows the error names, which is the ordered behaviour -- a
    launcher whose session-id minting collides or is retried is writing work
    the factory can no longer tell apart, and finding that out late is worse
    than finding it out here.
    """
    collisions = connection.execute(COLLIDING_SESSIONS).fetchall()
    if collisions:
        held = ", ".join(f"{session!r} on rows {ids}" for session, ids in collisions)
        raise LedgerError(
            f"run ledger at {db_path} has session ids held by more than one job, "
            f"so no read can tell those jobs apart: {held}"
        )


def live_jobs(
    *,
    repo: str | None = None,
    issue: int | None = None,
    db_path: Path = DB_PATH,
) -> list[LedgerRow]:
    """Every job still running, as the ledger's records and silences imply.

    A launch counts as live until one of three things ends it: a `job-report`
    for its session id, a later `job-launch` of the same node at the same repo
    and issue superseding it, or its traverse window closing — at
    `WINDOW_CLOSERS`, the one definition `awaiting_merge` reads by too. Filters
    conjoin, and passing none of them reads the whole machine; a filter that is
    set is an address, judged by the gate the writers pass through.

    A report is matched by session id alone, which is sound only while a
    session id names one job — so that is checked rather than assumed, and a
    store where two jobs hold one raises `LedgerError` before any answer is
    given. The alternative is the answer nobody can see is wrong: a report
    retiring a job it was never about, and the launcher's collision surfacing
    as work that finished without ever stopping.
    """
    _gate(**_given(repo=repo, issue=issue))
    with _ledger(db_path) as connection:
        _refuse_colliding_sessions(connection, db_path)
        return _select(connection, LIVE_JOBS, {"repo": repo, "issue": issue})


def awaiting_merge(
    *, repo: str | None = None, db_path: Path = DB_PATH
) -> list[LedgerRow]:
    """Every issue whose traverse ended `pr-ready` and has not moved on since.

    An end speaks for its issue only while its own window is open, by the one
    definition at `WINDOW_CLOSERS` that `live_jobs` reads by too — so an issue
    back in the factory for rework never reads as ready to merge while a build
    is rewriting its branch.

    The one place the module reads inside a payload, and it reads exactly one
    key. That key's vocabulary is closed and stated at `STATUSES`: a candidate
    carrying anything outside it — no `status` at all, a `status` that is not a
    string, a string nobody here recognises — is a row this cannot judge, and
    it raises `LedgerError` naming that row rather than dropping it. There is
    no reading under which a launcher's `"PR-Ready"` or `"pr_ready"` quietly
    means no.

    Only candidates are judged — the ends whose windows are still open. An end
    that has been superseded, spent or reopened past is dead history the query
    never consults, so a malformed row that is no longer in play cannot brick
    this read; one that *is* in play stops the read until it is repaired, which
    is a direct `UPDATE` on the row the error names. Append-only is this
    module's writing discipline, not a limit on the operator.
    """
    _gate(**_given(repo=repo))
    with _ledger(db_path) as connection:
        candidates = _select(connection, AWAITING_MERGE, {"repo": repo})
    unjudgeable = [
        row.id for row in candidates if row.payload.get(STATUS) not in STATUSES
    ]
    if unjudgeable:
        raise LedgerError(
            f"run ledger at {db_path} has {TRAVERSE_END} rows whose payload "
            f"{STATUS!r} is not one of {STATUSES}: {unjudgeable}"
        )
    return [row for row in candidates if row.payload[STATUS] == PR_READY]
