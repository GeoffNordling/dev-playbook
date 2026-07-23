"""Shared fixtures for the tools test suite."""

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from dev_playbook import gitrepo


@pytest.fixture(autouse=True)
def _clean_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip ambient git redirection variables from every test's environment.

    The suite runs inside the pre-push hook (``make check-judgments``), and from
    a linked worktree -- where the software factory works -- git exports an
    absolute ``GIT_DIR`` into that hook. It outranks ``git -C`` and ``cwd=`` in
    every fixture subprocess: ``git init`` becomes a silent no-op and
    ``ls-files`` reads the wrong index, so no test may inherit it.

    The set removed is ``gitrepo.no_git_env``'s, not a second hand-written copy
    -- one policy governs the code under test and the environment it is tested
    in, so a fixture repo is never built under different git settings than
    production would use.
    """
    for key in set(os.environ) - set(gitrepo.no_git_env()):
        monkeypatch.delenv(key)


def init_repo(path: Path) -> None:
    """Initialize an empty git repo at ``path``, creating the directory."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-q", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )


def commit_all(repo: Path) -> None:
    """Stage and commit everything in ``repo`` under a throwaway identity."""
    subprocess.run(
        ["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True
    )
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
        capture_output=True,
    )


@pytest.fixture
def ambient_git_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Callable[[str], Path]:
    """Export an absolute ``GIT_DIR`` naming a decoy repo that tracks one file.

    Reproduces the environment git creates inside a hook. An absolute
    ``GIT_DIR`` outranks ``git -C <root>`` and the working directory in every
    child process, so a git call that fails to scrub it silently answers for
    the decoy instead of the repo it named. Call this last, after the fixture
    repos exist -- a bare ``git init`` under an ambient ``GIT_DIR`` is itself a
    silent no-op. Returns the decoy root.
    """

    def factory(tracked: str) -> Path:
        decoy = tmp_path / "decoy"
        init_repo(decoy)
        leak = decoy / tracked
        leak.parent.mkdir(parents=True, exist_ok=True)
        leak.write_text("tracked in the decoy\n")
        commit_all(decoy)
        monkeypatch.setenv("GIT_DIR", str(decoy / ".git"))
        return decoy

    return factory


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[[dict[str, str]], Path]:
    """Write a throwaway repo from a {relative path: contents} map; return its root.

    Used by the judgments tests to stand up a fixture repo -- a
    ``pyproject.toml`` with ``[tool.judgments]``, declaration YAML files, and
    evidence files -- against ``tmp_path``.
    """

    def factory(files: dict[str, str]) -> Path:
        repo = tmp_path / "repo"
        for relpath, contents in files.items():
            path = repo / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)
        return repo

    return factory
