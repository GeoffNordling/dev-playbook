"""Behavioral tests for the command that runs the whole measurement pipeline.

Every test builds its own store in `tmp_path` and runs against that. The real
store is live and is never read here: a suite that read it would assert against
whatever the machine happened to be doing.

The fixture below is a plausible day rather than a minimal one — two sessions,
a typed slash command, a phantom subagent stop, a task notification and a ghost
session — because what this command is for is reporting what it dropped, and a
store with nothing to drop cannot show that.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd
import pytest
from measure_fakes import a_payload, at

from dev_playbook.measure import cli

WORKSPACE = Path("/w")
ALPHA = "/w/alpha"
BETA = "/w/beta"

SCHEMA = """
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    received_at TEXT,
    event TEXT,
    session_id TEXT,
    prompt_id TEXT,
    payload TEXT
)
"""

# How long each fixture turn keeps Claude busy, in seconds.
WORK_SECONDS = 30.0

# The pauses between one session's turns: mostly a reader typing the next
# prompt, twice a stretch nobody was there for. Two modes, so the mixture has
# something to find; all different, so the fit has a spread to work with.
ALPHA_IDLES = (60.0, 90.0, 150.0, 45.0, 300.0, 30.0, 3600.0, 75.0, 50.0, 200.0, 7200.0)
BETA_IDLES = (120.0, 400.0, 90.0)

# Beta opens long after alpha's last event, so a window can hold one session
# without the other — which is what makes dormancy visible at all.
BETA_START = 20000.0

# The whole fixture's gap count: every idle but each session's last one, which
# no submit follows.
FIXTURE_GAPS = len(ALPHA_IDLES) - 1 + len(BETA_IDLES) - 1


def a_turn(
    session: str, moment: float, index: int, cwd: str
) -> list[tuple[float, dict]]:
    """One complete turn: the human submits, Claude works, Claude stops."""
    prompt = f"{session}-{index}"
    return [
        (
            moment,
            a_payload(
                "UserPromptSubmit",
                session=session,
                prompt_id=prompt,
                prompt="do a thing",
                cwd=cwd,
            ),
        ),
        (
            moment + WORK_SECONDS,
            a_payload("Stop", session=session, prompt_id=prompt, cwd=cwd),
        ),
    ]


def a_session(
    session: str, idles: tuple[float, ...], start: float, cwd: str
) -> list[tuple[float, dict]]:
    """A session's whole life: one turn per idle, each followed by that pause."""
    rows = []
    moment = start
    for index, idle in enumerate(idles):
        rows.extend(a_turn(session, moment, index, cwd))
        moment += WORK_SECONDS + idle
    return rows


def fixture_rows() -> list[tuple[float, dict]]:
    """Two working sessions, plus one row for each thing the cleanings remove."""
    return [
        *a_session("alpha", ALPHA_IDLES, start=0.0, cwd=ALPHA),
        *a_session("beta", BETA_IDLES, start=BETA_START, cwd=BETA),
        # A typed /build: the expansion folds onto the submit that follows it.
        (
            5.0,
            a_payload(
                "UserPromptExpansion",
                session="alpha",
                prompt_id="alpha-0",
                command_name="build",
                command_args="",
                cwd=ALPHA,
            ),
        ),
        # A stop for a subagent nobody dispatched.
        (
            7.0,
            a_payload(
                "SubagentStop",
                session="alpha",
                agent_type="",
                agent_id="ghost-agent",
                cwd=ALPHA,
            ),
        ),
        # A prompt the harness submitted to report a finished background task.
        (
            9.0,
            a_payload(
                "UserPromptSubmit",
                session="alpha",
                prompt_id="alpha-note",
                prompt="<task-notification>done</task-notification>",
                cwd=ALPHA,
            ),
        ),
        # A session slot that never carried a submission.
        (11.0, a_payload("SessionStart", session="gamma", cwd=ALPHA)),
    ]


def a_store(path: Path, rows: list[tuple[float, dict]]) -> Path:
    """Write a store at `path` from (second, payload) pairs; return the path.

    Rows go in in the order given, so ids follow that order, which is the total
    order the store's own derivations walk.
    """
    connection = sqlite3.connect(path)
    connection.execute(SCHEMA)
    for second, payload in rows:
        connection.execute(
            "INSERT INTO events (received_at, payload) VALUES (?, ?)",
            (at(second).isoformat(), json.dumps(payload)),
        )
    connection.commit()
    connection.close()
    return path


def a_busy_store(tmp_path: Path) -> Path:
    """The fixture store, written where a test can read it."""
    return a_store(tmp_path / "events.db", fixture_rows())


def run_over(store_path: Path, *argv: str) -> int:
    """The command over `store_path`, writing its page beside it."""
    return cli.main(
        [str(store_path.parent / "activity.html"), "--db", str(store_path), *argv],
        workspace=WORKSPACE,
    )


# --- the pipeline -------------------------------------------------------------


def test_the_table_carries_the_definitive_rows_and_the_graded_ones(
    tmp_path: Path,
) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    assert set(run.table["state"]) == {"claude_active", "dormant", "human_present"}


def test_every_cleaning_reports_what_it_took_out(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    assert [(cleaning.technique, cleaning.removed) for cleaning in run.cleanings] == [
        ("collapse expansion/submit pairs", 1),
        ("drop phantom SubagentStop", 1),
        ("drop task-notification pseudo-prompts", 1),
        ("drop ghost sessions", 1),
    ]


def test_the_events_that_survive_carry_their_attribution(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    assert set(run.events["repo"]) == {"alpha", "beta"}
    assert "build" in set(run.events["skill"])


def test_the_window_defaults_to_the_whole_store(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    assert run.window == (at(0), at(max(second for second, _ in fixture_rows())))


def test_a_named_window_cuts_the_events_it_reads(tmp_path: Path) -> None:
    run = cli.pipeline(
        a_busy_store(tmp_path),
        since=at(0),
        until=at(BETA_START - 1),
        workspace=WORKSPACE,
    )

    assert run.window == (at(0), at(BETA_START - 1))
    assert run.windowed < run.stored
    assert set(run.events["session_id"]) == {"alpha"}


def test_dormancy_is_measured_against_the_window_not_the_events(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), until=at(30000), workspace=WORKSPACE)
    dormant = run.table[run.table["state"] == "dormant"]

    assert set(dormant["end"]) == {at(30000), at(BETA_START)}


def test_an_empty_store_is_refused(tmp_path: Path) -> None:
    empty = a_store(tmp_path / "empty.db", [])

    with pytest.raises(cli.PipelineError, match="holds no events"):
        cli.pipeline(empty, workspace=WORKSPACE)


def test_a_quiet_stretch_of_the_store_is_refused(tmp_path: Path) -> None:
    with pytest.raises(cli.PipelineError, match="no events between"):
        cli.pipeline(
            a_busy_store(tmp_path),
            since=at(6000),
            until=at(9000),
            workspace=WORKSPACE,
        )


def test_a_bound_past_the_stores_own_edge_is_refused(tmp_path: Path) -> None:
    with pytest.raises(cli.PipelineError, match="the store runs"):
        cli.pipeline(a_busy_store(tmp_path), since=at(90000), workspace=WORKSPACE)


def test_a_window_that_ends_before_it_starts_is_refused(tmp_path: Path) -> None:
    with pytest.raises(cli.PipelineError, match="is empty"):
        cli.pipeline(
            a_busy_store(tmp_path), since=at(500), until=at(100), workspace=WORKSPACE
        )


# --- window bounds ------------------------------------------------------------


def test_a_bound_without_a_zone_is_read_as_utc() -> None:
    assert cli.timestamp("2026-07-30T08:00") == pd.Timestamp("2026-07-30T08:00Z")


def test_a_bound_carrying_an_offset_is_converted() -> None:
    assert cli.timestamp("2026-07-30T10:00+02:00") == pd.Timestamp("2026-07-30T08:00Z")


def test_a_bare_date_is_that_days_first_moment() -> None:
    assert cli.timestamp("2026-07-30") == pd.Timestamp("2026-07-30T00:00Z")


# --- the report ---------------------------------------------------------------


def test_the_report_names_the_window_and_what_it_read(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    text = cli.report(run)

    assert f"{run.stored} rows in the store" in text
    assert "in the window" in text


def test_the_report_carries_the_fit_that_graded_presence(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    text = cli.report(run)

    assert f"presence mixture over {FIXTURE_GAPS} gaps" in text
    assert "even odds at" in text


def test_the_report_gives_both_levels_of_every_state(tmp_path: Path) -> None:
    run = cli.pipeline(a_busy_store(tmp_path), workspace=WORKSPACE)

    text = cli.report(run)

    assert "level     state                wall  expected" in text
    assert "sessions  claude_active" in text
    assert "machine   human_present" in text


def test_an_open_turn_is_reported_as_a_lower_bound(tmp_path: Path) -> None:
    rows = [
        *fixture_rows(),
        (
            30000.0,
            a_payload(
                "UserPromptSubmit",
                session="alpha",
                prompt_id="alpha-open",
                prompt="one more",
                cwd=ALPHA,
            ),
        ),
    ]
    run = cli.pipeline(a_store(tmp_path / "open.db", rows), workspace=WORKSPACE)

    assert run.unresolved == 1
    assert "1 turns are still open" in cli.report(run)


# --- the command --------------------------------------------------------------


def test_a_run_writes_a_page_that_needs_no_network(tmp_path: Path) -> None:
    exit_code = run_over(a_busy_store(tmp_path))
    page = (tmp_path / "activity.html").read_text(encoding="utf-8")

    assert exit_code == 0
    assert "<script src=" not in page
    assert "Plotly.newPlot" in page


def test_the_page_is_titled_with_the_lane_key_and_the_window(tmp_path: Path) -> None:
    run_over(a_busy_store(tmp_path))
    page = (tmp_path / "activity.html").read_text(encoding="utf-8")

    assert "activity by session" in page


def test_the_lane_key_pivots_the_page_to_repositories(tmp_path: Path) -> None:
    exit_code = run_over(a_busy_store(tmp_path), "--lane", "repo")
    page = (tmp_path / "activity.html").read_text(encoding="utf-8")

    assert exit_code == 0
    assert '"alpha"' in page
    assert '"beta"' in page


def test_the_run_prints_its_report_and_where_the_page_went(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    run_over(a_busy_store(tmp_path))

    printed = capsys.readouterr().out

    assert "presence mixture" in printed
    assert f"wrote {tmp_path / 'activity.html'}" in printed


def test_a_missing_store_is_one_line_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    exit_code = run_over(tmp_path / "nothing.db")

    printed = capsys.readouterr().err

    assert exit_code == 1
    assert printed.startswith("measure-timeline: unable to open database")


def test_a_window_the_command_cannot_use_is_one_line_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    exit_code = run_over(a_busy_store(tmp_path), "--since", "2030-01-01")

    printed = capsys.readouterr().err

    assert exit_code == 1
    assert printed.startswith("measure-timeline: the window 2030-01-01")


def test_a_lane_key_the_view_does_not_know_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run_over(a_busy_store(tmp_path), "--lane", "hostname")
