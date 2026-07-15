"""Behavioral tests for the judgements-run CLI: plan, render, record."""

import json
from pathlib import Path

import pytest

from dev_playbook.judgements.core import SCHEMA, prepare
from dev_playbook.judgements.runner import REFUTED, main

CONFIG = '[tool.judgements]\npaths = ["judgements/*.yaml"]\n'

ONE_JUDGEMENT = """\
judgements:
  - id: j1
    claim: docs/errors.md lists every exception src/exceptions.py raises.
    evidence: [docs/errors.md]
    reference: [src/exceptions.py]
    model: claude-sonnet-4-6
    effort: high
"""

TWO_JUDGEMENTS = """\
judgements:
  - id: j1
    claim: docs/errors.md lists every exception src/exceptions.py raises.
    evidence: [docs/errors.md]
    reference: [src/exceptions.py]
    model: claude-sonnet-4-6
    effort: high
  - id: j2
    claim: docs/errors.md names the module each exception lives in.
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
    """Stand up a judgements repo, chdir into it, and isolate the seen-set cache."""
    root = tmp_path / "repo"
    files = {
        "pyproject.toml": CONFIG,
        "judgements/a.yaml": ONE_JUDGEMENT,
        **EVIDENCE,
    }
    for relpath, contents in files.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return root


@pytest.fixture
def two_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A judgements repo carrying two declarations (j1, j2), cache isolated."""
    root = tmp_path / "repo"
    files = {
        "pyproject.toml": CONFIG,
        "judgements/a.yaml": TWO_JUDGEMENTS,
        **EVIDENCE,
    }
    for relpath, contents in files.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return root


def test_plan_reports_an_uncached_judgement_as_unseen(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["plan"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["schema"] == SCHEMA
    assert output["seen"] == []
    (entry,) = output["unseen"]
    assert entry.keys() == {"id", "model", "effort", "prompt"}
    assert entry["id"] == "j1"
    assert entry["model"] == "claude-sonnet-4-6"
    assert entry["effort"] == "high"
    assert "judgements-run render j1" in entry["prompt"]


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


def test_record_then_plan_reports_the_judgement_as_seen(
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


def test_list_rules_prints_the_refuted_rule(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["--list-rules"])

    assert exit_code == 0
    assert capsys.readouterr().out.split() == [REFUTED]


def test_record_refuted_verdict_emits_a_finding_and_does_not_cache(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["record", "--refuted", "j1"])

    out = capsys.readouterr().out
    assert exit_code == 1
    assert REFUTED in out
    assert "j1" in out
    # A refuted verdict is never recorded: the gate must stay red.
    assert main(["plan"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["seen"] == []


def test_record_refuted_takes_several_ids_and_caches_none(
    two_repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Space-separated refuted ids all refute; none is silently cached as a pass.
    exit_code = main(["record", "--refuted", "j1", "j2"])

    out = capsys.readouterr().out
    assert exit_code == 1
    assert out.count(REFUTED) == 2
    assert "j1" in out and "j2" in out
    assert main(["plan"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["seen"] == []


def test_record_rejects_an_id_that_is_also_refuted(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Recording an id as both a pass and a refutation is a contradiction; it must
    # fail loud and cache nothing rather than green the gate for a refuted claim.
    exit_code = main(["record", "j1", "--refuted", "j1"])
    capsys.readouterr()

    assert exit_code != 0
    assert main(["plan"]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["seen"] == []


def test_record_with_no_ids_and_no_refutations_is_an_error(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A bare record records nothing — a caller-side bug, surfaced loudly.
    exit_code = main(["record"])

    assert exit_code != 0
    assert capsys.readouterr().err.strip()


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
