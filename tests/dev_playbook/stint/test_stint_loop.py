"""The loop's stop rules, with a scripted fake call playing every agent.

Each test runs the loop on a small repository holding a four-task plan in two
segments. The fake call does what an agent would, and one call misbehaves.
No container and no tokens.
"""

import json
import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from dev_playbook.gitrepo import no_git_env
from dev_playbook.stint.loop import Assignment, Loop, Stop
from dev_playbook.stint.plan import DONE_MARK, OPEN_MARK
from dev_playbook.stint.records import CallRecord, StintRecord, Usage

PLAN = f"""\
# Plan

- [ ] one
- [ ] two
{OPEN_MARK}
- [ ] three
- [ ] four
{OPEN_MARK}
"""

Behave = Callable[[str, Path, dict], dict | None]


def git(copy: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(copy), *args],
        check=True,
        capture_output=True,
        text=True,
        env=no_git_env(),
    ).stdout.strip()


def commit(copy: Path, message: str) -> str:
    git(copy, "add", "-A")
    git(copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message)
    return git(copy, "rev-parse", "HEAD")


def check_first(copy: Path, old: str, new: str) -> None:
    plan = copy / "ws" / "PLAN.md"
    plan.write_text(plan.read_text().replace(old, new, 1))


@pytest.fixture
def copy(tmp_path: Path) -> Path:
    copy = tmp_path / "mc"
    (copy / "ws").mkdir(parents=True)
    (copy / "ws" / "PLAN.md").write_text(PLAN)
    git(copy, "init", "-q", "-b", "main")
    commit(copy, "seed")
    return copy


def fake(copy: Path, behave: Behave) -> Callable[[str, str, str | None], CallRecord]:
    """A call whose agents do the plan's bookkeeping, with ``behave`` overriding one."""

    def call(name: str, prompt: str, resume: str | None) -> CallRecord:
        n = int(name.split("-")[1])
        rec: dict = {
            "name": name,
            "session": resume or f"s-{name}",
            "resumed": resume,
            "api_key_source": "none",
            "seconds": 0,
            "is_error": False,
            "usage": Usage(2, 300, 10000 * (n + 1), 100)
            if name.startswith("principal")
            else Usage(2, 300, 5000, 100),
            "commits": [],
            "uncommitted": [],
            "answer": "",
        }
        if (out := behave(name, copy, rec)) is not None:
            return CallRecord(**out)
        if name == "principal-0":
            rec["answer"] = (
                'Ready.\n\n```json\n{"verdict": "launch", "reason": "ok"}\n```'
            )
        elif name.startswith("iter"):
            check_first(copy, "- [ ] ", "- [x] ")
            rec["commits"] = [commit(copy, name)]
            rec["answer"] = f'`{{"summary": "{name}", "blocker": null}}`'
        elif name.startswith("review"):
            rec["answer"] = "0 findings"
        else:
            check_first(copy, OPEN_MARK, DONE_MARK)
            rec["commits"] = [commit(copy, name)]
            left = "- [ ] " in (copy / "ws" / "PLAN.md").read_text()
            rec["answer"] = json.dumps(
                {"verdict": "continue" if left else "done", "reason": "r"}
            )
        return CallRecord(**rec)

    return call


def run(copy: Path, behave: Behave, budget: int = 6) -> tuple[str, StintRecord]:
    """Run the loop; return ``done`` or the stop's reason, and the record."""
    record = StintRecord(reason="", budget=budget)
    work = Assignment(
        copy=copy, repo="/r", workstream="ws", check="true", budget=budget
    )
    try:
        Loop(work, fake(copy, behave), record, copy.parent).run()
        return "done", record
    except Stop as stop:
        return str(stop), record


def honest(name: str, copy: Path, rec: dict) -> dict | None:
    return None


def dirty(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-2":
        (copy / "junk").write_text("x")
        rec["uncommitted"] = ["?? junk"]
        rec["answer"] = '{"summary": "s", "blocker": null}'
        return rec
    return None


def marker(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        check_first(copy, OPEN_MARK, DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "blocker": null}'
        return rec
    return None


def link(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        secret = copy.parent / "host-secret"
        secret.write_text("secret")
        (copy / "ws" / "PLAN.md").unlink()
        os.symlink(secret, copy / "ws" / "PLAN.md")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "blocker": null}'
        return rec
    return None


def prose(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "principal-1":
        check_first(copy, OPEN_MARK, DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = "All good, carry on."
        return rec
    return None


def lying_head(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        commit(copy, "a")
        rec["commits"] = ["0" * 40]
        rec["answer"] = '{"summary": "s", "blocker": null}'
        return rec
    return None


def reviewer_writes(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "review-1":
        (copy / "fix").write_text("x")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = "0 findings"
        return rec
    return None


def budget_eaten(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "principal-1":
        check_first(copy, OPEN_MARK, DONE_MARK)
        check_first(copy, OPEN_MARK, "- [ ] Fix it\n" + OPEN_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"verdict": "continue", "reason": "r"}'
        return rec
    return None


def no_usage(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "principal-1":
        check_first(copy, OPEN_MARK, DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"verdict": "continue", "reason": "r"}'
        rec["usage"] = None
        return rec
    return None


def blocked(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        rec["answer"] = '{"summary": "s", "blocker": "the spec is missing"}'
        return rec
    return None


def idle(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        rec["answer"] = '{"summary": "s", "blocker": null}'
        return rec
    return None


@pytest.mark.parametrize(
    ("behave", "budget", "want"),
    [
        (honest, 6, "done"),
        (honest, 3, "not launched: 4 tasks, budget 3"),
        (budget_eaten, 4, "budget: 4 of 4 iterations spent"),
        (dirty, 6, "iter-2 left work uncommitted"),
        (marker, 6, "iter-1 moved a checkpoint marker"),
        (link, 6, "symlink in the copy: ws/PLAN.md"),
        (prose, 6, "the answer's last line is not JSON"),
        (lying_head, 6, "iter-1: the copy's HEAD is not the call's last commit"),
        (reviewer_writes, 6, "review-1 committed"),
        (no_usage, 6, "principal-1 reported no token usage"),
        (blocked, 6, "iter-1 blocked: the spec is missing"),
        (idle, 6, "iter-1 committed nothing"),
    ],
)
def test_a_rule_stops_the_stint(
    copy: Path, behave: Behave, budget: int, want: str
) -> None:
    got, _ = run(copy, behave, budget)
    assert got.startswith(want)


def test_the_principal_resumes_its_own_session(copy: Path) -> None:
    _, record = run(copy, honest)
    resumed = [c.resumed for c in record.calls if c.name.startswith("principal")]
    assert resumed == [None, "s-principal-0", "s-principal-0"]


def test_the_principals_context_is_recorded_per_call(copy: Path) -> None:
    _, record = run(copy, honest)
    assert [(c.call, c.tokens) for c in record.principal_context] == [
        ("principal-0", 10402),
        ("principal-1", 20402),
        ("principal-2", 30402),
    ]


def test_two_tasks_in_one_is_noted_not_stopped(copy: Path) -> None:
    def two_tasks(name: str, copy: Path, rec: dict) -> dict | None:
        if name == "iter-1":
            check_first(copy, "- [ ] ", "- [x] ")
            check_first(copy, "- [ ] ", "- [x] ")
            rec["commits"] = [commit(copy, name)]
            rec["answer"] = '{"summary": "s", "blocker": null}'
            return rec
        return None

    got, record = run(copy, two_tasks)
    assert got == "done"
    assert record.notes == ["iter-1 checked off 2 tasks, not 1"]


def test_each_review_is_kept_in_the_folder(copy: Path) -> None:
    run(copy, honest)
    assert (copy.parent / "review-1.md").read_text() == "0 findings\n"
    assert (copy.parent / "review-2.md").is_file()
