import inspect
import json
import signal
import sqlite3
import time
import uuid
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

from dev_playbook.factory import ledger

COLUMNS = "id, received_at, kind, repo, issue, node, session_id, payload"

# Long enough that the contended write is genuinely blocked when it starts,
# short enough to sit well inside the module's busy timeout.
LOCK_HOLD_SECONDS = 0.25

# The hook-capture table the ledger sits beside, as `measure-event` creates it.
# Stood up here so the join below is exercised against the real column, not a
# stand-in for it.
EVENTS_SCHEMA = """
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    received_at TEXT,
    event TEXT,
    session_id TEXT,
    prompt_id TEXT,
    payload TEXT
)
"""

INSERT_EVENT = "INSERT INTO events (event, session_id) VALUES ('SessionStart', ?)"

JOIN_ON_SESSION_ID = """
SELECT l.repo, l.issue, l.node
FROM ledger AS l
JOIN events AS e ON l.session_id = e.session_id
WHERE l.kind = 'job-launch'
"""

# JSON a payload column can hold that is valid and still not a payload: the
# module annotates `LedgerRow.payload` as a dict, so anything else is a stored
# row it cannot use.
NOT_JSON_OBJECTS = ["null", "123", "true", "[1, 2]", '"pr-ready"']

# A `status` outside the module's closed vocabulary because it is not a string
# at all. The unhashable two are the reason the vocabulary is a tuple: a set
# would raise `TypeError` out of the gate meant to catch them.
NOT_STATUS_STRINGS: list[Any] = [1, None, True, ["pr-ready"], {"value": "pr-ready"}]

# What `traverse_end` refuses at the door: a payload with no `status` in it, one
# whose `status` is not a string, and one whose `status` is a string the graph
# never exits on -- the near-misses a launcher actually writes.
REFUSED_TRAVERSE_END_PAYLOADS: list[dict[str, Any]] = [
    {},
    {"note": "no status here"},
    *({"status": status} for status in NOT_STATUS_STRINGS),
    {"status": "pr_ready"},
    {"status": "PR-Ready"},
    {"status": ""},
]

# A second job whose address differs from `("owner/one", 1, "build")` in one
# column each -- the three ways a reused session id can span two jobs.
COLLIDING_JOBS = [
    ("owner/two", 1, "build"),
    ("owner/one", 2, "build"),
    ("owner/one", 1, "doc-pr-review"),
]

# A branch name where an issue number belongs. Typed loosely so the deliberate
# misuse is the test's subject rather than a type error.
NOT_AN_ISSUE_NUMBER: Any = "main"

# What the gate refuses in a column that names something -- a repo slug, a node,
# a session id. `None` strands the row it addresses, because a NULL matches
# nothing under SQL's three-valued logic; `""` is worse company, because it
# matches every other caller that got it equally wrong; and a value that is not
# a string at all lands in a column the queries and `LedgerRow` read as text.
REFUSED_FILTER_NAMES: list[Any] = ["", 438, uuid.UUID(int=1)]
REFUSED_NAMES: list[Any] = [None, *REFUSED_FILTER_NAMES]

# What it refuses in an issue number. GitHub numbers issues from 1, so 0 and
# negatives never arrive from live data; `"0"` is truthy and SQLite's INTEGER
# affinity then stores it on the zero address; `True` is an `int` subclass that
# silently addresses issue #1; and a float or a branch name is not the `int`
# `LedgerRow` promises.
REFUSED_FILTER_ISSUES: list[Any] = [0, "0", -1, True, 1.5, NOT_AN_ISSUE_NUMBER]
REFUSED_ISSUES: list[Any] = [None, *REFUSED_FILTER_ISSUES]

REFUSED_TRAVERSE_ADDRESSES: list[tuple[Any, Any]] = [
    *((repo, 438) for repo in REFUSED_NAMES),
    *(("owner/repo", issue) for issue in REFUSED_ISSUES),
]

REFUSED_JOB_ADDRESSES: list[tuple[Any, Any, Any, Any]] = [
    *((repo, 438, "build", "sess-1") for repo in REFUSED_NAMES),
    *(("owner/repo", issue, "build", "sess-1") for issue in REFUSED_ISSUES),
    *(("owner/repo", 438, node, "sess-1") for node in REFUSED_NAMES),
    *(("owner/repo", 438, "build", session) for session in REFUSED_NAMES),
]

# What the reads refuse in a filter. `None` is absent from these two lists: on a
# read it means "no filter" rather than an address, so it is the one value the
# gate never judges.
REFUSED_FILTERS: list[dict[str, Any]] = [
    *({"repo": repo} for repo in REFUSED_FILTER_NAMES),
    *({"issue": issue} for issue in REFUSED_FILTER_ISSUES),
]

TraverseWriter = Callable[..., None]

TRAVERSE_WRITERS: list[tuple[str, TraverseWriter]] = [
    ("traverse-start", ledger.traverse_start),
    ("phase-transition", ledger.phase_transition),
    ("verdict", ledger.verdict),
    ("traverse-escalation", ledger.traverse_escalation),
    ("traverse-end", ledger.traverse_end),
    ("closeout", ledger.closeout),
]

JobWriter = Callable[..., None]

JOB_WRITERS: list[tuple[str, JobWriter]] = [
    ("job-launch", ledger.job_launch),
    ("job-report", ledger.job_report),
]


def repoint_db_path_defaults(
    monkeypatch: pytest.MonkeyPatch, namespace: Mapping[str, object], elsewhere: Path
) -> None:
    """Aim every bound `db_path` default in `namespace` at `elsewhere`.

    By search rather than by list, so a public function added later is covered
    without anyone remembering to come back here.

    A bound default sits in one of two places depending on how the parameter
    was spelled -- `__kwdefaults__` when it is keyword-only, `__defaults__`
    when it is not -- and both are searched. Reading one dunder covers only the
    spelling the module happens to use today, which is a net with a hole in it:
    how a later function writes its own signature is not something this fixture
    gets to decide.

    `__defaults__` is a tuple with no names in it, so the parameters carrying a
    default are read off the signature in the same order to find which slot
    `db_path` occupies.
    """
    for entry in namespace.values():
        keyword_only = getattr(entry, "__kwdefaults__", None)
        if keyword_only and "db_path" in keyword_only:
            monkeypatch.setitem(keyword_only, "db_path", elsewhere)
        positional = getattr(entry, "__defaults__", None)
        if not positional or not callable(entry):
            continue
        named = [
            name
            for name, parameter in inspect.signature(entry).parameters.items()
            if parameter.default is not inspect.Parameter.empty
            and parameter.kind is not inspect.Parameter.KEYWORD_ONLY
        ]
        if "db_path" in named:
            monkeypatch.setattr(
                entry,
                "__defaults__",
                tuple(
                    elsewhere if name == "db_path" else default
                    for name, default in zip(named, positional, strict=True)
                ),
            )


@pytest.fixture(autouse=True)
def never_the_real_store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Repoint the module's default store into the temp tree, for every test.

    `DB_PATH` is the default on all ten public functions, so one omitted
    `db_path=` would otherwise append to the developer's real ledger. Autouse
    makes "nothing touches the real store" enforced rather than remembered.

    A default is bound once, at import, so repointing the module attribute
    alone leaves every one of those functions still aimed at the real ledger —
    it reads as a safety net and catches nothing. The bound defaults are
    repointed as well.
    """
    elsewhere = tmp_path / "default" / "events.db"
    monkeypatch.setattr(ledger, "DB_PATH", elsewhere)
    repoint_db_path_defaults(monkeypatch, vars(ledger), elsewhere)


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """The temp store a test writes to and reads back."""
    return tmp_path / "events.db"


def in_memory_store() -> sqlite3.Connection:
    """A connection to a store that refuses WAL, as a network mount would.

    SQLite keeps `memory` journal mode whatever `PRAGMA journal_mode=WAL`
    asks for, which is the refusal the module has to notice. No temp
    filesystem here reproduces it, so this stands in for the mount that
    would.
    """
    return sqlite3.Connection(":memory:")


def rot_the_stored_payload(db_path: Path, payload: str | None) -> None:
    """Damage the payload of the ledger's only row, behind the module's back.

    The module only ever INSERTs, so this stands in for a row that reached
    the store intact and rotted there — the hazard the module must report
    rather than crash past.
    """
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute("UPDATE ledger SET payload = ?", (payload,))
        connection.commit()


# A fragment of the `live_jobs` query and of nothing else, so a trace callback
# can tell that statement from the collision guard that runs ahead of it.
LIVE_JOBS_FRAGMENT = "relaunched"

# A second job landing on `sess-1`, written as raw SQL because the gate refuses
# to write one and the module's own writers are not the subject here.
COLLIDING_LAUNCH = (
    "INSERT INTO ledger (received_at, kind, repo, issue, node, session_id, payload) "
    "VALUES ('2026-08-20T00:00:00.000000+00:00', 'job-launch', 'owner/two', 2, "
    "'build', 'sess-1', '{}')"
)


def connect_colliding_between_the_guard_and_the_query(
    db_path: Path,
) -> tuple[Callable[..., sqlite3.Connection], list[str]]:
    """Real connections, one of which commits a colliding launch mid-read.

    The commit lands just before the `live_jobs` query itself — after the
    collision guard has run and passed — which is the window a held transaction
    closes and a shared connection does not. A trace callback on the module's
    own connection puts it there, with none of the timing a second thread and a
    barrier would need.

    The list of statements still waiting to fire is handed back with the
    connections, because the trigger is a fragment of the query matched by
    string: rename the alias it keys off and the callback stops firing, and a
    test that only looked at the answer would go on passing over a collision
    that never happened. Emptying that list is what says the window was hit.
    """
    connect: Callable[..., sqlite3.Connection] = sqlite3.connect
    pending = [COLLIDING_LAUNCH]

    def trace(statement: str) -> None:
        if pending and LIVE_JOBS_FRAGMENT in statement:
            with closing(connect(db_path)) as other:
                other.execute(pending.pop())
                other.commit()

    def connecting(*args: Any, **kwargs: Any) -> sqlite3.Connection:
        connection = connect(*args, **kwargs)
        connection.set_trace_callback(trace)
        return connection

    return connecting, pending


def raw_rows(db_path: Path) -> list[sqlite3.Row]:
    """Every ledger row, oldest first, read outside the module.

    Rows come back keyed by column name, so an assertion says `row["kind"]`
    rather than `row[2]`, and a failure reports which column disagreed instead
    of leaving the reader to count along `COLUMNS`.
    """
    with closing(sqlite3.connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            f"SELECT {COLUMNS} FROM ledger ORDER BY id"
        ).fetchall()


def test_traverse_start_appends_one_row(tmp_path: Path) -> None:
    db_path = tmp_path / "store" / "events.db"

    ledger.traverse_start("owner/repo", 438, {"mode": "direct"}, db_path=db_path)

    assert [tuple(row)[2:] for row in raw_rows(db_path)] == [
        ("traverse-start", "owner/repo", 438, None, None, '{"mode": "direct"}')
    ]


@pytest.mark.parametrize(("kind", "write"), TRAVERSE_WRITERS)
def test_a_traverse_writer_stores_its_kind_null_grain_and_payload(
    kind: str, write: TraverseWriter, db_path: Path
) -> None:
    """The `status` rides along because `traverse_end` demands one at the door.

    The other five writers interpret no payload key at all, so it passes
    straight through them as any other value would.
    """
    payload = {"note": kind, "status": "pr-ready"}

    write("owner/repo", 438, payload, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert (row["kind"], row["node"], row["session_id"]) == (kind, None, None)
    assert json.loads(row["payload"]) == payload


def store_by_positional_default(repo: str, db_path: Path = ledger.DB_PATH) -> Path:
    """A `db_path` default written without the `*` that makes it keyword-only.

    Stands in for the public function nobody has written yet. All ten in the
    module today are keyword-only, so nothing there exercises the other half of
    the search -- and no rule in the module or the standards bars this
    spelling, so the net has to hold the day one arrives.
    """
    return db_path


def test_the_real_store_net_repoints_a_db_path_that_is_not_keyword_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    elsewhere = tmp_path / "elsewhere" / "events.db"

    repoint_db_path_defaults(
        monkeypatch,
        {"store_by_positional_default": store_by_positional_default},
        elsewhere,
    )

    assert store_by_positional_default("owner/repo") == elsewhere


def test_a_call_that_omits_db_path_stays_out_of_the_real_store() -> None:
    """The autouse fixture's guarantee, exercised the one way that proves it.

    Every public function binds `DB_PATH` as its `db_path` default at import,
    so repointing the module attribute alone leaves all ten still aimed at the
    developer's own ledger. No test omits `db_path=` today; this is the day
    someone does.
    """
    ledger.traverse_start("owner/repo", 438, {"mode": "direct"})

    assert [row["kind"] for row in raw_rows(ledger.DB_PATH)] == ["traverse-start"]


def test_first_write_creates_the_store_in_wal_mode(tmp_path: Path) -> None:
    db_path = tmp_path / "absent" / "events.db"

    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
    assert mode == "wal"


def test_a_read_creates_the_store_it_finds_absent(tmp_path: Path) -> None:
    db_path = tmp_path / "absent" / "events.db"

    assert ledger.live_jobs(db_path=db_path) == []

    with closing(sqlite3.connect(db_path)) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    assert ("ledger",) in tables


def test_a_write_against_a_locked_store_waits_rather_than_failing(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    with closing(sqlite3.connect(db_path)) as blocker, ThreadPoolExecutor(1) as pool:
        blocker.execute("BEGIN EXCLUSIVE")
        contended = pool.submit(
            ledger.traverse_end,
            "owner/repo",
            438,
            {"status": "pr-ready"},
            db_path=db_path,
        )
        time.sleep(LOCK_HOLD_SECONDS)
        still_waiting = not contended.done()
        blocker.rollback()
        contended.result(timeout=ledger.BUSY_TIMEOUT_SECONDS)

    assert still_waiting
    assert [row["kind"] for row in raw_rows(db_path)] == [
        "traverse-start",
        "traverse-end",
    ]


def test_received_at_matches_the_events_timestamp_format(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    (row,) = raw_rows(db_path)
    stamped = datetime.fromisoformat(row["received_at"])
    assert stamped.tzinfo == UTC
    assert len(row["received_at"]) == len("2026-08-19T12:34:56.123456+00:00")


def test_a_writer_accepts_a_mapping_that_is_not_a_dict(db_path: Path) -> None:
    ledger.traverse_start(
        "owner/repo", 438, MappingProxyType({"mode": "direct"}), db_path=db_path
    )

    (row,) = raw_rows(db_path)
    assert row["payload"] == '{"mode": "direct"}'


@pytest.mark.parametrize(("kind", "write"), JOB_WRITERS)
def test_a_job_writer_stores_its_kind_both_grain_columns_and_payload(
    kind: str, write: JobWriter, db_path: Path
) -> None:
    write("owner/repo", 438, "build", "sess-1", {"note": kind}, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert tuple(row)[2:7] == (kind, "owner/repo", 438, "build", "sess-1")
    assert json.loads(row["payload"]) == {"note": kind}


def test_a_write_holds_off_the_signals_a_trap_writes_its_books_from(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A handler that landed inside a write would deadlock against it.

    The trap runs on the thread it interrupted, so a handler reached mid-write
    queues its own INSERT behind a write lock only that suspended thread can
    release: it waits out the busy timeout and leaves as `LedgerError`, and the
    `killed` end that closes the traverse's window never lands.

    The mask is read at the moment the store is opened, which is inside the
    write and the only place from which the answer means anything.
    """
    during: list[set[int]] = []
    opening: Callable[..., sqlite3.Connection] = sqlite3.connect

    def watched(*arguments: Any, **keywords: Any) -> sqlite3.Connection:
        during.append(set(signal.pthread_sigmask(signal.SIG_BLOCK, [])))
        return opening(*arguments, **keywords)

    monkeypatch.setattr(sqlite3, "connect", watched)

    ledger.traverse_start("owner/repo", 440, {"mode": "auto"}, db_path=db_path)

    assert set(ledger.DEFERRED_SIGNALS) <= during[0]
    assert not set(ledger.DEFERRED_SIGNALS) & signal.pthread_sigmask(
        signal.SIG_BLOCK, []
    )


# --- failure discipline ---


def test_a_write_to_an_unwritable_store_raises_ledger_error(tmp_path: Path) -> None:
    blocking_file = tmp_path / "not-a-directory"
    blocking_file.write_text("")

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.traverse_start(
            "owner/repo", 438, {}, db_path=blocking_file / "events.db"
        )

    assert isinstance(raised.value.__cause__, OSError)


def test_a_read_of_a_corrupt_store_raises_ledger_error(db_path: Path) -> None:
    db_path.write_text("this is not a database")

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert isinstance(raised.value.__cause__, sqlite3.Error)


def test_a_store_that_will_not_take_wal_raises_ledger_error(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        ledger.sqlite3, "connect", lambda *_args, **_kwargs: in_memory_store()
    )

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    assert "memory" in str(raised.value)


def test_a_read_of_an_unparseable_stored_payload_names_the_row(
    db_path: Path,
) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    rot_the_stored_payload(db_path, "{not json")

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert isinstance(raised.value.__cause__, json.JSONDecodeError)
    assert "row 1" in str(raised.value)


def test_a_read_of_a_null_stored_payload_raises_ledger_error(
    db_path: Path,
) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    rot_the_stored_payload(db_path, None)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert isinstance(raised.value.__cause__, TypeError)


@pytest.mark.parametrize("stored", NOT_JSON_OBJECTS)
def test_a_read_of_a_payload_that_is_not_an_object_names_the_row(
    stored: str, db_path: Path
) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    rot_the_stored_payload(db_path, stored)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert "row 1" in str(raised.value)


def test_awaiting_merge_refuses_a_candidate_whose_payload_is_not_an_object(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    rot_the_stored_payload(db_path, "123")

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert "row 1" in str(raised.value)


def test_a_stored_traverse_row_may_carry_no_node_or_session_id(
    db_path: Path,
) -> None:
    """The traverse grain's NULLs are its shape, not a row missing something."""
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    (row,) = ledger.awaiting_merge(db_path=db_path)

    assert (row.node, row.session_id) == (None, None)


@pytest.mark.parametrize("address", REFUSED_TRAVERSE_ADDRESSES)
@pytest.mark.parametrize(("kind", "write"), TRAVERSE_WRITERS)
def test_a_traverse_writer_refuses_an_address_the_gate_bars(
    kind: str, write: TraverseWriter, address: tuple[Any, Any], db_path: Path
) -> None:
    with pytest.raises(ValueError):
        write(*address, {}, db_path=db_path)

    assert not db_path.exists()


@pytest.mark.parametrize("address", REFUSED_JOB_ADDRESSES)
@pytest.mark.parametrize(("kind", "write"), JOB_WRITERS)
def test_a_job_writer_refuses_an_address_the_gate_bars(
    kind: str, write: JobWriter, address: tuple[Any, Any, Any, Any], db_path: Path
) -> None:
    with pytest.raises(ValueError):
        write(*address, {}, db_path=db_path)

    assert not db_path.exists()


@pytest.mark.parametrize("payload", REFUSED_TRAVERSE_END_PAYLOADS)
def test_traverse_end_refuses_a_status_the_gate_bars(
    payload: dict[str, Any], db_path: Path
) -> None:
    """A traverse ends on one of `STATUSES`, and the writer is told so.

    `traverse_end` is the sole writer of the one row `awaiting_merge` reads a
    payload value out of, and judging a status needs no knowledge of any other
    row -- so the judgment sits at the door, where the caller who got it wrong
    is still on the stack, rather than at a read where it would be a row nobody
    can attribute and nobody can repair.
    """
    with pytest.raises(ValueError):
        ledger.traverse_end("owner/repo", 438, payload, db_path=db_path)

    assert not db_path.exists()


@pytest.mark.parametrize("status", ledger.STATUSES)
def test_traverse_end_accepts_every_terminal_status(status: str, db_path: Path) -> None:
    """Every way a traverse ends, the escalated and killed ones included.

    An escalated exit writes `traverse-end` too (epic standing ruling 4), and so
    does the kill trap, so a door that took only `pr-ready` would refuse most of
    the traverses there are.
    """
    ledger.traverse_end("owner/repo", 438, {"status": status}, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert json.loads(row["payload"]) == {"status": status}


@pytest.mark.parametrize("filters", REFUSED_FILTERS)
def test_live_jobs_refuses_a_filter_the_gate_bars(
    filters: dict[str, Any], db_path: Path
) -> None:
    with pytest.raises(ValueError):
        ledger.live_jobs(**filters, db_path=db_path)

    assert not db_path.exists()


@pytest.mark.parametrize("repo", REFUSED_FILTER_NAMES)
def test_awaiting_merge_refuses_a_filter_the_gate_bars(
    repo: Any, db_path: Path
) -> None:
    with pytest.raises(ValueError):
        ledger.awaiting_merge(repo=repo, db_path=db_path)

    assert not db_path.exists()


def test_an_unserializable_payload_raises_before_anything_is_written(
    db_path: Path,
) -> None:
    with pytest.raises(TypeError):
        ledger.traverse_start("owner/repo", 438, {"opaque": object()}, db_path=db_path)

    assert not db_path.exists()


# --- live_jobs ---


def test_live_jobs_returns_a_launched_unreported_job(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch(
        "owner/repo", 438, "build", "sess-1", {"pid": 42}, db_path=db_path
    )

    live = ledger.live_jobs(db_path=db_path)

    assert [
        (row.repo, row.issue, row.node, row.session_id, row.payload) for row in live
    ] == [("owner/repo", 438, "build", "sess-1", {"pid": 42})]


def test_live_jobs_maps_every_stored_column_onto_its_own_field(
    db_path: Path,
) -> None:
    """The job-grain half of the positional unpack `_decode` reads rows by.

    Only two of the eight kinds are reachable through a public read —
    `live_jobs` returns `job-launch` and `awaiting_merge` returns
    `traverse-end`, and the brief adds no third read — so those two are where
    the decode is pinned. The unpack itself is kind-blind, and what it can get
    wrong is the column-to-field mapping: this asserts all eight fields against
    the row as raw SQL sees it, so a slipped column fails here rather than
    handing back a `node` holding a session id.
    """
    ledger.job_launch(
        "owner/repo", 438, "build", "sess-1", {"pid": 42}, db_path=db_path
    )

    (row,) = ledger.live_jobs(db_path=db_path)

    (stored,) = raw_rows(db_path)
    assert row == ledger.LedgerRow(
        id=stored["id"],
        received_at=stored["received_at"],
        kind="job-launch",
        repo="owner/repo",
        issue=438,
        node="build",
        session_id="sess-1",
        payload={"pid": 42},
    )


def test_live_jobs_drops_a_reported_job(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.job_report("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)

    assert ledger.live_jobs(db_path=db_path) == []


def test_live_jobs_keeps_every_node_launched_at_one_issue(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch(
        "owner/repo", 438, "bug-pr-review", "sess-bug", {}, db_path=db_path
    )
    ledger.job_launch(
        "owner/repo", 438, "code-pr-review", "sess-code", {}, db_path=db_path
    )
    ledger.job_launch(
        "owner/repo", 438, "doc-pr-review", "sess-doc", {}, db_path=db_path
    )

    live = ledger.live_jobs(db_path=db_path)

    assert [row.node for row in live] == [
        "bug-pr-review",
        "code-pr-review",
        "doc-pr-review",
    ]


def test_live_jobs_keeps_a_job_when_a_different_session_is_reported(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch(
        "owner/repo", 438, "code-pr-review", "sess-code", {}, db_path=db_path
    )
    ledger.job_launch(
        "owner/repo", 438, "doc-pr-review", "sess-doc", {}, db_path=db_path
    )
    ledger.job_report(
        "owner/repo", 438, "code-pr-review", "sess-code", {}, db_path=db_path
    )

    assert [row.session_id for row in ledger.live_jobs(db_path=db_path)] == ["sess-doc"]


@pytest.mark.parametrize("second", COLLIDING_JOBS)
def test_live_jobs_refuses_a_session_id_held_by_two_jobs(
    second: tuple[str, int, str], db_path: Path
) -> None:
    """A session id names one job, and it is what joins that job to its events.

    Two jobs holding one is corrupt however a query is written: a report for
    either retires both, the `events` join answers with the wrong issue, and no
    later row can tell them apart again.
    """
    ledger.job_launch("owner/one", 1, "build", "sess-x", {}, db_path=db_path)
    ledger.job_launch(*second, "sess-x", {}, db_path=db_path)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert "sess-x" in str(raised.value)


def test_live_jobs_answers_from_one_snapshot_of_the_store(
    db_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A launch committed after the collision guard cannot slip into the answer.

    The guard and the query are two statements, and the query matches a report
    on its session id alone — so a colliding launch landing between them would
    come back as live with nothing raised, which is the whole harm the guard
    exists to stop. One connection is not one snapshot; a held transaction is.

    The collision is asserted before the answer is. It fires from a trace
    callback keyed on a fragment of the query, so a later rewrite of that query
    can stop the collision happening at all — and then the answer below is
    right for the wrong reason and this test guards nothing. An empty `pending`
    is what says the store really did change under the read.
    """
    ledger.job_launch("owner/one", 1, "build", "sess-1", {}, db_path=db_path)
    connecting, pending = connect_colliding_between_the_guard_and_the_query(db_path)
    monkeypatch.setattr(ledger.sqlite3, "connect", connecting)

    live = ledger.live_jobs(db_path=db_path)

    assert pending == []
    assert [(row.repo, row.issue) for row in live] == [("owner/one", 1)]


def test_live_jobs_reads_a_launch_and_its_own_report_sharing_a_session_id(
    db_path: Path,
) -> None:
    """The one sharing that is not a collision: a job reporting on itself."""
    ledger.traverse_start("owner/one", 1, {}, db_path=db_path)
    ledger.job_launch("owner/one", 1, "build", "sess-x", {}, db_path=db_path)
    ledger.job_report("owner/one", 1, "build", "sess-x", {}, db_path=db_path)

    assert ledger.live_jobs(db_path=db_path) == []


def test_live_jobs_drops_a_job_superseded_by_a_later_launch_of_its_node(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-2", {}, db_path=db_path)

    assert [row.session_id for row in ledger.live_jobs(db_path=db_path)] == ["sess-2"]


def test_live_jobs_drops_a_job_once_its_traverse_ends(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    assert ledger.live_jobs(db_path=db_path) == []


def test_live_jobs_drops_a_job_when_a_later_traverse_starts(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    assert ledger.live_jobs(db_path=db_path) == []


def test_live_jobs_drops_a_job_once_its_issue_is_closed_out(db_path: Path) -> None:
    """A traverse killed before writing `traverse-end` still closes at closeout.

    The issue is terminal once it is closed out, so no future `traverse-start`
    will ever arrive to clear the launch — leaving it live would strand it in
    every answer for good.
    """
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.closeout("owner/repo", 438, {"outcome": "abandoned"}, db_path=db_path)

    assert ledger.live_jobs(db_path=db_path) == []


def test_live_jobs_keeps_a_job_through_a_traverse_escalation(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.traverse_escalation("owner/repo", 438, {"why": "stuck"}, db_path=db_path)

    assert [row.session_id for row in ledger.live_jobs(db_path=db_path)] == ["sess-1"]


def test_live_jobs_keeps_a_job_when_another_issues_traverse_ends(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    ledger.traverse_end("owner/repo", 999, {"status": "pr-ready"}, db_path=db_path)

    assert [row.session_id for row in ledger.live_jobs(db_path=db_path)] == ["sess-1"]


def three_open_jobs(db_path: Path) -> None:
    """Launch one open job in each of two repos, and a second issue of the first."""
    ledger.traverse_start("owner/one", 1, {}, db_path=db_path)
    ledger.job_launch("owner/one", 1, "build", "sess-one-1", {}, db_path=db_path)
    ledger.traverse_start("owner/one", 2, {}, db_path=db_path)
    ledger.job_launch("owner/one", 2, "build", "sess-one-2", {}, db_path=db_path)
    ledger.traverse_start("owner/two", 1, {}, db_path=db_path)
    ledger.job_launch("owner/two", 1, "build", "sess-two-1", {}, db_path=db_path)


def test_live_jobs_without_a_filter_reads_the_whole_machine(db_path: Path) -> None:
    three_open_jobs(db_path)

    live = ledger.live_jobs(db_path=db_path)

    assert [row.session_id for row in live] == [
        "sess-one-1",
        "sess-one-2",
        "sess-two-1",
    ]


def test_live_jobs_filters_conjoin(db_path: Path) -> None:
    three_open_jobs(db_path)

    live = ledger.live_jobs(repo="owner/one", issue=2, db_path=db_path)

    assert [row.session_id for row in live] == ["sess-one-2"]


def test_live_jobs_filters_on_repo_alone(db_path: Path) -> None:
    three_open_jobs(db_path)

    live = ledger.live_jobs(repo="owner/one", db_path=db_path)

    assert [row.session_id for row in live] == ["sess-one-1", "sess-one-2"]


def test_live_jobs_filters_on_issue_alone(db_path: Path) -> None:
    three_open_jobs(db_path)

    live = ledger.live_jobs(issue=1, db_path=db_path)

    assert [row.session_id for row in live] == ["sess-one-1", "sess-two-1"]


# --- awaiting_merge ---


def test_awaiting_merge_returns_a_pr_ready_traverse_end(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    waiting = ledger.awaiting_merge(db_path=db_path)

    assert [(row.repo, row.issue, row.payload) for row in waiting] == [
        ("owner/repo", 438, {"status": "pr-ready"})
    ]


def test_awaiting_merge_maps_every_stored_column_onto_its_own_field(
    db_path: Path,
) -> None:
    """The traverse-grain half, where both grain columns come back NULL."""
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    (row,) = ledger.awaiting_merge(db_path=db_path)

    (stored,) = raw_rows(db_path)
    assert row == ledger.LedgerRow(
        id=stored["id"],
        received_at=stored["received_at"],
        kind="traverse-end",
        repo="owner/repo",
        issue=438,
        node=None,
        session_id=None,
        payload={"status": "pr-ready"},
    )


def test_awaiting_merge_drops_an_issue_once_it_is_closed_out(db_path: Path) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    ledger.closeout("owner/repo", 438, {"outcome": "merged"}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_drops_an_issue_once_a_later_traverse_starts(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_never_returns_a_traverse_end_that_is_not_pr_ready(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "escalated"}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_reads_only_the_newest_traverse_end_of_an_issue(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "escalated"}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_neither_raises_nor_lists_an_issue_whose_traverse_was_killed(
    db_path: Path,
) -> None:
    """The third terminal status closes a window without ever awaiting a merge.

    A traverse that dies in its kill trap ends `killed`, and the gate has to
    take that status or the trap's last write raises inside the handler and the
    window never closes at all.
    """
    ledger.traverse_start("owner/repo", 440, {"mode": "auto"}, db_path=db_path)
    ledger.traverse_end("owner/repo", 440, {"status": "killed"}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_filters_on_repo(db_path: Path) -> None:
    ledger.traverse_end("owner/one", 1, {"status": "pr-ready"}, db_path=db_path)
    ledger.traverse_end("owner/two", 2, {"status": "pr-ready"}, db_path=db_path)

    waiting = ledger.awaiting_merge(repo="owner/two", db_path=db_path)

    assert [(row.repo, row.issue) for row in waiting] == [("owner/two", 2)]


# --- traverse_starts ---


def test_traverse_starts_returns_one_issues_starts_in_write_order(
    db_path: Path,
) -> None:
    """Every start the issue ever had, however many windows have closed since.

    The review loop's cycle cap counts from the newest baseline a start
    recorded, so these rows are read whole rather than through an open window:
    a start is what *closes* a window, so the only one inside any open window is
    the current traverse's own.
    """
    ledger.traverse_start("owner/repo", 441, {"mode": "auto"}, db_path=db_path)
    ledger.traverse_end("owner/repo", 441, {"status": "escalated"}, db_path=db_path)
    ledger.traverse_start(
        "owner/repo", 441, {"mode": "user-rework", "baseline_cycle": 3}, db_path=db_path
    )

    starts = ledger.traverse_starts(repo="owner/repo", issue=441, db_path=db_path)

    assert [row.payload for row in starts] == [
        {"mode": "auto"},
        {"mode": "user-rework", "baseline_cycle": 3},
    ]


def test_traverse_starts_reads_no_other_issue_and_no_other_kind(
    db_path: Path,
) -> None:
    ledger.traverse_start("owner/repo", 441, {"mode": "auto"}, db_path=db_path)
    ledger.traverse_start("owner/repo", 442, {"mode": "auto"}, db_path=db_path)
    ledger.traverse_start("other/repo", 441, {"mode": "auto"}, db_path=db_path)
    ledger.phase_transition("owner/repo", 441, {"to": "pr-review"}, db_path=db_path)

    starts = ledger.traverse_starts(repo="owner/repo", issue=441, db_path=db_path)

    assert [(row.kind, row.repo, row.issue) for row in starts] == [
        ("traverse-start", "owner/repo", 441)
    ]


def test_traverse_starts_answers_an_issue_that_never_started_with_nothing(
    db_path: Path,
) -> None:
    assert ledger.traverse_starts(repo="owner/repo", issue=441, db_path=db_path) == []


@pytest.mark.parametrize(
    ("repo", "issue"), [("", 441), ("owner/repo", 0), ("owner/repo", "441")]
)
def test_traverse_starts_refuses_an_address_the_ledger_cannot_use(
    repo: Any, issue: Any, db_path: Path
) -> None:
    with pytest.raises(ValueError):
        ledger.traverse_starts(repo=repo, issue=issue, db_path=db_path)


# --- the session-id spine ---


def test_a_job_launch_joins_to_its_events_on_session_id(db_path: Path) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute(EVENTS_SCHEMA)
        connection.executemany(INSERT_EVENT, [("sess-1",), ("sess-unrelated",)])
        connection.commit()
        joined = connection.execute(JOIN_ON_SESSION_ID).fetchall()

    assert joined == [("owner/repo", 438, "build")]
