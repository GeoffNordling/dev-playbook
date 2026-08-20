import json
import sqlite3
import time
import uuid
from collections.abc import Callable
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

# A `status` a candidate row can carry that is outside the module's closed
# vocabulary because it is not a string at all. The unhashable two are the
# reason the vocabulary is a tuple: a set would raise `TypeError` out of the
# guard rather than judge them.
NOT_STATUS_STRINGS = [1, None, True, ["pr-ready"], {"value": "pr-ready"}]

# The promoted columns a stored row of each grain has to carry. Every one is a
# column a query matches on -- `received_at` excepted, which `LedgerRow` simply
# promises is a string.
LAUNCH_KEY_COLUMNS = ["received_at", "repo", "issue", "node", "session_id"]
TRAVERSE_KEY_COLUMNS = ["received_at", "repo", "issue"]

# A second job whose address differs from `("owner/one", 1, "build")` in one
# column each -- the three ways a reused session id can span two jobs.
COLLIDING_JOBS = [
    ("owner/two", 1, "build"),
    ("owner/one", 2, "build"),
    ("owner/one", 1, "doc-pr-review"),
]

# A branch name where an issue number belongs -- the caller bug the gate
# refuses at the front door, and that an operator's own UPDATE can still put in
# the store behind the module's back. Typed loosely so the deliberate misuse is
# the test's subject rather than a type error.
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


@pytest.fixture(autouse=True)
def never_the_real_store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Repoint the module's default store into the temp tree, for every test.

    `DB_PATH` is the default on all ten public functions, so one omitted
    `db_path=` would otherwise append to the developer's real ledger. Autouse
    makes "nothing touches the real store" enforced rather than remembered.
    """
    monkeypatch.setattr(ledger, "DB_PATH", tmp_path / "default" / "events.db")


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
    the store intact and rotted there — the hazard an append-only table
    cannot repair, and so must report rather than crash past.
    """
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute("UPDATE ledger SET payload = ?", (payload,))
        connection.commit()


def overwrite_the_stored_column(db_path: Path, column: str, value: Any) -> None:
    """Set one promoted column of the ledger's only row, behind the module's back.

    The gate refuses every value below at the front door, so this stands in for
    a row that got into the store some other way — an older build, a
    hand-written INSERT, an operator's repair that overshot. Front door and
    store integrity are two different jobs, and this exercises the second.
    """
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute(f"UPDATE ledger SET {column} = ?", (value,))
        connection.commit()


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
    write("owner/repo", 438, {"note": kind}, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert (row["kind"], row["node"], row["session_id"]) == (kind, None, None)
    assert json.loads(row["payload"]) == {"note": kind}


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
            ledger.traverse_end, "owner/repo", 438, {}, db_path=db_path
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


def test_live_jobs_refuses_a_stored_launch_with_no_session_id(
    db_path: Path,
) -> None:
    """The row a report can never match, so it would stand as live forever."""
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    overwrite_the_stored_column(db_path, "session_id", None)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert "row 1" in str(raised.value)


@pytest.mark.parametrize("column", LAUNCH_KEY_COLUMNS)
def test_live_jobs_refuses_a_stored_launch_missing_a_key_column(
    column: str, db_path: Path
) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    overwrite_the_stored_column(db_path, column, None)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert column in str(raised.value)


@pytest.mark.parametrize("column", TRAVERSE_KEY_COLUMNS)
def test_awaiting_merge_refuses_a_candidate_missing_a_key_column(
    column: str, db_path: Path
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    overwrite_the_stored_column(db_path, column, None)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert column in str(raised.value)


def test_live_jobs_refuses_a_stored_launch_whose_issue_is_not_a_number(
    db_path: Path,
) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)
    overwrite_the_stored_column(db_path, "issue", NOT_AN_ISSUE_NUMBER)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.live_jobs(db_path=db_path)

    assert "issue" in str(raised.value)


def test_awaiting_merge_refuses_a_candidate_whose_issue_is_not_a_number(
    db_path: Path,
) -> None:
    """A column can hold the wrong type as well as nothing at all.

    The gate keeps a caller from writing one, but SQLite's INTEGER affinity
    converts only what already looks numeric and stores the rest as it came --
    so a row that reached the store any other way reads back as a `LedgerRow`
    lying about its own type.
    """
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    overwrite_the_stored_column(db_path, "issue", NOT_AN_ISSUE_NUMBER)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert "issue" in str(raised.value)


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


def test_awaiting_merge_refuses_a_candidate_whose_status_is_unrecognised(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr_ready"}, db_path=db_path)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert str(raised.value).endswith(": [1]")


def test_awaiting_merge_raises_naming_a_newest_traverse_end_with_no_status(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"note": "no status here"}, db_path=db_path)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert str(raised.value).endswith(": [1]")


@pytest.mark.parametrize("status", NOT_STATUS_STRINGS)
def test_awaiting_merge_refuses_a_candidate_whose_status_is_not_a_string(
    status: object, db_path: Path
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": status}, db_path=db_path)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert str(raised.value).endswith(": [1]")


def test_awaiting_merge_ignores_a_superseded_unrecognised_status(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr_ready"}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    assert [row.issue for row in ledger.awaiting_merge(db_path=db_path)] == [438]


def test_awaiting_merge_ignores_a_superseded_status_that_is_not_a_string(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": 7}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    assert [row.issue for row in ledger.awaiting_merge(db_path=db_path)] == [438]


def test_awaiting_merge_ignores_a_superseded_traverse_end_with_no_status(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"note": "no status here"}, db_path=db_path)
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)

    assert [row.issue for row in ledger.awaiting_merge(db_path=db_path)] == [438]


def test_awaiting_merge_ignores_a_closed_out_traverse_end_with_no_status(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"note": "no status here"}, db_path=db_path)
    ledger.closeout("owner/repo", 438, {"outcome": "merged"}, db_path=db_path)

    assert ledger.awaiting_merge(db_path=db_path) == []


def test_awaiting_merge_filters_on_repo(db_path: Path) -> None:
    ledger.traverse_end("owner/one", 1, {"status": "pr-ready"}, db_path=db_path)
    ledger.traverse_end("owner/two", 2, {"status": "pr-ready"}, db_path=db_path)

    waiting = ledger.awaiting_merge(repo="owner/two", db_path=db_path)

    assert [(row.repo, row.issue) for row in waiting] == [("owner/two", 2)]


# --- the session-id spine ---


def test_a_job_launch_joins_to_its_events_on_session_id(db_path: Path) -> None:
    ledger.job_launch("owner/repo", 438, "build", "sess-1", {}, db_path=db_path)

    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute(EVENTS_SCHEMA)
        connection.executemany(INSERT_EVENT, [("sess-1",), ("sess-unrelated",)])
        connection.commit()
        joined = connection.execute(JOIN_ON_SESSION_ID).fetchall()

    assert joined == [("owner/repo", 438, "build")]
