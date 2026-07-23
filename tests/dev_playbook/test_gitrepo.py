from collections.abc import Callable
from pathlib import Path

import pytest
from conftest import init_repo

from dev_playbook.gitrepo import canonical_repo_name, git_files, no_git_env


def test_ambient_git_dir_does_not_redirect_git_files(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    target = tmp_path / "target"
    init_repo(target)
    (target / "real.txt").write_text("belongs to the target\n")
    (target / ".gitignore").write_text("leaked.txt\n")
    (target / "leaked.txt").write_text("the target ignores its own copy\n")
    ambient_git_dir("leaked.txt")

    assert git_files(target) == [".gitignore", "real.txt"]


def test_ambient_git_dir_does_not_redirect_canonical_repo_name(
    tmp_path: Path, ambient_git_dir: Callable[[str], Path]
) -> None:
    target = tmp_path / "target"
    init_repo(target)
    ambient_git_dir("leaked.txt")

    assert canonical_repo_name(target) == "target"


def test_no_git_env_drops_redirection_and_keeps_the_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIT_DIR", "/somewhere/.git")
    monkeypatch.setenv("GIT_WORK_TREE", "/somewhere")
    monkeypatch.setenv("GIT_INDEX_FILE", "/somewhere/.git/index")
    monkeypatch.setenv("GIT_EXEC_PATH", "/usr/lib/git-core")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.bare")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "false")
    monkeypatch.setenv("PATH_TO_NOWHERE", "kept")

    scrubbed = no_git_env()

    assert "GIT_DIR" not in scrubbed
    assert "GIT_WORK_TREE" not in scrubbed
    assert "GIT_INDEX_FILE" not in scrubbed
    assert scrubbed["GIT_EXEC_PATH"] == "/usr/lib/git-core"
    assert scrubbed["GIT_CONFIG_COUNT"] == "1"
    assert scrubbed["GIT_CONFIG_KEY_0"] == "core.bare"
    assert scrubbed["GIT_CONFIG_VALUE_0"] == "false"
    assert scrubbed["PATH_TO_NOWHERE"] == "kept"
