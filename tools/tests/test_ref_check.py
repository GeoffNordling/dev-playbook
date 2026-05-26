"""Behavioral tests for tools/bin/ref-check — assert on exit code and stderr."""

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
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )


def commit_all(repo: Path) -> None:
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
            "init",
        ],
        check=True,
    )


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    ws = tmp_path / "workspace"
    ws.mkdir()
    return ws


def write(file: Path, content: str) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)


def test_in_repo_ref_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "docs.md", "see ~/workspace/primary/target.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_in_repo_ref_to_missing_file_is_broken(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/primary/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1
    assert "1/1 broken" in result.stderr


def test_cross_repo_ref_to_existing_file_is_ok(tmp_path: Path, workspace: Path) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(other / "thing.md", "x")
    write(repo / "docs.md", "see ~/workspace/other/thing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0


def test_cross_repo_ref_to_missing_file_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    other = workspace / "other"
    init_repo(repo)
    other.mkdir()
    write(repo / "docs.md", "see ~/workspace/other/missing.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_cross_repo_ref_to_missing_repo_is_broken(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "docs.md", "see ~/workspace/no-such-repo/foo.md\n")

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 1


def test_reference_inside_inline_code_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
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


def test_reference_inside_fenced_code_block_is_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    repo = workspace / "primary"
    init_repo(repo)
    write(
        repo / "docs.md",
        "intro\n```\nsee ~/workspace/primary/missing.md\n```\nend\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "no cross-references found" in result.stderr


def test_broken_refs_inside_adr_directory_are_skipped(
    tmp_path: Path, workspace: Path
) -> None:
    """ADRs are immutable historical records — broken refs in them are
    expected staleness, not lint errors."""
    repo = workspace / "primary"
    init_repo(repo)
    write(repo / "target.md", "x")
    write(repo / "other.md", "see ~/workspace/primary/target.md\n")
    write(
        repo / "docs" / "adr" / "0001-decision.md",
        "see ~/workspace/primary/gone.md\n",
    )

    result = run_ref_check(repo, tmp_path)

    assert result.returncode == 0
    assert "all ok" in result.stderr


def test_worktree_resolves_in_repo_refs_to_worktree_working_copy(
    tmp_path: Path, workspace: Path
) -> None:
    """File present only in the worktree's working copy must resolve as ok."""
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


def test_not_a_git_repo_exits_2(tmp_path: Path, workspace: Path) -> None:
    not_a_repo = workspace / "no-git-here"
    not_a_repo.mkdir()
    write(not_a_repo / "docs.md", "irrelevant\n")

    result = run_ref_check(not_a_repo, tmp_path)

    assert result.returncode == 2
    assert "not a git repository" in result.stderr
