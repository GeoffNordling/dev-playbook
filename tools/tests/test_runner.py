"""Behavioral tests for the judgments-run CLI: plan, render, record."""

import json
from pathlib import Path

import pytest

from judgments.core import SCHEMA, prepare
from judgments.runner import main

CONFIG = '[tool.judgments]\npaths = ["judgments/*.yaml"]\n'

ONE_JUDGMENT = """\
judgments:
  - id: j1
    claim: docs/errors.md lists every exception src/exceptions.py raises.
    evidence: [docs/errors.md]
    reference: [src/exceptions.py]
    model: claude-sonnet-4-6
    effort: high
"""

EVIDENCE = {
    "docs/errors.md": "errors doc\n",
    "src/exceptions.py": "class Boom(Exception): ...\n",
}


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Stand up a judgments repo, chdir into it, and isolate the seen-set cache."""
    root = tmp_path / "repo"
    files = {
        "pyproject.toml": CONFIG,
        "judgments/a.yaml": ONE_JUDGMENT,
        **EVIDENCE,
    }
    for relpath, contents in files.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return root


def test_plan_reports_an_uncached_judgment_as_unseen(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["plan"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["schema"] == SCHEMA
    assert output["seen"] == []
    assert output["unseen"] == [
        {"id": "j1", "model": "claude-sonnet-4-6", "effort": "high"}
    ]


def test_plan_with_no_config_emits_empty_lists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    exit_code = main(["plan"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {"schema": SCHEMA, "seen": [], "unseen": []}


def test_render_prints_exactly_the_prepared_prompt(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = prepare(
        "docs/errors.md lists every exception src/exceptions.py raises.",
        ["docs/errors.md"],
        ["src/exceptions.py"],
        "claude-sonnet-4-6",
        "high",
        repo,
    ).prompt

    exit_code = main(["render", "j1"])

    assert exit_code == 0
    assert capsys.readouterr().out == expected + "\n"


def test_record_then_plan_reports_the_judgment_as_seen(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["record", "j1"]) == 0

    assert main(["plan"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["seen"] == ["j1"]
    assert output["unseen"] == []


def test_record_is_idempotent(repo: Path) -> None:
    assert main(["record", "j1"]) == 0
    assert main(["record", "j1"]) == 0


def test_render_unknown_id_fails_loud(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["render", "nonexistent"])

    assert exit_code != 0
    assert "nonexistent" in capsys.readouterr().err


def test_record_unknown_id_fails_loud(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["record", "nonexistent"])

    assert exit_code != 0
    assert "nonexistent" in capsys.readouterr().err
