"""Behavioral tests for scripts/bump-pin (``dev_playbook.pins.bump``).

Two dangerous halves. The rewrite edits files in repos outside this one, so it is
tested directly and exhaustively against real canonical-shaped configs. The probe
promises to leave the tree exactly as it found it — the promise the caller relies
on to choose where the durable edit lands — so every way the verify run can end
is driven through it and the config checked byte for byte afterwards.

Preflight and the probe run over throwaway git repos built by the shared fixture,
with no network and a scripted stand-in for the gate.
"""

from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook.errors import ToolError
from dev_playbook.pins import bump, config, gate, release, worktree

URL = "https://github.com/GeoffNordling/dev-playbook"

CONFIG = """\
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: https://github.com/GeoffNordling/dev-playbook
    rev: 6cf8a2b554db3b22edcbca40186bdc12b71a1e41
    hooks:
      - id: playbook-check
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.20
    hooks:
      - id: ruff-check
"""

OLD = "6cf8a2b554db3b22edcbca40186bdc12b71a1e41"
NEW = "44848f72aecd73a64e9a0a4487e1e2ded0305199"
IDS = ("playbook-check",)

# A consumer left at the pin before the hook was renamed: the id its block
# carries is one the manifest at NEW no longer publishes.
STALE_ID_CONFIG = CONFIG.replace("- id: playbook-check", "- id: playbook-lint")

MANIFEST = """\
- id: playbook-check
  name: playbook check
  entry: playbook check
  language: python
  pass_filenames: false
  always_run: true
"""

PASSED = "playbook check Passed"
FINDINGS = "CLAUDE.md: harness.shape bad heading"
CRASH = "An unexpected error has occurred: Proxy CONNECT aborted"


def write_consumer(root: Path, config: str) -> Path:
    """A throwaway git repo on main, clean, up to date, carrying ``config``.

    ``origin/main`` is a local ref rather than a real remote: the freshness check
    reads it like any other rev, and a test that needed a second repo to fetch
    from would be testing git.
    """
    init_repo(root)
    (root / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
    commit_all(root)
    worktree.git_out(root, "update-ref", "refs/remotes/origin/main", "main")
    return root


def scripted_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *runs: tuple[int, str]
) -> None:
    """Point the gate at a script giving ``runs[n]`` on its nth call.

    The baseline and the verify are two calls to one command, and they have to
    differ: the shape a lost network takes is a green baseline off the cached pin
    and a verify that cannot clone the new rev.
    """
    script = tmp_path / "scripted-gate"
    counter = tmp_path / "gate-calls"
    arms = "\n".join(
        f"  {n}) cat <<'BODY'\n{output}\nBODY\n     exit {code} ;;"
        for n, (code, output) in enumerate(runs, start=1)
    )
    script.write_text(
        "#!/bin/sh\n"
        f"n=$(cat {counter} 2>/dev/null || echo 0)\n"
        "n=$((n + 1))\n"
        f"echo $n > {counter}\n"
        "case $n in\n"
        f"{arms}\n"
        "  *) echo 'gate called more times than the test scripted'; exit 3 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    monkeypatch.setattr(gate, "GATE", (str(script),))


def config_of(repo: Path) -> str:
    """The repo's pre-commit config as it stands on disk."""
    return (repo / ".pre-commit-config.yaml").read_text(encoding="utf-8")


def test_rewritten_moves_only_the_rev_line() -> None:
    updated, old = config.rewritten(CONFIG, URL, NEW, IDS)
    assert old == OLD
    assert config.pinned_rev(updated, URL) == NEW
    changed = [
        (before, after)
        for before, after in zip(CONFIG.splitlines(), updated.splitlines(), strict=True)
        if before != after
    ]
    assert changed == [(f"    rev: {OLD}", f"    rev: {NEW}")]


def test_rewritten_leaves_other_repos_pins_alone() -> None:
    updated, _ = config.rewritten(CONFIG, URL, NEW, IDS)
    assert "rev: v0.15.20" in updated


def test_rewritten_preserves_the_trailing_newline() -> None:
    updated, _ = config.rewritten(CONFIG, URL, NEW, IDS)
    assert updated.endswith("\n")
    assert not updated.endswith("\n\n")


def test_rewritten_preserves_a_missing_trailing_newline() -> None:
    updated, _ = config.rewritten(CONFIG.rstrip("\n"), URL, NEW, IDS)
    assert not updated.endswith("\n")


def test_rewritten_is_idempotent() -> None:
    once, _ = config.rewritten(CONFIG, URL, NEW, IDS)
    twice, old = config.rewritten(once, URL, NEW, IDS)
    assert twice == once
    assert old == NEW


def test_rewritten_renames_a_stale_hook_id_with_the_rev() -> None:
    updated, old = config.rewritten(STALE_ID_CONFIG, URL, NEW, IDS)
    assert old == OLD
    assert updated == CONFIG.replace(OLD, NEW)


def test_rewritten_replaces_every_entry_under_hooks_with_the_published_ids() -> None:
    many = CONFIG.replace(
        "      - id: playbook-check\n",
        "      - id: playbook-lint\n      - id: skill-lint\n      - id: shape-lint\n",
    )
    updated, _ = config.rewritten(many, URL, NEW, ("playbook-check", "extra"))
    assert updated == CONFIG.replace(OLD, NEW).replace(
        "      - id: playbook-check\n",
        "      - id: playbook-check\n      - id: extra\n",
    )


def test_rewritten_leaves_the_last_block_of_the_file_intact() -> None:
    last = CONFIG.replace("      - id: ruff-check\n", "")  # dev-playbook block last
    last = last.split("  - repo: https://github.com/astral-sh")[0]
    updated, _ = config.rewritten(
        last.replace("playbook-check", "playbook-lint"), URL, NEW, IDS
    )
    assert updated == last.replace(OLD, NEW)


def test_rewritten_refuses_a_block_with_no_hooks_key() -> None:
    without = CONFIG.replace("    hooks:\n      - id: playbook-check\n", "", 1)
    with pytest.raises(ToolError, match="no hooks: key"):
        config.rewritten(without, URL, NEW, IDS)


def test_manifest_ids_reads_the_published_ids_in_order() -> None:
    assert release.manifest_ids(MANIFEST) == ("playbook-check",)
    assert release.manifest_ids(MANIFEST + "- id: second\n  entry: x\n") == (
        "playbook-check",
        "second",
    )


def test_manifest_ids_refuses_a_body_that_is_not_a_hook_list() -> None:
    with pytest.raises(ToolError, match="not a list of hooks"):
        release.manifest_ids("hooks: {}\n")


def test_rewritten_refuses_a_config_with_no_such_pin() -> None:
    without = CONFIG.replace(URL, "https://github.com/other/repo")
    with pytest.raises(ToolError, match="no .* pin to move"):
        config.rewritten(without, URL, NEW, IDS)


HOST_PYPROJECT = f"""\
[project]
name = "a-host"

[dependency-groups]
dev = ["dev-playbook"]

[tool.uv.sources]
dev-playbook = {{ git = "{URL}", rev = "{OLD}" }}
"""


def fake_uv_lock(monkeypatch: pytest.MonkeyPatch, returncode: int = 0) -> list[Path]:
    """Stand in for ``uv lock``; the list collects each directory it ran in."""
    ran: list[Path] = []

    def run(argv: list[str], *, cwd: Path, **_: object) -> object:
        assert argv == ["uv", "lock"]
        ran.append(cwd)
        return type("Done", (), {"returncode": returncode, "stderr": "no resolve"})

    monkeypatch.setattr(config.subprocess, "run", run)
    return ran


def test_move_pin_moves_the_config_alone_outside_a_host(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ran = fake_uv_lock(monkeypatch)
    (tmp_path / ".pre-commit-config.yaml").write_text(CONFIG)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "plain"\n')
    assert config.move_pin(tmp_path, URL, NEW, IDS) == (
        [".pre-commit-config.yaml"],
        OLD,
    )
    assert NEW in (tmp_path / ".pre-commit-config.yaml").read_text()
    assert ran == []


def test_move_pin_moves_a_hosts_source_and_relocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ran = fake_uv_lock(monkeypatch)
    (tmp_path / ".pre-commit-config.yaml").write_text(CONFIG)
    (tmp_path / "pyproject.toml").write_text(HOST_PYPROJECT)
    changed, old = config.move_pin(tmp_path, URL, NEW, IDS)
    assert changed == [".pre-commit-config.yaml", "pyproject.toml", "uv.lock"]
    assert old == OLD
    assert (tmp_path / "pyproject.toml").read_text() == HOST_PYPROJECT.replace(OLD, NEW)
    assert ran == [tmp_path]


def test_move_pin_refuses_a_git_source_it_cannot_move(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_uv_lock(monkeypatch)
    split = HOST_PYPROJECT.replace(
        f'dev-playbook = {{ git = "{URL}", rev = "{OLD}" }}',
        f'[tool.uv.sources.dev-playbook]\ngit = "{URL}"\nrev = "{OLD}"',
    ).replace("[tool.uv.sources]\n", "")
    (tmp_path / ".pre-commit-config.yaml").write_text(CONFIG)
    (tmp_path / "pyproject.toml").write_text(split)
    with pytest.raises(ToolError, match="not on one"):
        config.move_pin(tmp_path, URL, NEW, IDS)


def test_move_pin_fails_loud_when_uv_lock_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_uv_lock(monkeypatch, returncode=1)
    (tmp_path / ".pre-commit-config.yaml").write_text(CONFIG)
    (tmp_path / "pyproject.toml").write_text(HOST_PYPROJECT)
    with pytest.raises(ToolError, match="uv lock failed"):
        config.move_pin(tmp_path, URL, NEW, IDS)


def test_pinned_reads_the_current_rev(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    assert bump.pinned(repo, URL) == OLD


def test_pinned_refuses_a_consumer_carrying_no_pin(tmp_path: Path) -> None:
    without = CONFIG.replace(URL, "https://github.com/other/repo")
    repo = write_consumer(tmp_path / "consumer", without)
    with pytest.raises(ToolError, match="not a bump"):
        bump.pinned(repo, URL)


def test_pinned_refuses_a_consumer_with_no_config_at_all(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    init_repo(repo)
    with pytest.raises(ToolError, match="no .pre-commit-config.yaml"):
        bump.pinned(repo, URL)


def test_consumer_root_refuses_the_hook_repo() -> None:
    with pytest.raises(ToolError, match="dogfoods"):
        bump.consumer_root(release.HOOK_REPO_ROOT)


def test_require_clean_refuses_a_dirty_repo(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    (repo / "scratch.txt").write_text("work in progress", encoding="utf-8")
    with pytest.raises(ToolError, match="uncommitted changes"):
        bump.require_clean(repo)


def test_probe_worktree_checks_out_origin_main_and_removes_itself(
    tmp_path: Path,
) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    (repo / "later.txt").write_text("landed upstream", encoding="utf-8")
    commit_all(repo)
    worktree.git_out(repo, "update-ref", "refs/remotes/origin/main", "main")
    worktree.git_out(repo, "reset", "-q", "--hard", "HEAD~1")  # checkout behind
    with worktree.probe_worktree(repo) as tree:
        assert (tree / "later.txt").is_file()
        assert tree != repo
        assert "bump-pin-" in str(tree)
        kept = tree
    assert not kept.exists()
    assert "bump-pin-" not in worktree.git_out(repo, "worktree", "list")


def test_probe_worktree_is_removed_when_the_body_raises(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    with pytest.raises(RuntimeError), worktree.probe_worktree(repo) as tree:
        kept = tree
        raise RuntimeError("gate died")
    assert not kept.exists()
    assert "bump-pin-" not in worktree.git_out(repo, "worktree", "list")


def test_run_gate_reports_a_clean_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripted_gate(monkeypatch, tmp_path, (0, PASSED))
    passed, output = gate.run_gate(tmp_path)
    assert passed
    assert "Passed" in output


def test_run_gate_reports_findings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    passed, output = gate.run_gate(tmp_path)
    assert not passed
    assert "harness.shape" in output


def test_run_gate_refuses_to_call_a_crash_a_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripted_gate(monkeypatch, tmp_path, (3, CRASH))
    with pytest.raises(ToolError, match="could not run"):
        gate.run_gate(tmp_path)


def test_run_gate_refuses_a_fatal_error_wearing_the_findings_exit_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripted_gate(monkeypatch, tmp_path, (1, "An error has occurred: InvalidConfig"))
    with pytest.raises(ToolError, match="could not run"):
        gate.run_gate(tmp_path)


def test_check_reports_green_and_leaves_the_checkout_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    scripted_gate(monkeypatch, tmp_path, (0, PASSED), (0, PASSED))
    assert bump.check(repo, URL, NEW, IDS) == 0
    assert config_of(repo) == CONFIG
    assert not worktree.git_out(repo, "status", "--porcelain")
    assert "bump-pin-" not in worktree.git_out(repo, "worktree", "list")


def test_check_reports_red_and_leaves_the_checkout_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    scripted_gate(monkeypatch, tmp_path, (0, PASSED), (1, FINDINGS))
    assert bump.check(repo, URL, NEW, IDS) == 1
    assert config_of(repo) == CONFIG
    assert not worktree.git_out(repo, "status", "--porcelain")


def test_check_leaves_no_worktree_when_the_gate_cannot_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    scripted_gate(monkeypatch, tmp_path, (0, PASSED), (3, CRASH))
    with pytest.raises(ToolError, match="could not run"):
        bump.check(repo, URL, NEW, IDS)
    assert config_of(repo) == CONFIG
    assert "bump-pin-" not in worktree.git_out(repo, "worktree", "list")


def test_check_judges_origin_main_not_the_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A dirty checkout on a feature branch, behind main, is never in the way."""
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    worktree.git_out(repo, "checkout", "-q", "-b", "issue-12")
    (repo / "scratch.txt").write_text("work in progress", encoding="utf-8")
    scripted_gate(monkeypatch, tmp_path, (0, PASSED), (0, PASSED))
    assert bump.check(repo, URL, NEW, IDS) == 0
    assert (repo / "scratch.txt").is_file()
    assert worktree.git_out(repo, "branch", "--show-current") == "issue-12"


def test_check_refuses_a_repo_already_red_at_its_current_pin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    with pytest.raises(ToolError, match="already red at its current pin"):
        bump.check(repo, URL, NEW, IDS)
    assert config_of(repo) == CONFIG


def test_check_runs_no_gate_on_a_repo_already_at_the_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    updated, _ = config.rewritten(CONFIG, URL, NEW, IDS)
    repo = write_consumer(tmp_path / "consumer", updated)
    scripted_gate(monkeypatch, tmp_path)  # any call at all exits 3
    assert bump.check(repo, URL, NEW, IDS) == 0


def test_write_moves_the_pin_and_leaves_it(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    assert bump.write(repo, URL, NEW, IDS) == 0
    assert config.pinned_rev(config_of(repo), URL) == NEW


def test_write_serves_a_repo_off_main(tmp_path: Path) -> None:
    """The durable edit lands on the branch cut after a red probe, not on main."""
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    worktree.git_out(repo, "checkout", "-q", "-b", "bump-pin-44848f72aecd")
    assert bump.write(repo, URL, NEW, IDS) == 0
    assert config.pinned_rev(config_of(repo), URL) == NEW


def test_write_refuses_a_dirty_repo(tmp_path: Path) -> None:
    repo = write_consumer(tmp_path / "consumer", CONFIG)
    (repo / "scratch.txt").write_text("work in progress", encoding="utf-8")
    with pytest.raises(ToolError, match="uncommitted changes"):
        bump.write(repo, URL, NEW, IDS)


def test_write_leaves_a_repo_already_at_the_target_alone(tmp_path: Path) -> None:
    updated, _ = config.rewritten(CONFIG, URL, NEW, IDS)
    repo = write_consumer(tmp_path / "consumer", updated)
    assert bump.write(repo, URL, NEW, IDS) == 0
    assert config_of(repo) == updated
