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
from dev_playbook.stint.call import CallFault
from dev_playbook.stint.loop import SHOWN, Assignment, Loop, Stop, shown
from dev_playbook.stint.plan import DONE_MARK, OPEN_MARK
from dev_playbook.stint.records import CallRecord, CheckRecord, StintRecord, Usage

PLAN = f"""\
# Plan

- [ ] one
- [ ] two
{OPEN_MARK}
- [ ] three
- [ ] four
{OPEN_MARK}
"""

HEAD_FILE = (
    "---\ntype: Workstream\n---\n\n# WS\n\n## Stints\n\n"
    "- **Planned.** Budget: six. Targets: `ws.one`.\n"
)
DRAFT = "---\ntype: Standard\n---\n\n# Draft\n\n`ws.one` · deterministic\n"
NOTES = "---\ntype: General-Sheet\n---\n\n# Notes\n"

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
    (copy / "ws" / "rules").mkdir(parents=True)
    (copy / "ws" / "PLAN.md").write_text(PLAN)
    (copy / "ws" / "WORKSTREAM.md").write_text(HEAD_FILE)
    (copy / "ws" / "rules" / "draft.md").write_text(DRAFT)
    (copy / "ws" / "rules" / "notes.md").write_text(NOTES)
    (copy / "ws" / "check").write_text("#!/bin/sh\nexit 0\n")
    (copy / "ws" / "check").chmod(0o755)
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
            rec["answer"] = f'`{{"summary": "{name}", "stuck": null}}`'
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


Exits = Callable[[str], int]
"""The target check's exit code at each of its runs, by the run's name."""


def clean(name: str) -> int:
    return 0


def checker(exits: Exits) -> Callable[[str, str], CheckRecord]:
    """A check that reports one finding line per nonzero exit, and writes nothing."""

    def check(name: str, command: str) -> CheckRecord:
        code = exits(name)
        output = [f"finding at {name}"] if code else []
        return CheckRecord(name, 0, code, output, [])

    return check


def run(
    copy: Path, behave: Behave, budget: int = 6, exits: Exits = clean
) -> tuple[str, StintRecord]:
    """Run the loop; return ``done`` or the stop's reason, and the record."""
    record = StintRecord(reason="", budget=budget)
    work = Assignment(copy=copy, repo="/r", workstream="ws", budget=budget)
    try:
        Loop(work, fake(copy, behave), checker(exits), record, copy.parent).run()
        return "done", record
    except Stop as stop:
        return str(stop), record


def honest(name: str, copy: Path, rec: dict) -> dict | None:
    return None


def dirty(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-2":
        (copy / "junk").write_text("x")
        rec["uncommitted"] = ["?? junk"]
        rec["answer"] = '{"summary": "s", "stuck": null}'
        return rec
    return None


def marker(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        check_first(copy, OPEN_MARK, DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "stuck": null}'
        return rec
    return None


def link(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        secret = copy.parent / "host-secret"
        secret.write_text("secret")
        (copy / "ws" / "PLAN.md").unlink()
        os.symlink(secret, copy / "ws" / "PLAN.md")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "stuck": null}'
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
        rec["answer"] = '{"summary": "s", "stuck": null}'
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


def get_stuck(copy: Path, name: str, rec: dict) -> dict:
    """Log why, commit it, and report stuck, as a stuck iteration does."""
    (copy / "ws" / "PROGRESS.md").write_text("- stuck: one — the spec is missing\n")
    rec["commits"] = [commit(copy, name)]
    rec["answer"] = '{"summary": "s", "stuck": "the spec is missing"}'
    return rec


def stuck(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        return get_stuck(copy, name, rec)
    return None


def idle(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        rec["answer"] = '{"summary": "s", "stuck": null}'
        return rec
    return None


def edit(rel: str, caller: str) -> Behave:
    """A behavior in which ``caller`` does its usual work and also edits ``rel``."""

    def behave(name: str, copy: Path, rec: dict) -> dict | None:
        if name != caller:
            return None
        (copy / rel).write_text("changed\n")
        if name.startswith("iter"):
            check_first(copy, "- [ ] ", "- [x] ")
            rec["answer"] = '{"summary": "s", "stuck": null}'
        else:
            check_first(copy, OPEN_MARK, DONE_MARK)
            rec["answer"] = '{"verdict": "continue", "reason": "r"}'
        rec["commits"] = [commit(copy, name)]
        return rec

    return behave


def faulted(name: str, copy: Path, rec: dict) -> dict | None:
    if name == "iter-1":
        raise CallFault("run.mjs exited 1")
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
        (stuck, 6, "principal-1 left 2 unchecked tasks above the checkpoint"),
        (idle, 6, "segment 1 has no commits to review"),
        (faulted, 6, "iter-1: run.mjs exited 1"),
        (
            edit("ws/WORKSTREAM.md", "iter-1"),
            6,
            "iter-1 changed the target: ws/WORKSTREAM.md",
        ),
        (
            edit("ws/rules/draft.md", "principal-1"),
            6,
            "principal-1 changed the target: ws/rules/draft.md",
        ),
        (edit("ws/check", "iter-2"), 6, "iter-2 changed the target: ws/check"),
    ],
)
def test_a_rule_stops_the_stint(
    copy: Path, behave: Behave, budget: int, want: str
) -> None:
    got, _ = run(copy, behave, budget)
    assert got.startswith(want)


def test_a_workstream_with_no_target_is_not_launched(copy: Path) -> None:
    (copy / "ws" / "check").chmod(0o644)
    got, record = run(copy, honest)
    assert got == "not launched: ws/check is not an executable file"
    assert record.calls == []


def test_the_check_runs_the_targeted_rules(copy: Path) -> None:
    commands: list[str] = []
    inner = checker(clean)

    def spy(name: str, command: str) -> CheckRecord:
        commands.append(command)
        return inner(name, command)

    record = StintRecord(reason="", budget=6)
    work = Assignment(copy=copy, repo="/r", workstream="ws", budget=6)
    Loop(work, fake(copy, honest), spy, record, copy.parent).run()
    assert commands == ["ws/check ws.one", "ws/check ws.one"]


def test_a_file_that_is_not_a_standard_may_change(copy: Path) -> None:
    got, _ = run(copy, edit("ws/rules/notes.md", "iter-1"))
    assert got == "done"


def test_a_deleted_draft_standard_stops_the_stint(copy: Path) -> None:
    def delete(name: str, copy: Path, rec: dict) -> dict | None:
        if name == "iter-1":
            (copy / "ws" / "rules" / "draft.md").unlink()
            check_first(copy, "- [ ] ", "- [x] ")
            rec["commits"] = [commit(copy, name)]
            rec["answer"] = '{"summary": "s", "stuck": null}'
            return rec
        return None

    got, _ = run(copy, delete)
    assert got == "iter-1 changed the target: ws/rules/draft.md"


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
            rec["answer"] = '{"summary": "s", "stuck": null}'
            return rec
        return None

    got, record = run(copy, two_tasks)
    assert got == "done"
    assert record.notes == ["iter-1 checked off 2 tasks, not 1"]


def test_each_review_is_kept_in_the_folder(copy: Path) -> None:
    run(copy, honest)
    assert (copy.parent / "review-1.md").read_text() == "0 findings\n"
    assert (copy.parent / "review-2.md").is_file()


def test_findings_before_the_end_are_a_signal_not_a_stop(copy: Path) -> None:
    got, record = run(copy, honest, exits=lambda name: int(name == "check-1"))
    assert got == "done"
    assert [c.exit for c in record.checks] == [1, 0]


def test_a_done_while_the_check_reports_findings_is_refused(copy: Path) -> None:
    got, _ = run(copy, honest, exits=lambda name: 1)
    assert got == "principal-2 said done while the check reports findings (exit 1)"


def test_the_principal_is_shown_the_checks_output(copy: Path) -> None:
    prompts: dict[str, str] = {}
    inner = fake(copy, honest)

    def spy(name: str, prompt: str, resume: str | None) -> CallRecord:
        prompts[name] = prompt
        return inner(name, prompt, resume)

    record = StintRecord(reason="", budget=6)
    work = Assignment(copy=copy, repo="/r", workstream="ws", budget=6)
    exits = checker(lambda name: int(name == "check-1"))
    Loop(work, spy, exits, record, copy.parent).run()
    assert "It exited 1;" in prompts["principal-1"]
    assert "finding at check-1" in prompts["principal-1"]
    assert (copy.parent / "check-1.txt").read_text() == "finding at check-1\nexit 1\n"


def test_long_check_output_is_cut_for_the_principal() -> None:
    cut = shown([f"f{i}" for i in range(SHOWN + 3)]).splitlines()
    assert len(cut) == SHOWN + 1
    assert cut[-1] == "(3 more lines not shown)"


def test_a_stuck_iteration_ends_its_segment_for_the_principal(copy: Path) -> None:
    def replan(name: str, copy: Path, rec: dict) -> dict | None:
        if name == "iter-1":
            return get_stuck(copy, name, rec)
        if name == "principal-1":
            plan = copy / "ws" / "PLAN.md"
            tasks = "- [ ] one\n- [ ] two\n- [ ] three\n- [ ] four\n"
            plan.write_text(f"# Plan\n\n{DONE_MARK}\n{tasks}{OPEN_MARK}\n")
            rec["commits"] = [commit(copy, name)]
            rec["answer"] = '{"verdict": "continue", "reason": "r"}'
            return rec
        return None

    got, record = run(copy, replan)
    assert got == "done"
    assert [c.name for c in record.calls][:4] == [
        "principal-0",
        "iter-1",
        "review-1",
        "principal-1",
    ]
    assert record.notes == [
        "iter-1 stuck: the spec is missing",
        "iter-1 checked off 0 tasks, not 1",
    ]


def test_a_check_that_leaves_files_stops_the_stint(copy: Path) -> None:
    def messy(name: str, command: str) -> CheckRecord:
        return CheckRecord(name, 0, 0, [], ["?? .cache/x"])

    record = StintRecord(reason="", budget=6)
    work = Assignment(copy=copy, repo="/r", workstream="ws", budget=6)
    loop = Loop(work, fake(copy, honest), messy, record, copy.parent)
    with pytest.raises(Stop, match="check-1 left work uncommitted"):
        loop.run()
