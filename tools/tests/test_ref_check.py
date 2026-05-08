"""Behavioral tests for tools/bin/ref-check.

Each test fabricates a workspace under tmp_path, sets HOME so that the
script's `~/workspace` resolves to the fake one, and invokes ref-check via
subprocess. Assertions are on exit code and stderr — that's the contract
callers rely on (pre-commit reads exit code; humans read stderr).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REF_CHECK = Path(__file__).resolve().parents[1] / "bin" / "ref-check"


def run_ref_check(
    repo_root: Path, home: Path, *args: str
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        ["python3", str(REF_CHECK), *args, str(repo_root)],
        capture_output=True,
        text=True,
        env=env,
    )


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )


def commit_all(repo: Path, message: str = "init") -> None:
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=t@example.com",
            "-c",
            "user.name=test",
            "commit",
            "-q",
            "-m",
            message,
        ],
        check=True,
    )


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Empty fake workspace at <tmp_path>/workspace/. HOME → <tmp_path>."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


def write(file: Path, content: str) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)


def test_in_repo_ref_to_existing_file_is_ok(tmp_path, workspace):
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_in_repo_ref_to_missing_file_is_broken(tmp_path, workspace):
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/primary/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


def test_cross_repo_ref_to_existing_file_is_ok(tmp_path, workspace):
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(other / "thing.md", "x")
    write(repo / "docs.md", "see ~/workspace/other/thing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_cross_repo_ref_to_missing_file_is_broken(tmp_path, workspace):
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(repo / "docs.md", "see ~/workspace/other/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_cross_repo_ref_to_missing_repo_is_broken(tmp_path, workspace):
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/no-such-repo/foo.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_reference_inside_inline_code_is_skipped(tmp_path, workspace):
    """Backticked content is prose per repo-documentation.md — refs inside
    `~/workspace/<placeholder>` syntax must not be classified."""
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "see `~/workspace/<name>/missing.md` for the template\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_reference_inside_fenced_code_block_is_skipped(tmp_path, workspace):
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "intro\n```\nsee ~/workspace/primary/missing.md\n```\nend\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_worktree_resolves_in_repo_refs_to_worktree_working_copy(tmp_path, workspace):
    """File present only in the worktree's working copy must resolve as ok.

    This is the worktree-equivalence guarantee: same .md content yields the
    same outcome whether scanned from the main checkout or a worktree of it.
    Without using `git rev-parse --git-common-dir`, an in-repo reference from
    a worktree falls through to absolute-path resolution and looks at the
    main checkout — which does not have this file. The fix prevents that.
    """
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "README.md", "base")
    commit_all(repo)

    wt = repo / ".claude" / "worktrees" / "feature-x"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", "feature-x"],
        check=True,
    )
    write(wt / "target.md", "only here")
    write(wt / "docs.md", "see ~/workspace/primary/target.md\n")
    assert not (repo / "target.md").exists()

    result = run_ref_check(wt, tmp_path)

    assert result.returncode == 0, result.stderr


def test_not_a_git_repo_exits_2(tmp_path, workspace):
    not_a_repo = workspace / "no-git-here"
    not_a_repo.mkdir()
    write(not_a_repo / "docs.md", "irrelevant\n")

    result = run_ref_check(not_a_repo, tmp_path)

    assert result.returncode == 2
    assert "not a git repository" in result.stderr
