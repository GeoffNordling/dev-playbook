"""Behavioral tests for scripts/cascade.

The cascade pushes to other repos' ``main``, cuts worktrees in them, launches a
headless agent, and commits to dev-playbook — so every path is driven over
throwaway repos with a real bare ``origin``, and the three outside programs are
scripts: the gate (``bump_pins.GATE``), the agent (``cascade.CLAUDE``), and the
GitHub CLI (``cascade.GH``). The one fact about a red repo the ledger records,
the PR, is read through the scripted ``gh`` and never from the agent's output,
and the tests hold the cascade to that.
"""

import subprocess
from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook import bump_pins, cascade, workspace_lint
from dev_playbook.bump_pins import git_out

URL = "https://github.com/GeoffNordling/dev-playbook"
OLD = "6cf8a2b554db3b22edcbca40186bdc12b71a1e41"
NEW = "44848f72aecd73a64e9a0a4487e1e2ded0305199"
IDS = ("playbook-check",)
CONFIG = f"""\
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: {URL}
    rev: {OLD}
    hooks:
      - id: playbook-lint
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.20
    hooks:
      - id: ruff-check
"""
# The bump moves the rev and renames the hook id in one edit.
BUMPED = CONFIG.replace(OLD, NEW).replace("playbook-lint", "playbook-check")

PASSED = "playbook check Passed"
FINDINGS = "CLAUDE.md: harness.shape bad heading"
CRASH = "An unexpected error has occurred: Proxy CONNECT aborted"

NOW = "2026-09-23 14:00"
PR_URL = "https://github.com/me/consumer/pull/7"

LEDGER = f"""\
---
type: Log
title: Pin Cascade Ledger
description: test ledger
---

# Pin Cascade Ledger

## Runs

{cascade.LEDGER_HEADER}
{cascade.LEDGER_RULE}
| 2026-09-22 09:00 | {OLD[:12]} | consumer | green | main abcdef123456 | no unmerged branches |
| 2026-09-22 09:00 | {OLD[:12]} | other | red | PR {PR_URL} | unmerged: feat (2026-09-01, 3 ahead) |
"""


# --- fixtures ---


def bare_origin(path: Path) -> Path:
    subprocess.run(
        ["git", "init", "-q", "--bare", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )
    return path


def consumer(tmp_path: Path, config: str = CONFIG, name: str = "consumer") -> Path:
    """A clone of a bare origin, on ``main``, carrying ``config``, pushed.

    ``origin/main`` is a real remote-tracking ref of a real remote, so the
    fetch, the probe worktree, and the push all exercise the git they would in
    the workspace.
    """
    origin = bare_origin(tmp_path / f"{name}.git")
    repo = tmp_path / name
    init_repo(repo)
    git_out(repo, "config", "user.email", "t@example.com")
    git_out(repo, "config", "user.name", "T")
    git_out(repo, "remote", "add", "origin", str(origin))
    (repo / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
    (repo / "README.md").write_text("# consumer\n", encoding="utf-8")
    commit_all(repo)
    git_out(repo, "push", "-q", "-u", "origin", "main")
    return repo


def origin_main(repo: Path, path: str = ".pre-commit-config.yaml") -> str:
    """``path`` as the remote's ``main`` has it, byte for byte, after a fresh fetch."""
    git_out(repo, "fetch", "-q", "origin")
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"origin/main:{path}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def push_branch(repo: Path, name: str, merged: bool = False) -> None:
    """A remote branch ``name``: one commit ahead of main, or merged (equal to it)."""
    git_out(repo, "checkout", "-q", "-b", name)
    if not merged:
        (repo / f"{name}.txt").write_text(name, encoding="utf-8")
        commit_all(repo)
    git_out(repo, "push", "-q", "origin", name)
    git_out(repo, "checkout", "-q", "main")


def scripted_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, run: tuple[int, str] | None = None
) -> None:
    """Point the gate at a script answering ``run`` once; no ``run`` means any call is a crash.

    The cascade runs the gate once per repo, at the new pin, so one scripted
    answer is the whole contract; a second call, or a call where none is
    expected, exits 3, which the gate reports as "could not run".
    """
    script = tmp_path / "scripted-gate"
    counter = tmp_path / "gate-calls"
    code, output = run if run is not None else (3, "gate called when none was expected")
    script.write_text(
        "#!/bin/sh\n"
        f"n=$(cat {counter} 2>/dev/null || echo 0)\n"
        f"echo $((n + 1)) > {counter}\n"
        f"[ \"$n\" = 0 ] || {{ echo 'gate called twice'; exit 3; }}\n"
        f"cat <<'BODY'\n{output}\nBODY\n"
        f"exit {code}\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    monkeypatch.setattr(bump_pins, "GATE", (str(script),))


def scripted_gh(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """A ``gh`` whose ``pr list`` answers the contents of one file; that file."""
    pr_file = tmp_path / "open-pr-url"
    script = tmp_path / "scripted-gh"
    script.write_text(
        f"#!/bin/sh\ncat {pr_file} 2>/dev/null\nexit 0\n", encoding="utf-8"
    )
    script.chmod(0o755)
    monkeypatch.setattr(cascade, "GH", (str(script),))
    return pr_file


def scripted_agent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, pr_file: Path, opens_pr: bool
) -> Path:
    """A ``claude`` that records its cwd and argv, and opens a PR or not; the record.

    The record is the cwd, a newline, then the arguments separated by ``\\x1f``
    — the prompt spans lines, so a line per argument would not do.
    """
    record = tmp_path / "agent-call"
    open_pr = f"echo {PR_URL} > {pr_file}\n" if opens_pr else ""
    script = tmp_path / "scripted-claude"
    script.write_text(
        f"#!/bin/sh\npwd > {record}\n"
        f'for a in "$@"; do printf \'%s\\037\' "$a" >> {record}; done\n'
        f'{open_pr}echo \'{{"result": "done"}}\'\nexit 0\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    monkeypatch.setattr(cascade, "CLAUDE", (str(script),))
    return record


def cascade_one(repo: Path, tmp_path: Path, dry_run: bool = False) -> cascade.Row:
    return cascade.cascade_repo(
        repo, URL, NEW, IDS, now=NOW, run_dir=tmp_path / "state", dry_run=dry_run
    )


# --- the ledger ---


def test_ledger_rows_skips_the_header_and_the_rule() -> None:
    rows = cascade.ledger_rows(LEDGER)
    assert [row[2] for row in rows] == ["consumer", "other"]
    assert rows[1][4] == f"PR {PR_URL}"


def test_recorded_matches_the_head_by_its_twelve_character_prefix() -> None:
    assert cascade.recorded(LEDGER, OLD) == {"consumer", "other"}
    assert cascade.recorded(LEDGER, NEW) == set()


def test_recorded_is_empty_for_an_empty_ledger() -> None:
    assert cascade.recorded("", NEW) == set()


def test_row_render_keeps_a_pipe_out_of_the_table() -> None:
    row = cascade.Row(NOW, NEW, "consumer", "failed", "git said a | b", "")
    assert row.render() == (
        f"| {NOW} | {NEW[:12]} | consumer | failed | git said a / b |  |"
    )


def test_record_appends_the_rows_on_origin_main_and_touches_the_ledger_alone(
    tmp_path: Path,
) -> None:
    hook_repo = consumer(tmp_path, name="dev-playbook")
    (hook_repo / "docs").mkdir()
    (hook_repo / workspace_lint.LEDGER).write_text(LEDGER, encoding="utf-8")
    commit_all(hook_repo)
    git_out(hook_repo, "push", "-q", "origin", "main")
    rows = [
        cascade.Row(NOW, NEW, "consumer", "green", "main 123456789abc", "n"),
        cascade.Row(NOW, NEW, "other", "current", f"main pins {NEW[:12]}", "n"),
    ]

    sha = cascade.record(rows, hook_repo=hook_repo)

    text = origin_main(hook_repo, workspace_lint.LEDGER)
    assert text.endswith(rows[0].render() + "\n" + rows[1].render() + "\n")
    assert cascade.recorded(text, NEW) == {"consumer", "other"}
    assert git_out(hook_repo, "rev-parse", "origin/main") == sha
    touched = git_out(hook_repo, "show", "--name-only", "--format=", sha)
    assert touched == workspace_lint.LEDGER
    # The command's own checkout was never written.
    assert git_out(hook_repo, "status", "--porcelain") == ""
    assert (
        not (hook_repo / workspace_lint.LEDGER)
        .read_text()
        .endswith(rows[1].render() + "\n")
    )


def test_record_refuses_a_hook_repo_with_no_ledger(tmp_path: Path) -> None:
    hook_repo = consumer(tmp_path, name="dev-playbook")
    with pytest.raises(workspace_lint.ToolError, match="no docs/pin-cascade.md"):
        cascade.record([], hook_repo=hook_repo)


# --- reading one consumer ---


def test_pinned_on_main_reads_origin_main_not_the_checkout(tmp_path: Path) -> None:
    repo = consumer(tmp_path)
    (repo / ".pre-commit-config.yaml").write_text(BUMPED, encoding="utf-8")
    commit_all(repo)  # ahead of origin, unpushed
    assert cascade.pinned_on_main(repo, URL) == OLD


def test_pinned_on_main_refuses_a_tree_with_no_pin(tmp_path: Path) -> None:
    repo = consumer(tmp_path, config="repos: []\n")
    with pytest.raises(workspace_lint.ToolError, match="no .* pin on origin/main"):
        cascade.pinned_on_main(repo, URL)


def test_unmerged_branches_reports_only_branches_ahead_of_main(
    tmp_path: Path,
) -> None:
    repo = consumer(tmp_path)
    push_branch(repo, "feat-live")
    push_branch(repo, "old-merged", merged=True)
    cascade.fetch_all(repo)

    branches = cascade.unmerged_branches(repo)

    assert [(b.name, b.ahead) for b in branches] == [("feat-live", 1)]
    assert len(branches[0].date) == len("2026-09-23")
    assert cascade.branch_notes(branches).startswith("unmerged: feat-live (")
    assert cascade.branch_notes([]) == "no unmerged branches"


# --- one repo: current and green ---


def test_a_repo_already_at_the_head_is_current_and_runs_no_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path, config=BUMPED)
    scripted_gate(monkeypatch, tmp_path)  # any call exits 3
    row = cascade_one(repo, tmp_path)
    assert (row.verdict, row.landing) == ("current", f"main pins {NEW[:12]}")
    assert row.notes == "no unmerged branches"


def test_green_lands_one_commit_on_main_and_leaves_the_checkout_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    push_branch(repo, "feat-live")
    scripted_gate(monkeypatch, tmp_path, (0, PASSED))
    scripted_gh(monkeypatch, tmp_path)

    row = cascade_one(repo, tmp_path)

    assert row.verdict == "green"
    landed = git_out(repo, "rev-parse", "origin/main")
    assert row.landing == f"main {landed[:12]}"
    assert row.notes.startswith("unmerged: feat-live (")
    assert origin_main(repo) == BUMPED
    assert "Pin dev-playbook at " + NEW[:12] in git_out(
        repo, "log", "-1", "--format=%s", "origin/main"
    )
    # Exactly one commit, on top of what main had.
    assert git_out(repo, "rev-list", "--count", "main..origin/main") == "1"
    # The checkout still reads the old pin, clean, on main.
    assert (repo / ".pre-commit-config.yaml").read_text() == CONFIG
    assert git_out(repo, "status", "--porcelain") == ""
    assert "bump-pin-" not in git_out(repo, "worktree", "list")


def test_green_under_dry_run_pushes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (0, PASSED))
    scripted_gh(monkeypatch, tmp_path)
    row = cascade_one(repo, tmp_path, dry_run=True)
    assert (row.verdict, row.landing) == ("green", "dry run: not landed")
    assert origin_main(repo) == CONFIG


def test_a_gate_that_cannot_run_is_a_failed_row_not_a_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (3, "An unexpected error has occurred"))
    scripted_gh(monkeypatch, tmp_path)
    row = cascade_one(repo, tmp_path)
    assert row.verdict == "failed"
    assert "the gate could not run" in row.landing
    assert origin_main(repo) == CONFIG


# --- one repo: red ---


def test_red_cuts_a_worktree_runs_the_agent_there_and_records_the_pr_gh_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    push_branch(repo, "feat-live")
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    pr_file = scripted_gh(monkeypatch, tmp_path)
    call = scripted_agent(monkeypatch, tmp_path, pr_file, opens_pr=True)

    row = cascade_one(repo, tmp_path)

    branch = f"bump-pin-{NEW[:12]}"
    worktree = repo / ".claude" / "worktrees" / branch
    assert (row.verdict, row.landing) == ("red", f"PR {PR_URL}")
    assert row.notes.startswith("unmerged: feat-live (")
    # The worktree holds the moved pin as one commit on the named branch.
    assert worktree.is_dir()
    assert git_out(worktree, "rev-parse", "--abbrev-ref", "HEAD") == branch
    assert (worktree / ".pre-commit-config.yaml").read_text() == BUMPED
    assert git_out(worktree, "rev-list", "--count", "origin/main..HEAD") == "1"
    # The agent ran in the worktree, on the pinned model, told the state.
    cwd, _, rest = call.read_text().partition("\n")
    assert Path(cwd).resolve() == worktree.resolve()
    argv = rest.split("\x1f")
    assert argv[argv.index("--model") + 1] == "opus"
    assert argv[argv.index("--permission-mode") + 1] == "bypassPermissions"
    prompt = argv[argv.index("-p") + 1]
    assert OLD in prompt and NEW in prompt and branch in prompt
    assert "feat-live (" in prompt
    assert FINDINGS in prompt
    assert "Never merge the PR" in prompt
    # The transcript and the findings are on disk.
    assert (tmp_path / "state" / "consumer.log").read_text().startswith('{"result"')
    assert (tmp_path / "state" / "consumer.findings.txt").read_text() == FINDINGS + "\n"
    # main was not touched.
    assert origin_main(repo) == CONFIG


def test_red_with_no_pr_afterwards_is_failed_and_keeps_the_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    pr_file = scripted_gh(monkeypatch, tmp_path)
    scripted_agent(monkeypatch, tmp_path, pr_file, opens_pr=False)

    row = cascade_one(repo, tmp_path)

    worktree = repo / ".claude" / "worktrees" / f"bump-pin-{NEW[:12]}"
    assert row.verdict == "failed"
    assert "opened no PR" in row.landing
    assert str(worktree) in row.landing
    assert worktree.is_dir()


def test_red_refuses_to_launch_the_agent_on_a_metered_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    pr_file = scripted_gh(monkeypatch, tmp_path)
    call = scripted_agent(monkeypatch, tmp_path, pr_file, opens_pr=True)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-metered")

    row = cascade_one(repo, tmp_path)

    assert row.verdict == "failed"
    assert "ANTHROPIC_API_KEY" in row.landing
    assert not call.exists()


def test_an_open_pr_for_this_head_is_pending_and_runs_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path)  # any call exits 3
    pr_file = scripted_gh(monkeypatch, tmp_path)
    pr_file.write_text(PR_URL + "\n", encoding="utf-8")
    row = cascade_one(repo, tmp_path)
    assert (row.verdict, row.landing) == ("pending", f"PR {PR_URL}")


def test_red_refuses_a_worktree_left_by_an_earlier_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    pr_file = scripted_gh(monkeypatch, tmp_path)
    call = scripted_agent(monkeypatch, tmp_path, pr_file, opens_pr=True)
    stale = repo / ".claude" / "worktrees" / f"bump-pin-{NEW[:12]}"
    stale.mkdir(parents=True)

    row = cascade_one(repo, tmp_path)

    assert row.verdict == "failed"
    assert "already exists" in row.landing
    assert not call.exists()


def test_red_under_dry_run_prints_the_findings_and_cuts_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    repo = consumer(tmp_path)
    scripted_gate(monkeypatch, tmp_path, (1, FINDINGS))
    pr_file = scripted_gh(monkeypatch, tmp_path)
    call = scripted_agent(monkeypatch, tmp_path, pr_file, opens_pr=True)

    row = cascade_one(repo, tmp_path, dry_run=True)

    assert (row.verdict, row.landing) == ("red", "dry run: no branch cut")
    assert FINDINGS in capsys.readouterr().out
    assert not (repo / ".claude").exists()
    assert not call.exists()


def test_the_prompt_names_the_skill_and_forbids_the_merge() -> None:
    prompt = cascade.agent_prompt(
        "consumer",
        Path("/w"),
        "bump-pin-abc",
        OLD,
        NEW,
        IDS,
        [cascade.Branch("feat", "2026-09-01", 3)],
        FINDINGS,
    )
    assert "update-standards-pin/SKILL.md" in prompt
    assert "Work the findings" in prompt and "Land the PR" in prompt
    assert "- feat (2026-09-01, 3 ahead)" in prompt
    assert "gh pr create --base main --head bump-pin-abc" in prompt
    assert "No user is present" in prompt


# --- the run ---


def fake_github(
    monkeypatch: pytest.MonkeyPatch, ledger: str | None, head: str = NEW
) -> None:
    """Stand in for every GitHub read ``main`` makes."""
    monkeypatch.setattr(cascade, "release_head", lambda: head)
    monkeypatch.setattr(cascade, "published_hook_ids", lambda sha: IDS)
    monkeypatch.setattr(cascade, "hook_repo_url", lambda: URL)
    monkeypatch.setattr(cascade, "hook_repo_slug", lambda: "me/dev-playbook")
    monkeypatch.setattr(cascade, "published_file", lambda slug, path: ledger)
    monkeypatch.setattr(workspace_lint, "check_auth", lambda: None)
    monkeypatch.setattr(cascade, "is_hook_repo", lambda repo: False)


def test_main_exits_at_once_when_every_repo_is_recorded_at_the_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    ws = tmp_path / "ws"
    consumer(ws)
    fake_github(monkeypatch, LEDGER, head=OLD)
    scripted_gate(monkeypatch, tmp_path)  # any call exits 3

    code = cascade.main(["--workspace", str(ws), "--repos", "consumer"])

    assert code == 0
    assert "nothing to do" in capsys.readouterr().out


def test_main_dry_run_probes_the_unrecorded_repos_and_records_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    ws = tmp_path / "ws"
    repo = consumer(ws)
    fake_github(monkeypatch, LEDGER)  # rows at OLD, none at NEW
    scripted_gate(monkeypatch, tmp_path, (0, PASSED))
    scripted_gh(monkeypatch, tmp_path)
    monkeypatch.setattr(cascade, "STATE_DIR", tmp_path / "state")

    code = cascade.main(
        ["--workspace", str(ws), "--repos", "consumer,ghost", "--dry-run"]
    )

    out, err = capsys.readouterr()
    assert code == 0
    assert "consumer: green — dry run: not landed" in out
    assert "not on this machine, not moved: ghost" in err
    assert "nothing recorded" in err
    assert origin_main(repo) == CONFIG


def test_main_refuses_a_live_run_with_no_published_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    ws = tmp_path / "ws"
    consumer(ws)
    fake_github(monkeypatch, None)
    code = cascade.main(["--workspace", str(ws), "--repos", "consumer"])
    assert code == 2
    assert "cannot run without it" in capsys.readouterr().err


def test_main_dry_run_treats_a_missing_ledger_as_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    ws = tmp_path / "ws"
    consumer(ws)
    fake_github(monkeypatch, None)
    scripted_gate(monkeypatch, tmp_path, (0, PASSED))
    scripted_gh(monkeypatch, tmp_path)
    monkeypatch.setattr(cascade, "STATE_DIR", tmp_path / "state")
    code = cascade.main(["--workspace", str(ws), "--repos", "consumer", "--dry-run"])
    assert code == 0
    assert "consumer: green" in capsys.readouterr().out


def test_main_passes_the_hook_repo_over_by_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    ws = tmp_path / "ws"
    consumer(ws, name="dev-playbook")
    fake_github(monkeypatch, LEDGER)
    monkeypatch.setattr(
        cascade, "is_hook_repo", lambda repo: repo.name == "dev-playbook"
    )
    code = cascade.main(["--workspace", str(ws), "--repos", "dev-playbook"])
    assert code == 0
    assert "nothing to do" in capsys.readouterr().out


def test_bump_pins_gate_is_the_cascade_gate() -> None:
    # One gate for both writers: a test that scripts bump_pins.GATE scripts the
    # cascade's probe too, and the two cannot judge a repo differently.
    assert cascade.run_gate is bump_pins.run_gate
