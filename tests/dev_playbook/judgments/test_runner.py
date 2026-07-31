"""Behavioral tests for the judgments-run CLI: plan, render, record."""

import json
import sys
from pathlib import Path

import pytest

from dev_playbook.judgments.core import SCHEMA, prepare
from dev_playbook.judgments.runner import main

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
    assert output["seen_count"] == 0
    (entry,) = output["unseen"]
    assert entry.keys() == {"id", "model", "effort", "prompt"}
    assert entry["id"] == "j1"
    assert entry["model"] == "claude-sonnet-4-6"
    assert entry["effort"] == "high"
    assert "render j1" in entry["prompt"]


def test_plan_counts_cached_judgments_without_listing_them(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The ids of already-passing judgments are context an orchestrating agent
    # pays for and never reads, so plan reports how many there are, not which.
    assert main(["record", "j1"]) == 0

    assert main(["plan"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["seen_count"] == 1
    assert "seen" not in output


def test_plan_hands_back_a_self_contained_invocation(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Every command the plan hands out -- the judge prompts and the `cli` a caller
    # appends `record` to -- must run without a PATH lookup, an activated
    # virtualenv, or a particular working directory, because judge agents have
    # none of those guaranteed. It names an absolute interpreter and its own root.
    assert main(["plan"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["cli"].startswith(sys.executable)
    assert f"--root {repo}" in output["cli"]
    assert output["unseen"][0]["prompt"].startswith(
        f"Run this exact command: {sys.executable}"
    )


def test_plan_with_no_config_emits_an_empty_docket(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.chdir(bare)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    exit_code = main(["plan"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["schema"] == SCHEMA
    assert output["seen_count"] == 0
    assert output["unseen"] == []


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
    assert output["seen_count"] == 1
    assert output["unseen"] == []


def test_root_option_runs_from_an_unrelated_directory(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The whole point of --root: a judge agent gets a fully-specified command and
    # runs it wherever it happens to be standing.
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    assert main(["--root", str(repo), "render", "j1"]) == 0


def test_root_option_rejects_a_directory_that_is_not_a_repo(
    repo: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()

    exit_code = main(["--root", str(not_a_repo), "plan"])

    assert exit_code == 1
    assert "no pyproject.toml" in capsys.readouterr().err


def test_record_is_idempotent(repo: Path) -> None:
    assert main(["record", "j1"]) == 0
    assert main(["record", "j1"]) == 0


def test_list_rules_reports_no_rules(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # judgments-run records passing verdicts but emits no findings, so it answers
    # the detector protocol with an empty rule set.
    exit_code = main(["--list-rules"])

    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_record_rejects_the_removed_refuted_flag(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The never-used refuted recording path is gone; passing it is a hard usage
    # error, never a silently-ignored no-op.
    with pytest.raises(SystemExit) as excinfo:
        main(["record", "--refuted", "j1"])

    assert excinfo.value.code == 2
    assert "refuted" in capsys.readouterr().err


def test_record_with_no_ids_is_an_error(
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
