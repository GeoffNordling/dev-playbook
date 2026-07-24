"""Behavioral tests for the playbook-lint aggregator.

Fixtures build a scripts/ directory of fake detectors — tiny executables with
canned stdout/stderr and exit codes — and point the module's roster at them,
so no test runs a real detector. The manifest-validation step is exercised
through a fake ``uvx`` on PATH, the same no-network pattern as the fake ``gh``
in test_workspace_lint.
"""

import os
from pathlib import Path

import pytest

from dev_playbook import playbook_lint

FAKE_DETECTOR = """\
#!/usr/bin/env python3
import sys
sys.stdout.write({out!r})
sys.stderr.write({err!r})
sys.exit({code})
"""


def write_detector(
    scripts_dir: Path, name: str, *, code: int, out: str = "", err: str = ""
) -> None:
    script = scripts_dir / name
    script.write_text(FAKE_DETECTOR.format(out=out, err=err, code=code))
    script.chmod(0o755)


def wire(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, detectors: tuple[str, ...]
) -> tuple[Path, Path]:
    """Point the module at a fake scripts/ dir; return (scripts_dir, repo root).

    The ambient ``SKIP`` is cleared so a developer's own environment cannot
    leak a skip into a test; tests that exercise SKIP set it explicitly.
    """
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(playbook_lint, "SCRIPTS_DIR", scripts_dir)
    monkeypatch.setattr(playbook_lint, "DETECTORS", detectors)
    monkeypatch.delenv("SKIP", raising=False)
    return scripts_dir, root


def test_all_clean_detectors_aggregate_to_exit_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint", "b-lint"))
    write_detector(scripts_dir, "a-lint", code=0, err="a-lint: clean\n")
    write_detector(scripts_dir, "b-lint", code=0, err="b-lint: clean\n")

    assert playbook_lint.main([str(root)]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "a-lint: clean" in captured.err
    assert "playbook-lint: 2 detector(s) clean" in captured.err


def test_findings_pass_through_and_aggregate_to_exit_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint", "b-lint"))
    write_detector(scripts_dir, "a-lint", code=0)
    write_detector(scripts_dir, "b-lint", code=1, out="x.md: b.rule broken\n")

    assert playbook_lint.main([str(root)]) == 1

    captured = capsys.readouterr()
    assert "x.md: b.rule broken" in captured.out
    assert "playbook-lint: findings from: b-lint" in captured.err


def test_output_prints_in_roster_order_not_completion_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scripts_dir, root = wire(monkeypatch, tmp_path, ("b-lint", "a-lint"))
    write_detector(scripts_dir, "a-lint", code=1, out="from-a\n")
    write_detector(scripts_dir, "b-lint", code=1, out="from-b\n")

    playbook_lint.main([str(root)])

    assert capsys.readouterr().out == "from-b\nfrom-a\n"


def test_detector_tool_error_aggregates_to_exit_two(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Exit 2 outranks a sibling's findings: a gate that cannot fully run must
    # not report as a mere red.
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint", "b-lint"))
    write_detector(scripts_dir, "a-lint", code=1, out="x.md: a.rule broken\n")
    write_detector(scripts_dir, "b-lint", code=2, err="b-lint: cannot scan\n")

    assert playbook_lint.main([str(root)]) == 2

    assert "playbook-lint: could not run: b-lint" in capsys.readouterr().err


def test_missing_detector_script_is_a_loud_tool_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A roster entry with no script is an enrollment defect in the hook repo
    # itself; it must brick the gate, not vanish.
    _, root = wire(monkeypatch, tmp_path, ("ghost-lint",))

    assert playbook_lint.main([str(root)]) == 2

    captured = capsys.readouterr()
    assert "cannot run" in captured.err
    assert "ghost-lint" in captured.err


def test_skip_env_skips_by_detector_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint", "b-lint"))
    write_detector(scripts_dir, "a-lint", code=1, out="from-a\n")
    write_detector(scripts_dir, "b-lint", code=0)
    monkeypatch.setenv("SKIP", "a-lint")

    assert playbook_lint.main([str(root)]) == 0

    captured = capsys.readouterr()
    assert "from-a" not in captured.out
    assert "playbook-lint: a-lint skipped (SKIP)" in captured.err


def test_skip_names_outside_the_roster_are_left_alone(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # SKIP is shared vocabulary with pre-commit itself (shellcheck, ruff), so a
    # name that matches no roster entry is not announced and not an error.
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint",))
    write_detector(scripts_dir, "a-lint", code=0)
    monkeypatch.setenv("SKIP", "shellcheck")

    assert playbook_lint.main([str(root)]) == 0

    assert "skipped" not in capsys.readouterr().err


def test_every_detector_skipped_exits_zero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, root = wire(monkeypatch, tmp_path, ("a-lint",))
    monkeypatch.setenv("SKIP", "a-lint")

    assert playbook_lint.main([str(root)]) == 0

    assert "playbook-lint: every detector skipped" in capsys.readouterr().err


def test_validate_manifest_runs_only_where_a_manifest_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint",))
    write_detector(scripts_dir, "a-lint", code=0)
    (root / ".pre-commit-hooks.yaml").write_text("- id: x\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_detector(bin_dir, "uvx", code=1, out="manifest invalid\n")
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    assert playbook_lint.main([str(root)]) == 1

    assert "findings from: validate-manifest" in capsys.readouterr().err


def test_no_manifest_means_no_validate_manifest_step(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A poison uvx proves non-invocation: were the step to run anyway, the run
    # would go red.
    scripts_dir, root = wire(monkeypatch, tmp_path, ("a-lint",))
    write_detector(scripts_dir, "a-lint", code=0)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_detector(bin_dir, "uvx", code=2)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    assert playbook_lint.main([str(root)]) == 0

    assert "validate-manifest" not in capsys.readouterr().err
