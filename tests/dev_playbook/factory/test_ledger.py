import sqlite3
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

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


def raw_rows(db_path: Path) -> list[tuple[object, ...]]:
    """Every ledger row as a raw tuple, oldest first, read outside the module."""
    with closing(sqlite3.connect(db_path)) as connection:
        return connection.execute(
            f"SELECT {COLUMNS} FROM ledger ORDER BY id"
        ).fetchall()


def test_traverse_start_appends_one_row(tmp_path: Path) -> None:
    db_path = tmp_path / "store" / "events.db"

    ledger.traverse_start("owner/repo", 438, {"mode": "direct"}, db_path=db_path)

    assert [row[2:] for row in raw_rows(db_path)] == [
        ("traverse-start", "owner/repo", 438, None, None, '{"mode": "direct"}')
    ]


@pytest.mark.parametrize(("kind", "write"), TRAVERSE_WRITERS)
def test_traverse_writers_stamp_their_kind_with_no_node_or_session(
    kind: str, write: TraverseWriter, db_path: Path
) -> None:
    write("owner/repo", 438, {"note": kind}, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert (row[2], row[5], row[6]) == (kind, None, None)


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

    assert (still_waiting, [row[2] for row in raw_rows(db_path)]) == (
        True,
        ["traverse-start", "traverse-end"],
    )


def test_received_at_matches_the_events_timestamp_format(db_path: Path) -> None:
    ledger.traverse_start("owner/repo", 438, {}, db_path=db_path)

    (row,) = raw_rows(db_path)
    stamped = datetime.fromisoformat(str(row[1]))
    assert (stamped.tzinfo, len(str(row[1]))) == (
        UTC,
        len("2026-08-19T12:34:56.123456+00:00"),
    )


@pytest.mark.parametrize(("kind", "write"), JOB_WRITERS)
def test_job_writers_carry_node_and_session(
    kind: str, write: JobWriter, db_path: Path
) -> None:
    write("owner/repo", 438, "build", "sess-1", {"note": kind}, db_path=db_path)

    (row,) = raw_rows(db_path)
    assert row[2:] == (
        kind,
        "owner/repo",
        438,
        "build",
        "sess-1",
        f'{{"note": "{kind}"}}',
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


def test_awaiting_merge_drops_an_issue_once_it_is_closed_out(db_path: Path) -> None:
    ledger.traverse_end("owner/repo", 438, {"status": "pr-ready"}, db_path=db_path)
    ledger.closeout("owner/repo", 438, {"outcome": "merged"}, db_path=db_path)

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


def test_awaiting_merge_raises_naming_a_newest_traverse_end_with_no_status(
    db_path: Path,
) -> None:
    ledger.traverse_end("owner/repo", 438, {"note": "no status here"}, db_path=db_path)

    with pytest.raises(ledger.LedgerError) as raised:
        ledger.awaiting_merge(db_path=db_path)

    assert str(raised.value).endswith(": [1]")


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
