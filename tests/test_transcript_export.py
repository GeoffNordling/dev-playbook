"""Tests for the transcript-export CLI: selection logic and file output.

Selection is exercised with mocked `session list` / `session search` runners (no
daemon); the end-to-end write path injects a render stub so `main` is checked for
the files it writes, not the rendering already covered elsewhere.
"""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from dev_playbook.transcript_export.cli import (
    SelectionError,
    main,
    select_session_ids,
)


def list_runner(ids: list[str]) -> Callable:
    """A fake subprocess.run answering `session list` with the given ids."""

    def runner(args: list[str], **kwargs: object) -> object:
        base = args.index("session")
        assert args[base : base + 2] == ["session", "list"]
        payload = {"sessions": [{"id": sid} for sid in ids], "total": len(ids)}
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout=json.dumps(payload)
        )

    return runner


def search_runner(match_ids: list[str], truncated: bool = False) -> Callable:
    """A fake `session search`; `match_ids` is one entry per per-message match."""

    def runner(args: list[str], **kwargs: object) -> object:
        base = args.index("session")
        assert args[base : base + 2] == ["session", "search"]
        payload: dict = {"matches": [{"session_id": sid} for sid in match_ids]}
        if truncated:
            payload["next_cursor"] = "cur-1"
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout=json.dumps(payload)
        )

    return runner


def refused_runner(args: list[str], **kwargs: object) -> object:
    """A runner standing in for a daemon that is not reachable."""
    return subprocess.CompletedProcess(
        args=args, returncode=1, stdout="", stderr="fatal: connection refused"
    )


def boom_runner(args: list[str], **kwargs: object) -> object:
    """A runner that fails if called — explicit ids must not hit the daemon."""
    raise AssertionError(f"daemon must not be queried: {args}")


# --- select_session_ids -----------------------------------------------------


def test_explicit_ids_pass_through_without_querying_daemon() -> None:
    ids = select_session_ids(["a", "b"], None, False, runner=boom_runner)
    assert ids == ["a", "b"]


def test_recent_takes_first_n_from_the_list() -> None:
    runner = list_runner(["s0", "s1", "s2", "s3"])
    assert select_session_ids([], 2, False, runner=runner) == ["s0", "s1"]


def test_recent_larger_than_list_returns_all_available() -> None:
    runner = list_runner(["s0", "s1"])
    assert select_session_ids([], 9, False, runner=runner) == ["s0", "s1"]


def test_all_returns_every_listed_id() -> None:
    runner = list_runner(["s0", "s1", "s2"])
    assert select_session_ids([], None, True, runner=runner) == ["s0", "s1", "s2"]


def test_recent_asks_the_daemon_for_only_the_rows_it_needs() -> None:
    # `--recent 2` must not drag the whole archive across the wire to slice it.
    seen: list[list[str]] = []

    def runner(args: list[str], **kwargs: object) -> object:
        seen.append(args)
        return list_runner(["s0", "s1"])(args, **kwargs)

    select_session_ids([], 2, False, runner=runner)

    assert seen[0][seen[0].index("--limit") + 1] == "2"


# --- select_session_ids: --find ---------------------------------------------


def test_find_resolves_a_single_matching_session() -> None:
    # Several per-message matches, one session: unambiguous, no --limit needed.
    runner = search_runner(["s0", "s0", "s0"])
    assert select_session_ids([], None, False, "auth", runner=runner) == ["s0"]


def test_find_dedups_matches_preserving_the_daemons_order() -> None:
    runner = search_runner(["s0", "s1", "s0", "s2"])
    ids = select_session_ids([], None, False, "auth", 3, runner=runner)
    assert ids == ["s0", "s1", "s2"]


def test_find_matching_several_sessions_without_a_limit_is_ambiguous() -> None:
    runner = search_runner(["s0", "s1"])
    with pytest.raises(SelectionError, match="matched 2 sessions"):
        select_session_ids([], None, False, "auth", runner=runner)


def test_find_reports_a_lower_bound_when_the_match_set_was_truncated() -> None:
    # A capped match set can only bound the session count from below; claiming a
    # total the daemon never confirmed would be a lie the caller cannot detect.
    runner = search_runner(["s0", "s1"], truncated=True)
    with pytest.raises(SelectionError, match="matched at least 2 sessions"):
        select_session_ids([], None, False, "auth", runner=runner)


def test_find_with_no_match_is_an_error() -> None:
    runner = search_runner([])
    with pytest.raises(SelectionError, match="no session matched 'ghost'"):
        select_session_ids([], None, False, "ghost", runner=runner)


def test_find_limit_larger_than_the_match_set_returns_what_matched() -> None:
    runner = search_runner(["s0", "s1"])
    assert select_session_ids([], None, False, "auth", 9, runner=runner) == ["s0", "s1"]


# --- argument validation ----------------------------------------------------


def test_no_selection_mode_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path)])


def test_explicit_ids_with_all_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "s0", "--all"])


def test_recent_and_all_together_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--recent", "2", "--all"])


def test_non_positive_recent_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--recent", "0"])


def test_find_with_all_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--find", "auth", "--all"])


def test_find_with_explicit_ids_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "s0", "--find", "auth"])


def test_limit_without_find_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--recent", "2", "--limit", "1"])


def test_non_positive_limit_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--find", "auth", "--limit", "0"])


# --- main end-to-end output -------------------------------------------------


def fake_render(session_id: str, runner: Callable) -> str:
    """A stand-in renderer producing a unique well-formed body per id."""
    return f'<session id="{session_id}"/>'


def test_main_writes_one_file_per_explicit_id(tmp_path: Path) -> None:
    code = main(
        [str(tmp_path), "alpha", "beta"], runner=boom_runner, render=fake_render
    )

    assert code == 0
    assert (tmp_path / "alpha.xml").read_text() == '<session id="alpha"/>'
    assert (tmp_path / "beta.xml").read_text() == '<session id="beta"/>'


def test_main_creates_missing_output_directory(tmp_path: Path) -> None:
    out_dir = tmp_path / "nested" / "out"
    main([str(out_dir), "alpha"], runner=boom_runner, render=fake_render)

    assert (out_dir / "alpha.xml").read_text() == '<session id="alpha"/>'


def test_main_rewrites_existing_file_idempotently(tmp_path: Path) -> None:
    (tmp_path / "alpha.xml").write_text("STALE")
    main([str(tmp_path), "alpha"], runner=boom_runner, render=fake_render)

    assert (tmp_path / "alpha.xml").read_text() == '<session id="alpha"/>'


def test_main_with_recent_renders_the_selected_ids(tmp_path: Path) -> None:
    main(
        [str(tmp_path), "--recent", "2"],
        runner=list_runner(["s0", "s1", "s2"]),
        render=fake_render,
    )

    assert (tmp_path / "s0.xml").exists()
    assert (tmp_path / "s1.xml").exists()
    assert not (tmp_path / "s2.xml").exists()


def test_main_with_find_renders_the_matched_session(tmp_path: Path) -> None:
    code = main(
        [str(tmp_path), "--find", "auth"],
        runner=search_runner(["s0", "s0"]),
        render=fake_render,
    )

    assert code == 0
    assert (tmp_path / "s0.xml").read_text() == '<session id="s0"/>'


# --- main failure paths: one legible line, never a traceback -----------------


def test_main_reports_an_unreachable_daemon_as_one_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path), "--recent", "1"], runner=refused_runner)

    assert code == 1
    err = capsys.readouterr().err
    assert err.startswith("transcript-export: ")
    assert "connection refused" in err
    assert "Traceback" not in err
    assert len(err.strip().splitlines()) == 1


def test_main_reports_an_ambiguous_find_as_one_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path), "--find", "auth"], runner=search_runner(["s0", "s1"]))

    assert code == 1
    err = capsys.readouterr().err
    assert "matched 2 sessions" in err
    assert "--limit" in err
    assert "Traceback" not in err


def test_main_writes_nothing_when_selection_fails(tmp_path: Path) -> None:
    # Selection resolves before the first file is opened, so a failed export
    # leaves no half-written directory of transcripts behind.
    out_dir = tmp_path / "out"
    code = main([str(out_dir), "--find", "auth"], runner=search_runner(["s0", "s1"]))

    assert code == 1
    assert not out_dir.exists()
