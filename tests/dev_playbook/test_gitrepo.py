"""Pins the git-environment scrub: what it strips, and that no test inherits it."""

import os
import subprocess
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


def test_no_git_env_drops_every_repository_locating_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIT_DIR", "/somewhere/.git")
    monkeypatch.setenv("GIT_WORK_TREE", "/somewhere")
    monkeypatch.setenv("GIT_INDEX_FILE", "/somewhere/.git/index")
    monkeypatch.setenv("GIT_COMMON_DIR", "/somewhere/.git")
    monkeypatch.setenv("GIT_PREFIX", "sub/dir/")
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", "/somewhere/.git/objects")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'core.worktree'='/elsewhere'")

    scrubbed = no_git_env()

    assert not {
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_COMMON_DIR",
        "GIT_PREFIX",
        "GIT_OBJECT_DIRECTORY",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
    } & set(scrubbed)


def test_no_git_env_keeps_transport_auth_and_unrelated_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GIT_EXEC_PATH", "/usr/lib/git-core")
    monkeypatch.setenv("GIT_SSH_COMMAND", "ssh -i /keys/id_ed25519")
    monkeypatch.setenv("GIT_ASKPASS", "/usr/bin/askpass")
    monkeypatch.setenv("GIT_SSL_CAINFO", "/etc/ssl/ca.pem")
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    monkeypatch.setenv("PATH_TO_NOWHERE", "kept")

    scrubbed = no_git_env()

    assert scrubbed["GIT_EXEC_PATH"] == "/usr/lib/git-core"
    assert scrubbed["GIT_SSH_COMMAND"] == "ssh -i /keys/id_ed25519"
    assert scrubbed["GIT_ASKPASS"] == "/usr/bin/askpass"
    assert scrubbed["GIT_SSL_CAINFO"] == "/etc/ssl/ca.pem"
    assert scrubbed["GIT_TERMINAL_PROMPT"] == "0"
    assert scrubbed["PATH_TO_NOWHERE"] == "kept"


def test_no_git_env_scrubs_exactly_what_git_reports_as_repository_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reported = subprocess.run(
        ["git", "rev-parse", "--local-env-vars"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    for name in reported:
        monkeypatch.setenv(name, "set-by-the-test")

    scrubbed = set(os.environ) - set(no_git_env())

    assert scrubbed == set(reported)


def test_suite_environment_carries_no_git_redirection() -> None:
    leaked = set(os.environ) - set(no_git_env())

    assert leaked == set()
