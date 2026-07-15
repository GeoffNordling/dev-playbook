"""Behavioral tests for assert_judgement_cached: the pytest cache-gate helper."""

from pathlib import Path

import pytest

from dev_playbook.judgements.core import prepare
from dev_playbook.judgements.pytest_support import assert_judgement_cached
from dev_playbook.skipcache import seen

CONFIG = '[tool.judgements]\npaths = ["judgements/*.yaml"]\n'

ONE_JUDGEMENT = """\
judgements:
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
    """Stand up a judgements repo, chdir into it, and isolate the seen-set cache.

    Also clears any ambient ``SKIP_JUDGEMENTS`` so the gate runs by default; the
    make targets export it (``=1`` under ``make test``), and a leaked value would
    silently turn these gate-behaviour tests into skips. Tests that exercise the
    skip lever set the variable themselves.
    """
    root = tmp_path / "repo"
    for relpath, contents in {
        "pyproject.toml": CONFIG,
        "judgements/a.yaml": ONE_JUDGEMENT,
        **EVIDENCE,
    }.items():
        path = root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    monkeypatch.chdir(root)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.delenv("SKIP_JUDGEMENTS", raising=False)
    return root


def _record(root: Path) -> None:
    """Record the fixture judgement's key, so its cache gate would pass."""
    key = prepare(
        "docs/errors.md lists every exception src/exceptions.py raises.",
        ["docs/errors.md"],
        ["src/exceptions.py"],
        "claude-sonnet-4-6",
        "high",
        root,
    ).key
    seen.record([key])


def test_passes_silently_when_the_judgement_is_cached(repo: Path) -> None:
    _record(repo)

    assert_judgement_cached("j1")  # a cache hit does not raise


def test_fails_with_a_factual_cache_miss_when_uncached(repo: Path) -> None:
    with pytest.raises(AssertionError, match="j1.*cache miss"):
        assert_judgement_cached("j1")


def test_unknown_id_raises_a_loud_error_not_a_silent_pass(repo: Path) -> None:
    with pytest.raises(ValueError, match="unknown judgement id"):
        assert_judgement_cached("nonexistent")


def test_missing_evidence_file_raises_a_loud_error(repo: Path) -> None:
    (repo / "docs" / "errors.md").unlink()

    with pytest.raises(FileNotFoundError):
        assert_judgement_cached("j1")


def test_skip_judgements_1_skips_the_gate_visibly(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SKIP_JUDGEMENTS", "1")

    # An uncached judgement: without the skip lever this would fail the gate, so
    # the skip must short-circuit before the cache check -- and as a real pytest
    # skip (visible in the summary), naming the id.
    with pytest.raises(pytest.skip.Exception, match="j1"):
        assert_judgement_cached("j1")


def test_skip_judgements_0_arms_the_gate(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SKIP_JUDGEMENTS", "0")

    with pytest.raises(AssertionError, match="j1.*cache miss"):
        assert_judgement_cached("j1")


def test_only_the_literal_1_arms_the_skip(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Any value other than the literal "1" runs the gate -- the tripwire cannot
    # be disarmed by a truthy-looking string.
    monkeypatch.setenv("SKIP_JUDGEMENTS", "true")

    with pytest.raises(AssertionError, match="j1.*cache miss"):
        assert_judgement_cached("j1")
