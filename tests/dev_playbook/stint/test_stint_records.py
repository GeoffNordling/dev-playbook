"""The records a stint leaves, and the copy read as plain files."""

import json
import os
import subprocess
from pathlib import Path

import pytest

from dev_playbook.gitrepo import no_git_env
from dev_playbook.stint import workcopy
from dev_playbook.stint.records import CallRecord, StintRecord, Usage


def call(name: str) -> CallRecord:
    return CallRecord(
        name=name,
        session="s1",
        resumed=None,
        api_key_source="none",
        seconds=3,
        is_error=False,
        usage=Usage(2, 300, 10000, 100),
        commits=["abc"],
        uncommitted=[],
        answer="ok",
    )


def test_context_counts_input_cached_and_output() -> None:
    assert Usage(2, 300, 10000, 100).context == 10402


def test_a_call_record_is_written_under_its_name(tmp_path: Path) -> None:
    call("iter-1").write(tmp_path)
    written = json.loads((tmp_path / "iter-1.json").read_text())
    assert written["answer"] == "ok"
    assert written["usage"]["cache_read_input_tokens"] == 10000


def test_stint_json_keeps_each_calls_summary(tmp_path: Path) -> None:
    StintRecord(reason="done", budget=4, calls=[call("iter-1")]).write(tmp_path)
    written = json.loads((tmp_path / "stint.json").read_text())
    assert written["reason"] == "done"
    assert written["calls"] == [
        {
            "name": "iter-1",
            "session": "s1",
            "resumed": None,
            "seconds": 3,
            "commits": ["abc"],
        }
    ]


def git(root: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    return done.stdout.strip()


def test_head_commit_matches_git_loose_and_packed(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q", "-b", "main")
    git(
        tmp_path,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "one",
    )
    assert workcopy.head_commit(tmp_path) == git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "pack-refs", "--all")
    assert workcopy.head_commit(tmp_path) == git(tmp_path, "rev-parse", "HEAD")


def test_read_plain_refuses_a_symlink(tmp_path: Path) -> None:
    secret = tmp_path / "secret"
    secret.write_text("host file")
    (tmp_path / "ws").mkdir()
    os.symlink(secret, tmp_path / "ws" / "PLAN.md")
    with pytest.raises(workcopy.CopyFault, match="symlink in the copy: ws/PLAN.md"):
        workcopy.read_plain(tmp_path, "ws/PLAN.md")
