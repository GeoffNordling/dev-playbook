"""No-token check of stint.py's stop rules: a scripted fake step plays every agent.

Each case runs the driver on a small git repository of its own, seeded with
the wordcount plan, where the fake step does what an agent would and one call
misbehaves. Prints PASS or FAIL per case and exits with the number of fails.

Usage: python3 rules.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

RIG = Path(__file__).resolve().parent
sys.path.insert(0, str(RIG))
import stint  # noqa: E402

LAB = Path(tempfile.mkdtemp(prefix="stint-rules-"))


def git(copy, *a):
    """Run the version-control tool in the copy and return its output."""
    return subprocess.run(
        ["git", "-C", str(copy), *a], check=True, capture_output=True, text=True
    ).stdout


def fresh():
    """A new copy holding only the seeded plan, committed."""
    shutil.rmtree(LAB, ignore_errors=True)
    copy = LAB / "mc"
    ws = copy / "ws"
    ws.mkdir(parents=True)
    for f in ("WORKSTREAM", "PLAN", "PROGRESS"):
        shutil.copy(RIG / "seed/wordcount" / f"{f}.md.in", ws / f"{f}.md")
    git(copy, "init", "-q", "-b", "main")
    git(copy, "add", "-A")
    git(copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
    return copy


def commit(copy, msg):
    """Commit everything in the copy and return the new SHA."""
    git(copy, "add", "-A")
    git(copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", msg)
    return git(copy, "rev-parse", "HEAD").strip()


def check_first(copy, old, new):
    """Replace the first `old` in the plan with `new`."""
    p = copy / "ws/PLAN.md"
    p.write_text(p.read_text().replace(old, new, 1))


def fake(behave):
    """A step whose agents do the plan's bookkeeping, with `behave` overriding one call."""

    def step(args, name, prompt, resume):
        copy = args.copy
        rec = {
            "name": name,
            "session": resume or f"s-{name}",
            "resumed": resume,
            "apiKeySource": "none",
            "seconds": 0,
            "isError": False,
            "commits": [],
            "uncommitted": [],
            "answer": "",
            "usage": {
                "inputTokens": 2,
                "cacheCreationInputTokens": 300,
                "cacheReadInputTokens": 10000 * (int(name.split("-")[1]) + 1)
                if name.startswith("principal")
                else 5000,
                "outputTokens": 100,
            },
        }
        out = behave(name, copy, rec)
        if out is not None:
            return out
        if name.startswith("principal-0"):
            rec["answer"] = (
                'Ready.\n\n```json\n{"verdict": "launch", "reason": "ok"}\n```'
            )
        elif name.startswith("iter"):
            check_first(copy, "- [ ] ", "- [x] ")
            rec["commits"] = [commit(copy, name)]
            rec["answer"] = (
                f'`{{"summary": "{name}", "tasksLeft": 0, "blocker": null}}`'
            )
        elif name.startswith("review"):
            rec["answer"] = "0 findings"
        else:
            check_first(copy, stint.OPEN_MARK, stint.DONE_MARK)
            rec["commits"] = [commit(copy, name)]
            left = "- [ ] " in (copy / "ws/PLAN.md").read_text()
            rec["answer"] = json.dumps(
                {"verdict": "continue" if left else "done", "reason": "r"}
            )
        return rec

    return step


def run(behave, budget=6):
    """Run the driver with the fake step; return the yield reason and the stint."""
    copy = fresh()
    args = SimpleNamespace(
        lab=LAB,
        copy=copy,
        stint=LAB,
        workstream="ws",
        check="true",
        budget=budget,
        model="m",
    )
    s = stint.Stint(args)
    s.step = fake(behave)
    try:
        return s.run(), s
    except stint.Yield as y:
        return str(y), s


def dirty(name, copy, rec):
    """iter-2 leaves a file uncommitted."""
    if name == "iter-2":
        (copy / "junk").write_text("x")
        rec["uncommitted"] = ["?? junk"]
        rec["answer"] = '{"summary": "s", "tasksLeft": 0, "blocker": null}'
        return rec


def two_tasks(name, copy, rec):
    """iter-1 checks off two tasks."""
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        check_first(copy, "- [ ] ", "- [x] ")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "tasksLeft": 0, "blocker": null}'
        return rec


def marker(name, copy, rec):
    """iter-1 checks off a checkpoint marker."""
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        check_first(copy, stint.OPEN_MARK, stint.DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "tasksLeft": 0, "blocker": null}'
        return rec


def link(name, copy, rec):
    """iter-1 replaces the plan with a link to a host file."""
    if name == "iter-1":
        secret = LAB / "host-secret"
        secret.write_text("secret")
        (copy / "ws/PLAN.md").unlink()
        os.symlink(secret, copy / "ws/PLAN.md")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"summary": "s", "tasksLeft": 0, "blocker": null}'
        return rec


def prose(name, copy, rec):
    """principal-1 answers with no JSON line."""
    if name == "review-1":
        rec["answer"] = "0 findings"
        return rec
    if name == "principal-1":
        check_first(copy, stint.OPEN_MARK, stint.DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = "All good, carry on."
        return rec


def lying_head(name, copy, rec):
    """iter-1 reports a commit that is not the copy's HEAD."""
    if name == "iter-1":
        check_first(copy, "- [ ] ", "- [x] ")
        commit(copy, "a")
        rec["commits"] = ["0" * 40]
        rec["answer"] = '{"summary": "s", "tasksLeft": 0, "blocker": null}'
        return rec


def reviewer_writes(name, copy, rec):
    """review-1 commits a file."""
    if name == "review-1":
        (copy / "fix").write_text("x")
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = "0 findings"
        return rec


def budget_eaten(name, copy, rec):
    """principal-1 adds a fix task, so four iterations cannot finish the plan."""
    if name == "principal-1":
        check_first(copy, stint.OPEN_MARK, stint.DONE_MARK)
        check_first(copy, stint.OPEN_MARK, "- [ ] Fix it\n" + stint.OPEN_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"verdict": "continue", "reason": "r"}'
        return rec


def no_usage(name, copy, rec):
    """principal-1 does its bookkeeping but reports no token usage."""
    if name == "principal-1":
        check_first(copy, stint.OPEN_MARK, stint.DONE_MARK)
        rec["commits"] = [commit(copy, name)]
        rec["answer"] = '{"verdict": "continue", "reason": "r"}'
        del rec["usage"]
        return rec


CASES = [
    ("happy path", lambda n, c, r: None, 6, "done"),
    (
        "plan bigger than budget",
        lambda n, c, r: None,
        3,
        "not launched: 4 tasks, budget 3",
    ),
    ("budget runs out", budget_eaten, 4, "budget: 4 of 4 iterations spent"),
    ("uncommitted work", dirty, 6, "iter-2 left work uncommitted"),
    ("marker moved", marker, 6, "iter-1 moved a checkpoint marker"),
    ("plan is a symlink", link, 6, "symlink in the copy: ws/PLAN.md"),
    ("no JSON ending", prose, 6, "the answer's last line is not JSON"),
    (
        "record lies about HEAD",
        lying_head,
        6,
        "iter-1: the copy's HEAD is not the call's last commit",
    ),
    ("reviewer commits", reviewer_writes, 6, "review-1 committed"),
    ("no token usage", no_usage, 6, "principal-1 reported no token usage"),
]
fails = 0
for label, behave, budget, want in CASES:
    got, s = run(behave, budget)
    ok = got.startswith(want)
    fails += not ok
    print(
        f"{'PASS' if ok else 'FAIL'} {label}: {got}  [calls: {' '.join(c['name'] for c in s.calls)}]"
    )
got, s = run(lambda n, c, r: None)
resumes = [c["resumed"] for c in s.calls if c["name"].startswith("principal")]
ok = resumes == [None, "s-principal-0", "s-principal-0"]
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} principal resumed with its own session: {resumes}")
got, s = run(lambda n, c, r: None)
ok = s.context == [
    {"call": "principal-0", "tokens": 10402},
    {"call": "principal-1", "tokens": 20402},
    {"call": "principal-2", "tokens": 30402},
]
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} principal context recorded per call: {s.context}")
got, s = run(two_tasks)
ok = got == "done" and s.notes == ["iter-1 checked off 2 tasks, not 1"]
fails += not ok
print(
    f"{'PASS' if ok else 'FAIL'} two tasks in one is noted, not stopped: {got}, {s.notes}"
)
shutil.rmtree(LAB)
sys.exit(fails)
