"""The whole stint around a fake Sandcastle: both copies made, the branch landed.

The fake runner plays Node and every agent: it edits and commits in the work
copy as the agent would, and answers with the stream Claude would print. No
container and no tokens.
"""

import json
import sqlite3
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from dev_playbook.checks.billing import BILLING_ENV_VARS
from dev_playbook.errors import ToolError
from dev_playbook.gitrepo import no_git_env
from dev_playbook.stint.launch import Host, Order, launch
from dev_playbook.stint.plan import DONE_MARK, OPEN_MARK
from dev_playbook.stint.workcopy import CopyFault

PLAN = f"- [ ] one\n{OPEN_MARK}\n- [ ] two\n{OPEN_MARK}\n"
INIT = json.dumps({"type": "system", "subtype": "init", "apiKeySource": "none"})
USAGE = {
    "inputTokens": 2,
    "cacheCreationInputTokens": 300,
    "cacheReadInputTokens": 10000,
    "outputTokens": 100,
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        env=no_git_env(),
    ).stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def tick(copy: Path, old: str, new: str) -> None:
    plan = copy / "ws" / "PLAN.md"
    plan.write_text(plan.read_text().replace(old, new, 1))


def agent(name: str, copy: Path) -> tuple[str, list[str]]:
    """What each agent does in the copy: its answer and its commits."""
    if name == "principal-0":
        return '{"verdict": "launch", "reason": "ok"}', []
    if name.startswith("iter"):
        tick(copy, "- [ ] ", "- [x] ")
        return '{"summary": "s", "blocker": null}', [commit(copy, name)]
    if name.startswith("review"):
        return "0 findings", []
    tick(copy, OPEN_MARK, DONE_MARK)
    left = "- [ ] " in (copy / "ws" / "PLAN.md").read_text()
    verdict = "continue" if left else "done"
    return json.dumps({"verdict": verdict, "reason": "r"}), [commit(copy, name)]


def runner(request: dict) -> dict:
    if request["job"] == "check":
        return {"exit": 0, "output": [], "probe": [""]}
    name = Path(request["log"]).stem
    answer, commits = agent(name, Path(request["copy"]))
    result = json.dumps({"type": "result", "result": answer, "is_error": False})
    return {
        "session": request["resume"] or f"s-{name}",
        "usage": USAGE,
        "commits": commits,
        "raw": [INIT, result],
        "probe": [],
    }


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in BILLING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    repo = tmp_path / "mc"
    (repo / "ws").mkdir(parents=True)
    (repo / "ws" / "PLAN.md").write_text(PLAN)
    (repo / ".pre-commit-config.yaml").write_text("repos: []\n")
    git(repo, "init", "-q", "-b", "main")
    commit(repo, "seed")
    git(repo, "branch", "-q", "seed")
    return repo


@pytest.fixture
def host(tmp_path: Path) -> Host:
    playbook = tmp_path / "dev-playbook"
    (playbook / "dotfiles" / "dot-claude").mkdir(parents=True)
    (playbook / "dotfiles" / "dot-claude" / "settings.json").write_text("{}")
    git(playbook, "init", "-q", "-b", "main")
    commit(playbook, "published")
    events = tmp_path / "events.db"
    with sqlite3.connect(events) as conn:
        conn.execute(
            "CREATE TABLE events (received_at, event, session_id, prompt_id, payload)"
        )
    (tmp_path / "credentials.json").write_text("secret")
    return Host(
        image="i",
        credentials=tmp_path / "credentials.json",
        events=events,
        runner=runner,
        workspace=tmp_path,
    )


def order(tmp_path: Path, repo: Path, name: str = "s1") -> Order:
    return Order(
        repo=repo,
        base="seed",
        workstream="ws",
        check="true",
        budget=6,
        name=name,
        home=tmp_path / "home",
        playbook=tmp_path / "dev-playbook",
        model="m",
    )


def test_a_stint_lands_its_branch_and_deletes_both_copies(
    tmp_path: Path, repo: Path, host: Host
) -> None:
    record = launch(order(tmp_path, repo), host)
    assert (record.reason, record.closed) == ("done", True)
    landed = git(repo, "log", "--format=%s", "seed..s1").split()
    assert landed == ["principal-2", "iter-2", "principal-1", "iter-1"]
    folder = tmp_path / "home" / "mc" / "s1"
    assert sorted(p.name for p in folder.iterdir()) == [
        "calls",
        "check-1.txt",
        "check-2.txt",
        "review-1.md",
        "review-2.md",
        "stint.json",
    ]
    assert json.loads((folder / "stint.json").read_text())["reason"] == "done"


def test_a_folder_already_there_is_refused(
    tmp_path: Path, repo: Path, host: Host
) -> None:
    (tmp_path / "home" / "mc" / "s1").mkdir(parents=True)
    with pytest.raises(ToolError, match="already exists"):
        launch(order(tmp_path, repo), host)


def test_a_failed_launch_still_writes_the_record(
    tmp_path: Path, repo: Path, host: Host
) -> None:
    git(repo, "branch", "-q", "s1")
    with pytest.raises(CopyFault, match="already holds a branch named s1"):
        launch(order(tmp_path, repo), host)
    folder = tmp_path / "home" / "mc" / "s1"
    written = json.loads((folder / "stint.json").read_text())
    assert written["reason"].startswith("the tool failed: ")
    assert not (folder / "config").exists()


def test_a_base_with_no_gate_is_refused(tmp_path: Path, repo: Path, host: Host) -> None:
    git(repo, "rm", "-q", ".pre-commit-config.yaml")
    commit(repo, "no gate")
    git(repo, "branch", "-q", "-f", "seed")
    with pytest.raises(ToolError, match="holds no .pre-commit-config.yaml"):
        launch(order(tmp_path, repo), host)
    assert not (tmp_path / "home").exists()


def test_a_copy_of_a_worktree_is_named_for_its_repository(
    tmp_path: Path, repo: Path, host: Host
) -> None:
    worktree = tmp_path / "feature-x"
    git(repo, "worktree", "add", "-q", str(worktree), "-b", "feature-x", "seed")
    copies: list[str] = []

    def spy(request: dict) -> dict:
        copies.append(request["copy"])
        return runner(request)

    spied = replace(host, runner=spy)
    record = launch(order(tmp_path, worktree), spied)
    assert record.reason == "done"
    assert {Path(c) for c in copies} == {tmp_path / "home" / "mc" / "s1" / "mc"}


def test_each_referenced_repo_gets_a_read_only_sibling_copy(
    tmp_path: Path, repo: Path, host: Host
) -> None:
    lib = tmp_path / "lib"
    (lib / "docs").mkdir(parents=True)
    (lib / "docs" / "a.md").write_text("published\n")
    git(lib, "init", "-q", "-b", "main")
    commit(lib, "lib")
    (repo / "ws" / "links.md").write_text(
        "See ~/workspace/lib/docs/a.md, ~/workspace/gone/b.md, and"
        " ~/workspace/mc/ws/PLAN.md.\n"
    )
    commit(repo, "links")
    git(repo, "branch", "-q", "-f", "seed")
    seen: list[dict[str, Path]] = []

    def spy(request: dict) -> dict:
        mounts = {
            m["sandboxPath"]: Path(m["hostPath"])
            for m in request["mounts"]
            if m["sandboxPath"].startswith("/home/agent/workspace/")
        }
        assert (mounts["/home/agent/workspace/lib"] / "docs" / "a.md").is_file()
        seen.append(mounts)
        return runner(request)

    launch(order(tmp_path, repo), replace(host, runner=spy))
    folder = tmp_path / "home" / "mc" / "s1"
    assert seen[0] == {
        "/home/agent/workspace/dev-playbook": folder / "config",
        "/home/agent/workspace/lib": folder / "siblings" / "lib",
    }
    assert not (folder / "siblings").exists()
