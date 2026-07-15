"""Shared fixtures for the tools test suite."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[[dict[str, str]], Path]:
    """Write a throwaway repo from a {relative path: contents} map; return its root.

    Used by the judgements tests to stand up a fixture repo -- a
    ``pyproject.toml`` with ``[tool.judgements]``, declaration YAML files, and
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
