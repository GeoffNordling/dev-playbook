"""Shared fixtures and helpers for the tools test suite."""

import json
import os
import sqlite3
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from dev_playbook import gitrepo


@pytest.fixture(autouse=True)
def _clean_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip ambient git redirection variables from every test's environment.

    The suite runs inside the pre-push hook (``make check-judgments-cache``),
    and from a linked worktree -- where the software factory works -- git
    exports an absolute ``GIT_DIR`` into that hook. It outranks ``git -C``
    and ``cwd=`` in every fixture subprocess: ``git init`` becomes a silent
    no-op and ``ls-files`` reads the wrong index, so no test may inherit it.

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


# --- the software factory's two test modules share these ---


class StoredRow(NamedTuple):
    """One run-ledger row as a factory test reads it back out of the store."""

    kind: str
    node: str | None
    session_id: str | None
    payload: dict[str, Any]


def ledger_rows(db: Path) -> list[StoredRow]:
    """Every row the run ledger holds, in write order; none before it exists.

    Read with SQL rather than through ``dev_playbook.factory.ledger``: that
    module's own reads answer questions about open windows and live jobs, and a
    test asking what was written needs the rows themselves.
    """
    if not db.exists():
        return []
    with sqlite3.connect(db) as connection:
        rows = connection.execute(
            "SELECT kind, node, session_id, payload FROM ledger ORDER BY id"
        ).fetchall()
    return [
        StoredRow(kind, node, session_id, json.loads(payload))
        for kind, node, session_id, payload in rows
    ]


def write_definition(directory: Path, stem: str, frontmatter: dict[str, Any]) -> Path:
    """Write one agent definition, its frontmatter rendered as YAML."""
    body = "\n".join(f"{key}: {value}" for key, value in frontmatter.items())
    path = directory / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{body}\n---\n\nThe node's instructions.\n")
    return path


def process_state(pid: int) -> str | None:
    """The single-letter process-table state of ``pid``, or None once it is gone.

    Read from ``/proc`` rather than asked with ``os.kill(pid, 0)``: a signal
    probe answers "alive" for a zombie, and a child whose launcher was destroyed
    is reparented, so it is a zombie until the reaper collects it. What these
    tests measure is that it stopped running, which the state letter says and
    the signal probe does not.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # The comm field is parenthesized and may hold spaces of its own, so the
    # split starts after the last ')' rather than at the second field.
    return stat.rpartition(")")[2].split()[0]
