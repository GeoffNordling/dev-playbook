"""Behavioral tests for scripts/bump-pins.

The rewrite is the dangerous half — it edits files in repos outside this one —
so it is tested directly and exhaustively against real canonical-shaped configs.
Preflight is tested over throwaway git repos built by the shared fixture, with
no network and no gate run: every case it covers is a refusal reached before any
gate would fire.
"""

from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook import bump_pins, workspace_lint

URL = "https://github.com/GeoffNordling/dev-playbook"

CONFIG = """\
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: 6cf8a2b554db3b22edcbca40186bdc12b71a1e41
    hooks:
      - id: playbook-lint
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.20
    hooks:
      - id: ruff-check
"""

OLD = "6cf8a2b554db3b22edcbca40186bdc12b71a1e41"
NEW = "44848f72aecd73a64e9a0a4487e1e2ded0305199"


def write_consumer(root: Path, config: str) -> Path:
    """A throwaway git repo on main, clean, carrying ``config``."""
    init_repo(root)
    (root / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
    commit_all(root)
    return root


def refusal(repo: Path) -> bump_pins.Outcome:
    """Preflight's refusal for ``repo``, failing loudly when it does not refuse."""
    outcome = bump_pins.preflight(repo, URL, NEW)
    assert outcome is not None, "expected preflight to refuse this repo"
    return outcome


def test_rewritten_moves_only_the_rev_line() -> None:
    updated, old = bump_pins.rewritten(CONFIG, URL, NEW)
    assert old == OLD
    assert workspace_lint.pinned_rev(updated, URL) == NEW
    changed = [
        (before, after)
        for before, after in zip(CONFIG.splitlines(), updated.splitlines(), strict=True)
        if before != after
    ]
    assert changed == [(f"    rev: {OLD}", f"    rev: {NEW}")]


def test_rewritten_leaves_other_repos_pins_alone() -> None:
    updated, _ = bump_pins.rewritten(CONFIG, URL, NEW)
    assert "rev: v0.15.20" in updated


def test_rewritten_preserves_the_trailing_newline() -> None:
    updated, _ = bump_pins.rewritten(CONFIG, URL, NEW)
    assert updated.endswith("\n")
    assert not updated.endswith("\n\n")


def test_rewritten_preserves_a_missing_trailing_newline() -> None:
    updated, _ = bump_pins.rewritten(CONFIG.rstrip("\n"), URL, NEW)
    assert not updated.endswith("\n")


def test_rewritten_is_idempotent() -> None:
    once, _ = bump_pins.rewritten(CONFIG, URL, NEW)
    twice, old = bump_pins.rewritten(once, URL, NEW)
    assert twice == once
    assert old == NEW


def test_rewritten_refuses_a_config_with_no_such_pin() -> None:
    without = CONFIG.replace(URL, "https://github.com/other/repo")
    with pytest.raises(bump_pins.ToolError, match="no .* pin to move"):
        bump_pins.rewritten(without, URL, NEW)


def test_preflight_passes_a_clean_current_consumer(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    assert bump_pins.preflight(repo, URL, NEW) is None


def test_preflight_skips_a_repo_already_at_the_target(tmp_path: Path) -> None:
    updated, _ = bump_pins.rewritten(CONFIG, URL, NEW)
    outcome = refusal(write_consumer(tmp_path / "consumer", updated))
    assert outcome.status == bump_pins.CURRENT
    assert not outcome.open_work


def test_preflight_skips_a_dirty_repo(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    (repo / "scratch.txt").write_text("work in progress", encoding="utf-8")
    assert refusal(repo).status == bump_pins.DIRTY


def test_preflight_skips_a_repo_off_main(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    bump_pins.git_out(repo, "checkout", "-b", "issue-12")
    outcome = refusal(repo)
    assert outcome.status == bump_pins.OFF_MAIN
    assert "issue-12" in outcome.detail


def test_preflight_flags_a_consumer_carrying_no_pin(tmp_path: Path) -> None:
    without = CONFIG.replace(URL, "https://github.com/other/repo")
    outcome = refusal(write_consumer(tmp_path / "consumer", without))
    assert outcome.status == bump_pins.NO_PIN
    assert outcome.open_work


def test_preflight_flags_a_consumer_with_no_config_at_all(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    init_repo(repo)
    outcome = refusal(repo)
    assert outcome.status == bump_pins.NO_PIN
    assert outcome.open_work
