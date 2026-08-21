"""The software factory's append-only run ledger.

The `ledger` table sits beside the hook-capture `events` table in the same
SQLite store, and this module is the only code that touches it. Rows are
appended and never changed: state is derived by reading which records exist
and which are absent.
"""

import json
import signal
import sqlite3
from collections.abc import Callable, Iterator, Mapping
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

DB_PATH = Path("~/.local/share/claude-measure/events.db").expanduser()

# The signals whose handlers write to this ledger, held off for the length of
# every write. A traverse traps exactly these two and writes the books from the
# trap -- `traverse.TRAPPED` is this tuple, so the pair cannot drift into a
# signal that is trapped here and not deferred there.
#
# The invariant that makes holding them off work: **every thread any process
# writing to this ledger starts must block these two.** Blocking them on the
# writing thread alone is not enough -- CPython runs the C handler on whichever
# thread the kernel picks and the main thread then runs the Python handler at
# its next bytecode boundary regardless of its own mask, so one unblocked
# thread anywhere is a route back into the write. `launcher._pump` is the one
# thread this system starts, and it blocks them on entry.
DEFERRED_SIGNALS = (signal.SIGINT, signal.SIGTERM)

# Concurrent traverses write to one database. WAL lets their readers and
# writers coexist, and the busy timeout makes a collision queue rather than
# fail.
BUSY_TIMEOUT_SECONDS = 5.0

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
# said is dead history this never consults.
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
# status the traverse exited with, and those are the three terminal statuses the
# graph has. `traverse_end` refuses anything else at the door, so adding a
# terminal status is an edit here -- which is the point: the ledger is where a
# launcher's typo surfaces, and it surfaces at the write.
#
# `killed` is the one no `traverse_issue` return carries. It is written from the
# kill trap, where the traverse is being taken down mid-flight and no value can
# be returned to anyone -- and it has to be in the vocabulary, because a trap
# whose last write raises leaves the window open and every job of that issue
# reading as live for good. It closes a window like any other end and is never
# `pr-ready`, so `awaiting_merge` passes over it without a clause of its own.
#
# A tuple, not a set: membership on a tuple compares rather than hashes, so an
# unhashable status -- a list, an object -- is judged unrecognised instead of
# raising `TypeError` out of the gate meant to catch it.
STATUS = "status"
PR_READY = "pr-ready"
ESCALATED = "escalated"
KILLED = "killed"
STATUSES = (PR_READY, ESCALATED, KILLED)


def _names(value: object) -> bool:
    """A repo slug, node or session id: a string with something in it."""
    return isinstance(value, str) and value != ""


def _numbers(value: object) -> bool:
    """A GitHub issue number: a whole positive `int`, and `bool` is not one."""
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


# The whole addressing rule, in one place: `_gate` judges every address a
# public call hands in, and nothing below it re-checks one.
#
# A name that is missing or empty breaks its row two ways. A NULL is unmatchable
# under SQL's three-valued logic, so the row can never be superseded, reported
# or closed out and stands in every answer for good. An empty string is worse
# company: it *does* match, so every caller that gets it wrong lands on one
# shared address and supersedes work it has nothing to do with.
#
# An issue number is judged as strictly on type as on value, because SQLite's
# INTEGER affinity converts what looks numeric and stores the rest as it came:
# `"0"` lands on the zero address, `True` addresses issue #1 by subclassing
# `int`, and `"main"` sits in a column `LedgerRow` promises is an `int`. Zero
# and negatives are barred because GitHub numbers issues from 1.
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


def _gate_status(payload: Mapping[str, object]) -> None:
    """Refuse a `traverse-end` carrying a status the graph never exits on.

    Beside the address gate, and for the same reason: a traverse ends on one of
    `STATUSES` and nothing else, so a payload carrying anything outside that is
    a launcher's typo. It is a caller bug, raised as `ValueError` and before the
    store is touched, so nothing is written.

    This is the only writer of a `traverse-end`, and judging a status needs no
    sight of any other row -- so the judgment belongs here, where the caller who
    got it wrong is still on the stack. Made at the read instead it would arrive
    as a stored row nobody can attribute, long after the caller that wrote it
    has gone. `awaiting_merge` reads the key with no guard of its own
    because of this: a row that got past here carries a status it recognises.
    """
    if STATUS not in payload:
        raise ValueError(
            f"the run ledger cannot record a {TRAVERSE_END} with no {STATUS!r} in "
            f"its payload: a traverse ends on one of {STATUSES}"
        )
    status = payload[STATUS]
    if status not in STATUSES:
        raise ValueError(
            f"the run ledger cannot record a {TRAVERSE_END} whose {STATUS} is "
            f"{status!r}: a traverse ends on one of {STATUSES}"
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
    - A **stored payload this module cannot use**, naming the row id: text
      that will not decode at all (chained from the decode error), and text
      that decodes into something other than a JSON object (unchained — the
      store disagreeing with itself, not an operation failing).
    - **Stored rows this module cannot tell apart**, naming them: one session
      id held by more than one job, which no read can resolve because a session
      id is what a job is addressed and joined by.

    A caller's own bug is deliberately none of these — telling the operator
    their store is unusable would send them to check a disk that is fine. Each
    surfaces as itself, with nothing written: a payload that will not serialize
    raises `TypeError`, an address or a `traverse-end` status the gates refuse
    raises `ValueError`, and a column argument SQLite cannot bind raises
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
    changes anything; every later one reads back the mode already set. The mode
    comes back lowercase whatever case the pragma asked in, which is the one
    thing worth knowing about the comparison below.
    """
    (mode,) = connection.execute("PRAGMA journal_mode=WAL").fetchone()
    if mode != "wal":
        raise LedgerError(
            f"run ledger at {db_path} would not take WAL journal mode and is in "
            f"{mode!r} mode, so concurrent traverses would collide"
        )


@contextmanager
def _uninterrupted() -> Iterator[None]:
    """Hold the deferred signals off for the length of the block.

    Python runs a signal handler on the main thread at an arbitrary bytecode
    boundary, so without this one can land in the middle of a write -- and a
    traverse's handler writes to this ledger. Its own INSERT would then queue
    behind a write lock only the thread it interrupted can release, wait out
    `BUSY_TIMEOUT_SECONDS`, and leave as `LedgerError` from inside a handler:
    the `killed` end never lands, and the window it exists to close stays open
    for good.

    The whole mask is restored rather than the two signals unblocked, so a
    write reached from inside a block that already blocked them -- the trap's
    own sweep is one -- leaves them blocked on the way out.
    """
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, DEFERRED_SIGNALS)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


@contextmanager
def _ledger(db_path: Path) -> Iterator[sqlite3.Connection]:
    """The store, open in one transaction, table present, WAL on, timeout set.

    The `BEGIN` is what makes the block one snapshot; one connection is not.
    `sqlite3` opens a transaction only ahead of DML, so consecutive `SELECT`s
    here would otherwise be separate autocommit reads — which is how a colliding
    `job-launch` slipped past `live_jobs`'s collision guard into the answer that
    guard exists to hold back. It is deferred, so it takes no lock of its own
    and a writer's `INSERT` still queues on the busy timeout, and it opens after
    the DDL, which commits in autocommit, so a read still creates the store it
    finds absent.

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
            connection.execute("BEGIN")
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

    The two deferred signals are held off for the length of the write, which is
    what keeps a trap that writes the books out of the middle of one -- see
    `_uninterrupted`. The encoding happens outside that hold, because it is not
    the transaction and a signal is free to land there.

    The payload is encoded before the store is touched, so a payload that will
    not serialize raises with nothing written. `allow_nan=False` puts a NaN or
    an infinity in that class: `json.dumps` would otherwise write them as bare
    tokens no JSON parser accepts, and SQLite's `json_valid` reads the row back
    as invalid -- an unqueryable payload in the one column `_gate` cannot judge.

    `json.dumps` serializes `dict` alone, not the `Mapping` protocol, so the
    payload is copied into one first — otherwise the most natural immutable
    payloads, a `MappingProxyType` or a `ChainMap`, would be refused as
    unserializable despite being nothing of the sort.
    """
    encoded = json.dumps(dict(payload), allow_nan=False)
    received_at = datetime.now(UTC).isoformat(timespec="microseconds")
    with _uninterrupted(), _ledger(db_path) as connection:
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

    A `traverse-end` is gated on its payload as well, because it is the one kind
    whose payload this module reads back. The address is judged first either
    way, so a call that gets both wrong is told about the address it is filed
    under before the status it carries.
    """
    _gate(repo=repo, issue=issue)
    if kind == TRAVERSE_END:
        _gate_status(payload)
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
    guards it runs alongside run inside the one transaction `_ledger` holds —
    see there for why a shared connection alone would not have been enough.

    A filter left None matches everything, which each query spells out as
    `:name IS NULL OR column = :name` -- so the filters conjoin and passing
    none of them reads the whole machine.
    """
    return [_decode(row) for row in connection.execute(query, dict(filters))]


# What a `COLUMNS` select yields, before the payload is parsed.
StoredRow = tuple[int, str, str, str, int, str | None, str | None, str]


def _decode(stored: StoredRow) -> LedgerRow:
    """One raw row as a `LedgerRow`, its payload text parsed back into a dict.

    A **payload** fails two ways, and the second is not the first: text that
    will not parse at all, and text that parses into something other than an
    object. `null`, a number and a list are all valid JSON, so they clear the
    parse and are still not the `dict` a payload is — left alone they ride out
    of here inside a `LedgerRow` that lies about its own type, and surface much
    later as a `TypeError` from whatever first treats one as a mapping. The
    sibling `measure-event` draws the same line for the same reason. Both leave
    as `LedgerError` naming the row, so a caller who catches that to mean "the
    ledger is broken" does not walk straight past a bare `json` error.

    The promoted columns are taken as they come. `_gate` judges every address
    on the way in and no writer here can get past it, so a stored row with an
    empty or wrong-typed `repo`, `issue`, `node` or `session_id` is not
    something this module can produce -- and policing a store nothing else
    writes to is a check that can only ever fire on a row placed by hand.

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
    return LedgerRow(*stored[:-1], payload=payload)


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
    key. It judges nothing: `traverse_end` is the sole writer of these rows and
    demands a status from the closed vocabulary at `STATUSES` before it writes
    one, so every row that reaches here already carries a status this
    recognises. A launcher's `"PR-Ready"` or `"pr_ready"` never gets this far.
    """
    _gate(**_given(repo=repo))
    with _ledger(db_path) as connection:
        candidates = _select(connection, AWAITING_MERGE, {"repo": repo})
    return [row for row in candidates if row.payload[STATUS] == PR_READY]
