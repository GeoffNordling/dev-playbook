"""Tests for the transcript-export CLI: selection logic and file output.

Selection is exercised with a mocked `session list` runner (no daemon); the
end-to-end write path injects a render stub so `main` is checked for the files
it writes, not the rendering already covered elsewhere.
"""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from transcript_export.cli import main, select_session_ids


def list_runner(ids: list[str]) -> Callable:
    """A fake subprocess.run answering `session list` with the given ids."""

    def runner(args: list[str], **kwargs: object) -> object:
        assert args[1:3] == ["session", "list"]
        payload = {"sessions": [{"id": sid} for sid in ids], "total": len(ids)}
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout=json.dumps(payload)
        )

    return runner


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
