"""Behavioral tests for tools/bin/no-future-annotations."""

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "no-future-annotations"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_clean_directory_exits_zero(tmp_path: Path) -> None:
    (tmp_path / "ok.py").write_text("x: int | None = None\n")
    result = run(str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_flags_future_annotations_in_py_file(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("from __future__ import annotations\n\nx: int = 1\n")
    result = run(str(tmp_path))
    assert result.returncode == 1
    assert str(bad) in result.stdout
    assert "no-future-annotations" in result.stdout


def test_flags_extensionless_python_shebang(tmp_path: Path) -> None:
    script = tmp_path / "mytool"
    script.write_text("#!/usr/bin/env python3\nfrom __future__ import annotations\n")
    result = run(str(tmp_path))
    assert result.returncode == 1
    assert str(script) in result.stdout


def test_ignores_non_python_extensionless_files(tmp_path: Path) -> None:
    other = tmp_path / "notes"
    other.write_text("from __future__ import annotations\n")
    result = run(str(tmp_path))
    assert result.returncode == 0


def test_ignores_string_literals(tmp_path: Path) -> None:
    f = tmp_path / "stringy.py"
    f.write_text('docs = "from __future__ import annotations"\n')
    result = run(str(tmp_path))
    assert result.returncode == 0


def test_other_future_imports_are_allowed(tmp_path: Path) -> None:
    f = tmp_path / "div.py"
    f.write_text("from __future__ import division\n")
    result = run(str(tmp_path))
    assert result.returncode == 0


def test_skips_excluded_dirs(tmp_path: Path) -> None:
    excluded = tmp_path / ".venv" / "lib"
    excluded.mkdir(parents=True)
    (excluded / "bad.py").write_text("from __future__ import annotations\n")
    result = run(str(tmp_path))
    assert result.returncode == 0


def test_accepts_individual_files_as_args(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("from __future__ import annotations\n")
    good = tmp_path / "good.py"
    good.write_text("x = 1\n")
    result = run(str(bad), str(good))
    assert result.returncode == 1
    assert str(bad) in result.stdout
    assert str(good) not in result.stdout


def test_repo_self_scan_is_clean() -> None:
    """The dev-playbook repo itself should be free of the banned import."""
    repo = Path(__file__).resolve().parents[2]
    result = run(str(repo))
    assert result.returncode == 0, result.stdout + result.stderr
