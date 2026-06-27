"""Behavioral tests for assert_judgment_cached: the pytest cache-gate helper."""

from pathlib import Path

import pytest

from judgments.core import prepare
from judgments.pytest_support import assert_judgment_cached
from skipcache import seen

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
    for relpath, contents in {
        "pyproject.toml": CONFIG,
        "judgments/a.yaml": ONE_JUDGMENT,
        **EVIDENCE,
    }.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return root


def _record(root: Path) -> None:
    """Record the fixture judgment's key, so its cache gate would pass."""
    key = prepare(
        "docs/errors.md lists every exception src/exceptions.py raises.",
        ["docs/errors.md"],
        ["src/exceptions.py"],
        "claude-sonnet-4-6",
        "high",
        root,
    ).key
    seen.record([key])


def test_passes_silently_when_the_judgment_is_cached(repo: Path) -> None:
    _record(repo)

    assert_judgment_cached("j1")  # a cache hit does not raise


def test_fails_with_a_factual_cache_miss_when_uncached(repo: Path) -> None:
    with pytest.raises(AssertionError, match="j1.*cache miss"):
        assert_judgment_cached("j1")


def test_unknown_id_raises_a_loud_error_not_a_silent_pass(repo: Path) -> None:
    with pytest.raises(ValueError, match="unknown judgment id"):
        assert_judgment_cached("nonexistent")


def test_missing_evidence_file_raises_a_loud_error(repo: Path) -> None:
    (repo / "docs" / "errors.md").unlink()

    with pytest.raises(FileNotFoundError):
        assert_judgment_cached("j1")
