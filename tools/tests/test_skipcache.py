"""Behavioral tests for the skipcache seen-set library."""

import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from skipcache import filter, record


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the seen-set at a throwaway cache dir so tests never touch ~/.cache."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    return tmp_path


def test_filter_returns_all_keys_unseen_when_nothing_recorded() -> None:
    result = filter(["3f9c", "b1e0"])

    assert result.seen == []
    assert result.unseen == ["3f9c", "b1e0"]


def test_filter_with_no_keys_returns_empty_partition() -> None:
    result = filter([])

    assert result.seen == []
    assert result.unseen == []


def test_filter_separates_recorded_keys_from_new_ones() -> None:
    record(["a"])

    result = filter(["a", "b"])

    assert result.seen == ["a"]
    assert result.unseen == ["b"]


def test_record_is_idempotent() -> None:
    record(["a"])
    record(["a"])

    result = filter(["a"])

    assert result.seen == ["a"]
    assert result.unseen == []


def test_recorded_keys_persist_across_processes(isolated_cache: Path) -> None:
    record(["abc"])

    tools_dir = Path(__file__).resolve().parents[1]
    program = "import skipcache; print(skipcache.filter(['abc']).seen)"
    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=tools_dir,
        env={**os.environ, "PYTHONPATH": str(tools_dir)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "abc" in result.stdout


def test_store_lives_at_xdg_cache_path(isolated_cache: Path) -> None:
    record(["a"])

    assert (isolated_cache / "skipcache" / "seen.sqlite").is_file()


def test_store_holds_keys_only(isolated_cache: Path) -> None:
    record(["a", "b"])

    db = isolated_cache / "skipcache" / "seen.sqlite"
    with closing(sqlite3.connect(db)) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        columns = conn.execute(f"PRAGMA table_info({tables[0][0]})").fetchall()

    assert len(tables) == 1
    assert len(columns) == 1


def test_keys_are_stored_opaquely() -> None:
    opaque = ["", "a b\tc", "naïve", "'); DROP TABLE seen;--", "x" * 2000]
    record(opaque)

    result = filter(opaque)

    assert result.seen == opaque
    assert result.unseen == []


def test_record_with_no_keys_is_a_noop() -> None:
    record([])

    result = filter(["a"])

    assert result.seen == []
    assert result.unseen == ["a"]


def test_store_falls_back_to_home_cache_without_xdg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    record(["a"])

    assert (tmp_path / ".cache" / "skipcache" / "seen.sqlite").is_file()
