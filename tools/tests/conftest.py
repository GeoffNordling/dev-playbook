"""Shared fixtures for the tools test suite."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pytest

from workflow_state_data.core import IssueData, LabelEvent


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


@pytest.fixture
def ts() -> Callable[[str], datetime]:
    """Parse an ISO-8601 timestamp string into a datetime."""
    return datetime.fromisoformat


@pytest.fixture
def make_issue(ts: Callable[[str], datetime]) -> Callable[..., IssueData]:
    """Factory for an open, in-flight issue; phase and field overrides per test."""

    def factory(phase: str = "tdd", **overrides: object) -> IssueData:
        """Build IssueData with in-flight defaults plus the given overrides."""
        defaults: dict = {
            "repo": "geoff/widgets",
            "number": 7,
            "title": "Add widget",
            "state": "open",
            "created_at": ts("2026-01-01T00:00:00+00:00"),
            "closed_at": None,
            "labels": (
                "category:enhancement",
                "mode:direct",
                "tests:yes",
                f"phase:{phase}",
            ),
            "events": (
                LabelEvent(
                    "labeled", f"phase:{phase}", ts("2026-01-01T00:00:00+00:00")
                ),
            ),
            "comment_count": 3,
        }
        return IssueData(**{**defaults, **overrides})

    return factory
