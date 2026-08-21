import fcntl
import json
import signal
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest
from conftest import (
    commit_all,
    init_repo,
    ledger_rows,
    process_state,
    write_definition,
)

from dev_playbook.factory import launcher, ledger, traverse

# The issue every test traverses unless it says otherwise, and the checkout the
# slug resolves to inside the temp workspace.
REPO = "owner/repo"
NAME = "repo"
ISSUE = 440
BRANCH = f"issue-{ISSUE}"

# The labels a released `phase:build` issue carries.
BUILD_LABELS = ["mode:direct", "tests:yes", "phase:build"]
PR_REVIEW_LABELS = ["mode:direct", "tests:yes", "phase:pr-review"]

# The PR the stub gh reports once open-pr has run.
PR_URL = "https://github.com/owner/repo/pull/12"
PR_NUMBER = 12

# The review names the three reviewer definitions open their cycle headers with.
REVIEW_NAMES = {
    "bug-pr-review": "bug review",
    "code-pr-review": "code review",
    "doc-pr-review": "doc review",
}

# A stand-in for gh, answering every call the traverse makes off a real bare
# origin repo, so a sha it reports is the sha origin genuinely holds. Every
# invocation is appended to `calls.jsonl`, which is how a test sees the single
# label move. A branch named in the plan's `shas` overrides the mirror — that is
# how a test makes `origin/main` stale after the fetch, or makes the issue
# branch missing on origin, without touching the repos themselves.
#
# The review loop's three reads are served out of the world directory the fake
# claude writes into, so a cycle really does advance because a reviewer posted:
# the cycle headers are whatever reviewers have written, and the thread state a
# cycle sees is the plan's entry for the highest cycle those headers reach.
STUB_GH = """
import json
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
plan = json.loads((here / "plan.json").read_text())
world = Path(plan["world"])
argv = sys.argv[1:]
with (here / "calls.jsonl").open("a") as log:
    log.write(json.dumps(argv) + "\\n")


def origin_sha(branch):
    if branch in plan["shas"]:
        return plan["shas"][branch]
    done = subprocess.run(
        ["git", "-C", plan["origin"], "rev-parse", "--verify", "refs/heads/" + branch],
        capture_output=True,
        text=True,
    )
    return done.stdout.strip() if done.returncode == 0 else None


def review_lines():
    posted = [
        json.loads(path.read_text()) for path in (world / "reviews").glob("*.json")
    ]
    posted.sort(key=lambda entry: entry["seq"])
    return [entry["line"] for entry in posted]


def cycle_now():
    highest = 0
    for line in review_lines():
        fields = line.split(" \\u00b7 ")
        if len(fields) == 4 and fields[2].startswith("cycle "):
            highest = max(highest, int(fields[2][len("cycle "):]))
    return highest


def threads_now():
    defined = {int(at): threads for at, threads in plan["threads"].items()}
    reached = [at for at in sorted(defined) if at <= cycle_now()]
    return defined[reached[-1]] if reached else []


def thread_node(thread):
    line = thread.get("line", 1)
    body = thread.get("body")
    opened = [] if body is None else [{"databaseId": 1, "body": body}]
    return {
        "id": thread["id"],
        "isResolved": thread.get("isResolved", False),
        "isOutdated": thread.get("isOutdated", False),
        "path": thread.get("path", "src/dev_playbook/factory/traverse.py"),
        "line": line,
        "originalLine": thread.get("originalLine", line),
        "subjectType": "LINE",
        "comments": {"nodes": opened},
    }


if argv[:2] == ["issue", "view"]:
    print("\\n".join(plan["labels"]))
elif argv[:2] == ["issue", "edit"]:
    pass
elif argv[:1] == ["api"]:
    endpoint = [word for word in argv[1:] if not word.startswith("-")][0]
    if endpoint == "graphql":
        print(json.dumps({"data": {"repository": {"pullRequest": {"reviewThreads": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [thread_node(thread) for thread in threads_now()],
        }}}}}))
    elif endpoint.endswith("/reviews"):
        for line in review_lines():
            print(line)
    elif endpoint.endswith("/files"):
        for changed in plan["files"]:
            print("\\t".join(str(field) for field in changed))
    elif "/branches/" in endpoint:
        sha = origin_sha(endpoint.rsplit("/branches/", 1)[1])
        if sha is None:
            sys.stderr.write("gh: Not Found (HTTP 404)\\n")
            raise SystemExit(1)
        print(sha)
    else:
        sys.stderr.write("stub gh: unhandled api call %r\\n" % (argv,))
        raise SystemExit(64)
elif argv[:2] == ["pr", "list"]:
    if plan["pr_url"]:
        print("%d %s" % (plan["pr_number"], plan["pr_url"]))
else:
    sys.stderr.write("stub gh: unhandled call %r\\n" % (argv,))
    raise SystemExit(64)
"""

# A stand-in for claude that dispatches on the `--agent` it was spawned with, so
# one plan drives both nodes of a traverse. It records every launch, optionally
# does the committing and pushing a real build node's work would leave behind,
# then emits its canned stream and exits the way its step says.
FAKE_CLAUDE = """
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PEER_BUDGET = 10.0

here = Path(__file__).parent
plan = json.loads((here / "plan.json").read_text())
world = Path(plan["world"])
reviews = plan["review_names"]
argv = sys.argv[1:]
node = argv[argv.index("--agent") + 1]
session = argv[argv.index("--session-id") + 1]
prompt = argv[argv.index("-p") + 1]
step = plan[node]
with (here / "launched.jsonl").open("a") as log:
    log.write(
        json.dumps(
            {
                "node": node,
                "session": session,
                "cwd": os.getcwd(),
                "pid": os.getpid(),
                "prompt": prompt,
            }
        )
        + "\\n"
    )
# A reviewer posts its cycle header before anything else, the way a real one
# posts its review: the header is the loop's durable state, and the count is
# this review name's own headers plus one.
if node in reviews:
    posted = world / "reviews"
    posted.mkdir(parents=True, exist_ok=True)
    name = reviews[node]
    mine = sum(
        1
        for path in posted.glob("*.json")
        if json.loads(path.read_text())["review"] == name
    )
    short = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    landing = posted / (session + ".json")
    staged = posted / (session + ".staging")
    staged.write_text(
        json.dumps(
            {
                "review": name,
                "seq": time.time_ns(),
                "line": "%s \\u00b7 %s \\u00b7 cycle %d \\u00b7 %s"
                % (name, short, mine + 1, session),
            }
        )
    )
    # Renamed into place, so a sibling reading the directory never reads a file
    # that is still being written.
    staged.rename(landing)
# A rendezvous, so a test can prove the fan-out really is one: this run refuses
# to finish until the log holds as many launches as it was told to wait for, and
# a launcher that ran its nodes one after another can never reach that count.
if step["await_peers"]:
    met = False
    give_up = time.time() + PEER_BUDGET
    while time.time() < give_up:
        if len((here / "launched.jsonl").read_text().splitlines()) >= step[
            "await_peers"
        ]:
            met = True
            break
        time.sleep(0.02)
    if not met:
        sys.stderr.write("fake claude: %s never met its peers\\n" % node)
        raise SystemExit(70)
branch = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
).stdout.strip()
# Read before the detach, which would leave it reading "HEAD".
if step["detach"]:
    subprocess.run(["git", "checkout", "-q", "--detach"], check=True)
if step["commit"]:
    # Named by session, so a second launch into a worktree a first already
    # committed in still has something to commit.
    Path("built-by-%s-%s.txt" % (node, session)).write_text("the node's work\\n")
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=test",
         "commit", "-q", "-m", "the node's work"],
        check=True,
    )
    if step["push"]:
        subprocess.run(
            ["git", "push", "-q", "origin", "HEAD:refs/heads/" + branch], check=True
        )
if step["dirty"]:
    Path("left-by-%s.txt" % node).write_text("work that never reached a commit\\n")
if step["ignore_sigterm"]:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
for line in step["lines"]:
    resolved = {k: (os.getcwd() if v == "$CWD" else v) for k, v in line.items()}
    print(json.dumps(resolved), flush=True)
time.sleep(step["linger"])
sys.exit(step["exit_code"])
"""

# A traverse driven from a separate process, so a test can signal the traverse
# itself rather than the child it supervises — and so the stdout and exit code
# `main` produces are measured through the real entry point. The two module
# paths the suite redirects are set here by hand: a monkeypatched attribute lives
# in this process alone, and a child importing `launcher` fresh would otherwise
# sweep the machine's real `/etc` managed settings.
TRAVERSE_RUNNER = """
import json
import sys
from pathlib import Path

arguments = json.loads(Path(sys.argv[1]).read_text())
sys.path.insert(0, arguments["src"])

from dev_playbook.factory import launcher, traverse

launcher.MANAGED_SETTINGS = Path(arguments["managed_settings"])
launcher.MANAGED_SETTINGS_DIR = Path(arguments["managed_settings_dir"])

raise SystemExit(
    traverse.main(
        arguments["argv"],
        db_path=Path(arguments["db_path"]),
        lock_dir=Path(arguments["lock_dir"]),
        workspace_dir=Path(arguments["workspace_dir"]),
        agents_dir=Path(arguments["agents_dir"]),
        claude_cmd=tuple(arguments["claude_cmd"]),
        gh_cmd=tuple(arguments["gh_cmd"]),
        timeout_s=arguments["timeout_s"],
        grace_s=arguments["grace_s"],
    )
)
"""

# How long a test waits for a traverse process to reach the state it is about to
# act on, and for a signalled process and its child to be gone.
PROCESS_BUDGET = 20.0
PROCESS_POLL = 0.05

# The deadline a traverse runs under when the test itself is what ends the job,
# rather than the clock. Long enough that nothing times out first.
PATIENT_DEADLINE = 60.0

# Hook events precede `init` in a real stream, so every canned stream opens with
# one: the parser scans for `init` rather than reading the first line.
HOOK_LINE: dict[str, Any] = {
    "type": "system",
    "subtype": "hook_started",
    "hook_event": "SessionStart",
}

# The report a node returns in the envelope both schemas describe.
DONE_REPORT: dict[str, Any] = {"outcome": "done", "gist": "The work is done."}
ESCALATED_REPORT: dict[str, Any] = {
    "outcome": "escalated",
    "gist": "The brief contradicts the code.",
}

# What a review returns instead — the same two fields plus the counts of what it
# posted, which is the envelope the reviewer definitions end on.
REVIEWED_REPORT: dict[str, Any] = {
    "outcome": "done",
    "gist": "Two Blocking findings on PR #12.",
    "blocking_count": 2,
    "suggestion_count": 1,
}

# What the adjudicator returns — the envelope plus what it settled. `dispositions`
# is the one thing the graph reads off a report rather than off GitHub: a fix-now
# ruling is written nowhere durable, because the thread it names stays open and
# unmarked for the next cycle's reviewer.
ADJUDICATED_REPORT: dict[str, Any] = {
    "outcome": "done",
    "gist": "Three suggestions settled on PR #12.",
    "dispositions": [
        {
            "thread": "PRRT_suggestion",
            "outcome": "fix-now",
            "fix": "name the constant as the review states",
        },
        {
            "thread": "PRRT_deferred",
            "outcome": "defer",
            "reason": "needs-design",
            "stub": 512,
        },
        {"thread": "PRRT_declined", "outcome": "decline", "reason": "no-consequence"},
    ],
    "callouts": [],
}

# What it reports when its docket settles to nothing the next lap has to carry —
# the four fields all the same, because the envelope is read by its shape.
NOTHING_SETTLED: dict[str, Any] = {
    "outcome": "done",
    "gist": "Nothing left open to settle on PR #12.",
    "dispositions": [],
    "callouts": [],
}

# What a review that could not be produced at all reports — no threads posted,
# so both counts are zero, stated rather than left out.
ESCALATED_REVIEW: dict[str, Any] = {
    "outcome": "escalated",
    "gist": "The green gate is red on this branch.",
    "blocking_count": 0,
    "suggestion_count": 0,
}

# A well-formed definition for each node this graph launches.
DEFINITIONS: dict[str, dict[str, Any]] = {
    "build": {
        "name": "build",
        "description": "The build node.",
        "model": "opus",
        "effort": "xhigh",
    },
    "open-pr": {
        "name": "open-pr",
        "description": "The open-pr node.",
        "model": "sonnet",
        "effort": "low",
    },
    **{
        node: {
            "name": node,
            "description": f"The {node} node.",
            "model": "sonnet",
            "effort": "xhigh",
        }
        for node in REVIEW_NAMES
    },
    "adjudicator": {
        "name": "adjudicator",
        "description": "The adjudicator node.",
        "model": "opus",
        "effort": "xhigh",
    },
}

# The changed file a traverse's pull request carries unless a test says
# otherwise: one code file, which elects the code track and nothing else.
CODE_FILE = ["src/dev_playbook/factory/traverse.py", "modified", 12, 3]
DOC_FILE = ["software-factory/factory-operations.md", "modified", 40, 20]


# A Blocking and a Suggestion thread, as the GraphQL read hands them over.
def blocking_thread(
    thread_id: str = "PRRT_blocking", *, resolved: bool = False
) -> dict[str, Any]:
    """One open Blocking thread, which is what drives a rework lap."""
    return {
        "id": thread_id,
        "isResolved": resolved,
        "path": "src/dev_playbook/factory/traverse.py",
        "line": 41,
        "body": "Blocking — the verdict is never written.\n\n— code review · sess-x",
    }


def suggestion_thread(thread_id: str = "PRRT_suggestion") -> dict[str, Any]:
    """One open Suggestion thread, which a converged pull request may keep."""
    return {
        "id": thread_id,
        "isResolved": False,
        "path": "src/dev_playbook/factory/traverse.py",
        "line": 9,
        "body": "Suggestion — name this constant.\n\n— code review · sess-x",
    }


def commentless_thread(thread_id: str = "PRRT_silent") -> dict[str, Any]:
    """A thread the read hands back with no comment on it — a shape nobody grades."""
    return {
        "id": thread_id,
        "isResolved": False,
        "path": "src/dev_playbook/factory/traverse.py",
        "line": 41,
    }


# The shrunk clocks every supervision runs under, so a `timed-out` classification
# is reached in test time rather than in the job's real hour.
BRIEF_DEADLINE = 0.4
BRIEF_GRACE = 0.4

# Long enough that a child the traverse fails to kill fails the test by holding
# it rather than by passing for the wrong reason.
LINGER_SECONDS = 30.0


def init_line(cwd: str = "$CWD", api_key_source: str = "none") -> dict[str, Any]:
    """An `init` message declaring where the run was placed and what pays for it."""
    return {
        "type": "system",
        "subtype": "init",
        "cwd": cwd,
        "apiKeySource": api_key_source,
        "model": "claude-opus-4-5",
        "permissionMode": "bypassPermissions",
    }


def result_line(report: dict[str, Any] | None = None) -> dict[str, Any]:
    """A terminating `result` envelope carrying the accounting a job-report records."""
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "duration_ms": 5432,
        "num_turns": 3,
        "usage": {"input_tokens": 100, "output_tokens": 20},
        "permission_denials": [],
        "structured_output": report,
    }


def node_step(
    lines: list[dict[str, Any]] | None = None,
    *,
    commit: bool = False,
    push: bool = False,
    detach: bool = False,
    dirty: bool = False,
    linger: float = 0.0,
    exit_code: int = 0,
    ignore_sigterm: bool = False,
    await_peers: int = 0,
) -> dict[str, Any]:
    """One node's plan for the fake claude — what it does, says, and exits with."""
    if lines is None:
        lines = [HOOK_LINE, init_line(), result_line(DONE_REPORT)]
    return {
        "lines": lines,
        "commit": commit,
        "push": push,
        "detach": detach,
        "dirty": dirty,
        "linger": linger,
        "exit_code": exit_code,
        "ignore_sigterm": ignore_sigterm,
        "await_peers": await_peers,
    }


def clean_build() -> dict[str, Any]:
    """A build that commits its work, pushes the branch, and reports done."""
    return node_step(commit=True, push=True)


def clean_review() -> dict[str, Any]:
    """A review that posts its cycle header and reports on the full envelope."""
    return node_step([HOOK_LINE, init_line(), result_line(REVIEWED_REPORT)])


def clean_adjudication() -> dict[str, Any]:
    """An adjudicator that settles its docket and reports what it settled."""
    return node_step([HOOK_LINE, init_line(), result_line(ADJUDICATED_REPORT)])


# The plan every fake claude starts from: every node clean, the build committing
# and pushing the branch its verification then reads back off origin.
DEFAULT_STEPS: dict[str, dict[str, Any]] = {
    "build": clean_build(),
    "open-pr": node_step(),
    "adjudicator": clean_adjudication(),
    **{node: clean_review() for node in REVIEW_NAMES},
}


def wait_until(ready: Callable[[], bool], budget: float = PROCESS_BUDGET) -> bool:
    """Poll `ready` until it holds, within `budget` seconds."""
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        if ready():
            return True
        time.sleep(PROCESS_POLL)
    return False


def add_worktree(checkout: Path, branch: str) -> Path:
    """Create the issue's worktree by hand, the way a previous traverse left it."""
    path = checkout / ".claude" / "worktrees" / branch
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "-C", str(checkout), "worktree", "add", "-q", str(path), "-b", branch],
        check=True,
        capture_output=True,
    )
    return path


def push_branch(checkout: Path, branch: str) -> None:
    """Put a branch on origin, the way the lap before this one left it there."""
    subprocess.run(
        ["git", "-C", str(checkout), "push", "-q", "origin", branch],
        check=True,
        capture_output=True,
    )


def blank_column(db: Path, column: str) -> None:
    """Null one grain column of the store's only `job-launch` row.

    Written with raw SQL because no writer in `ledger` will produce it: the
    row this makes is a store that has gone wrong, which is the whole case
    under test.
    """
    with closing(sqlite3.connect(db)) as connection:
        connection.execute(f"UPDATE ledger SET {column} = NULL")
        connection.commit()


def kinds(db: Path) -> list[str]:
    """The kinds the ledger holds, in write order."""
    return [row.kind for row in ledger_rows(db)]


def payload_of(db: Path, kind: str) -> dict[str, Any]:
    """The payload of the one row of `kind` the ledger holds."""
    (found,) = [row for row in ledger_rows(db) if row.kind == kind]
    return found.payload


def payloads_of(db: Path, kind: str) -> list[dict[str, Any]]:
    """Every payload of `kind` the ledger holds, in write order."""
    return [row.payload for row in ledger_rows(db) if row.kind == kind]


def seed_review(world: Path, name: str, *, cycle: int, sha: str) -> None:
    """Leave one review's cycle header behind, the way a finished cycle does.

    This is the whole of what a crashed traverse leaves for the next one to pick
    up: the loop keeps no state of its own, so a header on the pull request is
    the state.
    """
    posted = world / "reviews"
    posted.mkdir(parents=True, exist_ok=True)
    (posted / f"{name.replace(' ', '-')}-{cycle}.json").write_text(
        json.dumps(
            {
                "review": name,
                "seq": cycle,
                "line": f"{name} · {sha} · cycle {cycle} · sess-{name[0]}{cycle}",
            }
        )
    )


@pytest.fixture
def home(tmp_path: Path) -> Path:
    """A throwaway home directory, so no sweep reads the real ``~/.claude``."""
    path = tmp_path / "home"
    (path / ".claude").mkdir(parents=True)
    return path


@pytest.fixture(autouse=True)
def child_env(home: Path, monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Make this process's environment clean, since every child inherits it.

    Autouse: the traverse preflights and spawns under `os.environ`, so a machine
    that happens to export a billing variable — or an effort level — must not
    decide what these tests measure.
    """
    monkeypatch.setenv("HOME", str(home))
    for var in (*launcher.BILLING_ENV_VARS, launcher.EFFORT_LEVEL_VAR):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.fixture(autouse=True)
def managed_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Point the managed-settings roster at an empty temp tree, never ``/etc``."""
    settings = tmp_path / "etc" / "managed-settings.json"
    drop_in = tmp_path / "etc" / "managed-settings.d"
    monkeypatch.setattr(launcher, "MANAGED_SETTINGS", settings)
    monkeypatch.setattr(launcher, "MANAGED_SETTINGS_DIR", drop_in)
    return settings, drop_in


@pytest.fixture
def origin(tmp_path: Path) -> Path:
    """A bare repo standing in for origin, so a push and a fetch are both real."""
    path = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "-q", "--bare", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )
    return path


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """The workspace directory the slug's checkout is derived inside."""
    path = tmp_path / "workspace"
    path.mkdir()
    return path


@pytest.fixture
def checkout(workspace: Path, origin: Path) -> Path:
    """The issue's main checkout, on `main`, with its one commit on origin."""
    root = workspace / NAME
    init_repo(root)
    (root / "README.md").write_text("fixture\n")
    commit_all(root)
    subprocess.run(
        ["git", "-C", str(root), "remote", "add", "origin", str(origin)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "push", "-q", "origin", "main"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "fetch", "-q", "origin", "main"],
        check=True,
        capture_output=True,
    )
    return root


@pytest.fixture
def locks(tmp_path: Path) -> Path:
    """A throwaway lock directory, so no test takes the real factory's locks."""
    return tmp_path / "locks"


@pytest.fixture
def db(tmp_path: Path) -> Path:
    """A throwaway ledger, so no test writes to the real events.db."""
    return tmp_path / "ledger" / "events.db"


@pytest.fixture
def agents_dir(tmp_path: Path) -> Path:
    """A throwaway user agents directory holding both nodes this graph launches."""
    path = tmp_path / "agents"
    path.mkdir()
    for node, frontmatter in DEFINITIONS.items():
        write_definition(path, node, frontmatter)
    return path


@pytest.fixture
def world(tmp_path: Path) -> Path:
    """Where the reviewers post their cycle headers and the stub gh reads them.

    One directory shared by the two stand-ins, which is what makes a cycle
    advance for the reason it advances in production: a review ran and left a
    header behind.
    """
    path = tmp_path / "world"
    path.mkdir()
    return path


@pytest.fixture
def stub_gh(
    tmp_path: Path, origin: Path, world: Path
) -> Callable[..., tuple[str, ...]]:
    """Write the stub gh for one test and return the command that runs it."""
    here = tmp_path / "gh"
    here.mkdir()
    script = here / "gh.py"
    script.write_text(STUB_GH)

    def plan(
        labels: list[str] | None = None,
        *,
        shas: dict[str, str | None] | None = None,
        pr_url: str | None = PR_URL,
        pr_number: int = PR_NUMBER,
        files: list[list[Any]] | None = None,
        threads: dict[int, list[dict[str, Any]]] | None = None,
    ) -> tuple[str, ...]:
        (here / "plan.json").write_text(
            json.dumps(
                {
                    "origin": str(origin),
                    "world": str(world),
                    "labels": BUILD_LABELS if labels is None else labels,
                    "shas": shas or {},
                    "pr_url": pr_url,
                    "pr_number": pr_number,
                    "files": [CODE_FILE] if files is None else files,
                    "threads": threads or {},
                }
            )
        )
        return (sys.executable, str(script))

    return plan


@pytest.fixture
def gh_calls(tmp_path: Path) -> Callable[[], list[list[str]]]:
    """Read back every call the stub gh was made with, in order."""

    def read() -> list[list[str]]:
        log = tmp_path / "gh" / "calls.jsonl"
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text().splitlines()]

    return read


@pytest.fixture
def fake_claude(tmp_path: Path, world: Path) -> Callable[..., tuple[str, ...]]:
    """Write the stand-in claude for one test and return the command that runs it."""
    here = tmp_path / "fake"
    here.mkdir()
    script = here / "claude.py"
    script.write_text(FAKE_CLAUDE)

    def plan(**steps: dict[str, Any]) -> tuple[str, ...]:
        (here / "plan.json").write_text(
            json.dumps(
                {
                    **DEFAULT_STEPS,
                    **steps,
                    "world": str(world),
                    "review_names": REVIEW_NAMES,
                }
            )
        )
        return (sys.executable, str(script))

    return plan


@pytest.fixture
def launched(tmp_path: Path) -> Callable[[], list[dict[str, Any]]]:
    """Read back every node launch the fake claude recorded, in order."""

    def read() -> list[dict[str, Any]]:
        log = tmp_path / "fake" / "launched.jsonl"
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text().splitlines()]

    return read


@pytest.fixture
def traverse_issue(
    checkout: Path,
    workspace: Path,
    locks: Path,
    db: Path,
    agents_dir: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    fake_claude: Callable[..., tuple[str, ...]],
) -> Callable[..., traverse.TraverseOutcome]:
    """Run a traverse through every seam, naming only what a test varies.

    `checkout` is requested rather than used so the issue's checkout exists for
    every test that does not deliberately remove it.
    """

    def run(**seams: Any) -> traverse.TraverseOutcome:
        # `or` rather than a `pop` default: both fallbacks write the plan file
        # their command reads, and a `pop` default is built whether or not it is
        # used — so the default plan would overwrite the one a test just wrote.
        return traverse.traverse_issue(
            seams.pop("repo", REPO),
            seams.pop("issue", ISSUE),
            seams.pop("mode", "auto"),
            db_path=db,
            lock_dir=locks,
            workspace_dir=workspace,
            agents_dir=agents_dir,
            claude_cmd=seams.pop("claude_cmd", None) or fake_claude(),
            gh_cmd=seams.pop("gh_cmd", None) or stub_gh(),
            timeout_s=seams.pop("timeout_s", BRIEF_DEADLINE),
            grace_s=seams.pop("grace_s", BRIEF_GRACE),
            **seams,
        )

    return run


@pytest.fixture
def traverse_process(
    tmp_path: Path,
    checkout: Path,
    workspace: Path,
    locks: Path,
    db: Path,
    agents_dir: Path,
    managed_settings: tuple[Path, Path],
    stub_gh: Callable[..., tuple[str, ...]],
    fake_claude: Callable[..., tuple[str, ...]],
) -> Callable[..., subprocess.Popen[str]]:
    """Spawn a traverse in its own process, through the real `main`."""
    runner = tmp_path / "runner.py"
    runner.write_text(TRAVERSE_RUNNER)
    managed, drop_in = managed_settings
    spawned = 0

    def start(**seams: Any) -> subprocess.Popen[str]:
        nonlocal spawned
        spawned += 1
        arguments = tmp_path / f"traverse-{spawned}.json"
        arguments.write_text(
            json.dumps(
                {
                    "src": str(Path(traverse.__file__).parents[2]),
                    "managed_settings": str(managed),
                    "managed_settings_dir": str(drop_in),
                    "argv": [
                        seams.pop("repo", REPO),
                        str(seams.pop("issue", ISSUE)),
                        seams.pop("mode", "auto"),
                    ],
                    "db_path": str(db),
                    "lock_dir": str(locks),
                    "workspace_dir": str(workspace),
                    "agents_dir": str(agents_dir),
                    "claude_cmd": list(seams.pop("claude_cmd", None) or fake_claude()),
                    "gh_cmd": list(seams.pop("gh_cmd", None) or stub_gh()),
                    "timeout_s": seams.pop("timeout_s", BRIEF_DEADLINE),
                    "grace_s": seams.pop("grace_s", BRIEF_GRACE),
                }
            )
        )
        return subprocess.Popen(
            [sys.executable, str(runner), str(arguments)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    return start


# --- the entry gate, before any ledger write ---


@pytest.mark.parametrize("mode", ["", "spike", "AUTO", "user_rework", "rework"])
def test_a_mode_outside_the_vocabulary_is_refused_with_nothing_written(
    mode: str, db: Path, locks: Path, traverse_issue: Callable[..., Any]
) -> None:
    with pytest.raises(traverse.TraverseError):
        traverse_issue(mode=mode)

    assert ledger_rows(db) == []
    assert not locks.exists()


def test_a_slug_with_no_checkout_in_the_workspace_is_refused_with_nothing_written(
    db: Path, locks: Path, traverse_issue: Callable[..., Any]
) -> None:
    with pytest.raises(traverse.TraverseError):
        traverse_issue(repo="owner/never-cloned")

    assert ledger_rows(db) == []
    assert not locks.exists()


def test_the_checkout_is_derived_from_the_second_half_of_the_slug(
    checkout: Path, workspace: Path
) -> None:
    """A slug whose owner is not the directory name still resolves.

    `~/workspace` is flat and holds no owner directories, so the owner half of
    the slug addresses GitHub and nothing on disk.
    """
    assert traverse.checkout_of("someone-else/repo", workspace) == checkout


# --- the per-issue lock ---


def test_a_traverse_of_an_issue_already_locked_is_refused_with_nothing_written(
    db: Path, locks: Path, traverse_issue: Callable[..., Any]
) -> None:
    """A held lock means a live traverse, and a second `traverse-start` would
    close that traverse's window out from under it — so nothing is written.

    The lock is taken here on a descriptor of this process's own, which conflicts
    exactly as another process's would: an `flock` belongs to the open file
    description, not to the process that opened it.
    """
    held = traverse.lock_path(REPO, ISSUE, locks)
    held.parent.mkdir(parents=True, exist_ok=True)
    with open(held, "w") as descriptor:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)

        with pytest.raises(traverse.TraverseError):
            traverse_issue()

    assert ledger_rows(db) == []


def test_a_lock_left_behind_by_a_finished_traverse_holds_nothing(
    db: Path, locks: Path, traverse_issue: Callable[..., Any]
) -> None:
    """The lock rides the descriptor, so the file it lives in is never stale."""
    abandoned = traverse.lock_path(REPO, ISSUE, locks)
    abandoned.parent.mkdir(parents=True, exist_ok=True)
    abandoned.write_text("")

    traverse_issue()

    assert kinds(db)[0] == "traverse-start"


def test_two_issues_of_one_repo_take_different_locks(locks: Path) -> None:
    assert traverse.lock_path(REPO, 1, locks) != traverse.lock_path(REPO, 2, locks)


def test_two_repos_whose_slugs_differ_only_by_the_slash_take_different_locks(
    locks: Path,
) -> None:
    """The separator is encoded, so no two slugs can collide onto one lock."""
    assert traverse.lock_path("a/b-c", 1, locks) != traverse.lock_path(
        "a-b/c", 1, locks
    )


# --- orienting from the labels ---


UNORIENTABLE_LABELS = [
    ["mode:direct", "phase:intake"],
    ["mode:direct", "phase:design"],
    ["mode:direct", "phase:merged"],
    ["mode:direct", "tests:yes"],
    [],
    ["mode:spike", "phase:build"],
]


@pytest.mark.parametrize("labels", UNORIENTABLE_LABELS)
def test_a_phase_this_graph_does_not_run_ends_escalated_with_full_books(
    labels: list[str],
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(gh_cmd=stub_gh(labels))

    assert outcome.status == "escalated"
    assert kinds(db) == ["traverse-start", "traverse-escalation", "traverse-end"]
    assert payload_of(db, "traverse-end") == {"status": "escalated"}
    assert launched() == []


def test_an_escalation_before_any_launch_names_neither_a_node_nor_a_session(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(gh_cmd=stub_gh(["phase:merged"]))

    escalation = payload_of(db, "traverse-escalation")
    assert escalation["node"] is None
    assert escalation["session_id"] is None
    assert "phase:merged" in escalation["reason"]
    assert outcome.session_id is None


def test_the_traverse_start_records_the_mode_it_was_launched_in(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    traverse_issue(mode="user-rework", gh_cmd=stub_gh(["phase:merged"]))

    assert payload_of(db, "traverse-start") == {"mode": "user-rework"}


# --- the graph ---


def test_a_build_phase_issue_runs_its_nodes_then_the_loop_and_ends_pr_ready(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Build, open-pr, one converging review cycle, then the adjudicator.

    The whole path. The convergence run is not conditional — the pull request's
    disposition sections are brought up to date on it whether or not this cycle
    left anything open — so the last two rows are its launch and its report.
    """
    outcome = traverse_issue()

    assert [launch["node"] for launch in launched()][:2] == ["build", "open-pr"]
    written = kinds(db)
    assert written[:6] == [
        "traverse-start",
        "job-launch",
        "job-report",
        "phase-transition",
        "job-launch",
        "job-report",
    ]
    # The fan-out's four rows are unordered among themselves by construction —
    # two jobs racing each other is the whole point — so the cycle is judged on
    # which rows it wrote rather than on which of them won.
    assert sorted(written[6:10]) == [
        "job-launch",
        "job-launch",
        "job-report",
        "job-report",
    ]
    assert written[10:] == ["verdict", "job-launch", "job-report", "traverse-end"]
    assert payload_of(db, "phase-transition") == {"from": "build", "to": "pr-review"}
    assert payload_of(db, "traverse-end") == {"status": "pr-ready", "pr_url": PR_URL}
    assert outcome == traverse.TraverseOutcome("pr-ready", pr_url=PR_URL)


def test_a_pr_review_phase_issue_skips_the_build_and_falls_into_the_loop(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Re-entry runs open-pr, which is idempotent, and then reviews as usual."""
    outcome = traverse_issue(gh_cmd=stub_gh(PR_REVIEW_LABELS))

    assert nodes_launched(launched) == [
        "adjudicator",
        "bug-pr-review",
        "code-pr-review",
        "open-pr",
    ]
    assert "phase-transition" not in kinds(db)
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]
    assert outcome.status == "pr-ready"


def test_a_phase_launches_exactly_the_nodes_its_graph_entry_names(
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The tuples in `GRAPH` are the graph, not a note about it.

    Left unwalked, an entry that names one node runs two, and the next author
    to add a phase — one that only re-verifies, say — spends a job on a node
    they declared out of it and reads the module's own word for the structure
    as false. What the entry governs is the run up to the review loop; the loop
    itself follows every entry.
    """
    monkeypatch.setattr(traverse, "GRAPH", {traverse.BUILD: (traverse.BUILD,)})

    outcome = traverse_issue()

    assert [run["node"] for run in launched()][0] == traverse.BUILD
    assert traverse.OPEN_PR not in nodes_launched(launched)
    assert outcome.status == "pr-ready"


def test_every_node_is_launched_in_the_issues_worktree_with_the_issue_as_its_prompt(
    checkout: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    traverse_issue()

    worktree = checkout / ".claude" / "worktrees" / BRANCH
    assert {Path(launch["cwd"]).resolve() for launch in launched()} == {
        worktree.resolve()
    }


def test_the_label_move_is_the_one_write_the_traverse_makes_to_the_issue(
    gh_calls: Callable[[], list[list[str]]], traverse_issue: Callable[..., Any]
) -> None:
    traverse_issue()

    edits = [call for call in gh_calls() if call[:2] == ["issue", "edit"]]
    assert edits == [
        [
            "issue",
            "edit",
            str(ISSUE),
            "--repo",
            REPO,
            "--add-label",
            "phase:pr-review",
            "--remove-label",
            "phase:build",
        ]
    ]


# --- every way a job fails ends the traverse, with no retry ---


# Every way one job can come back other than clean-and-done, with the two-layer
# outcome each must be classified as. The expected pair is carried so the five
# cases are held apart: without it a bug collapsing them all onto one
# classification would still satisfy every assertion below.
FAILING_BUILDS: list[tuple[str, dict[str, Any], tuple[str, str | None]]] = [
    (
        "schema-refused",
        node_step([HOOK_LINE, init_line(), result_line(None)], commit=True, push=True),
        ("schema-refused", None),
    ),
    (
        "died",
        node_step([HOOK_LINE, init_line()], exit_code=1),
        ("died", None),
    ),
    (
        "timed-out",
        node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS),
        ("timed-out", None),
    ),
    (
        "misconfigured",
        node_step([HOOK_LINE, init_line(cwd="/somewhere/else"), result_line()]),
        ("misconfigured", None),
    ),
    (
        "task-escalated",
        node_step(
            [HOOK_LINE, init_line(), result_line(ESCALATED_REPORT)],
            commit=True,
            push=True,
        ),
        ("clean", "escalated"),
    ),
]


@pytest.mark.parametrize(
    ("step", "classification"),
    [(step, classification) for _, step, classification in FAILING_BUILDS],
    ids=[name for name, _, _ in FAILING_BUILDS],
)
def test_a_build_that_does_not_come_back_clean_and_done_ends_the_traverse(
    step: dict[str, Any],
    classification: tuple[str, str | None],
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(claude_cmd=fake_claude(build=step))

    assert outcome.status == "escalated"
    assert [launch["node"] for launch in launched()] == ["build"]
    assert kinds(db) == [
        "traverse-start",
        "job-launch",
        "job-report",
        "traverse-escalation",
        "traverse-end",
    ]
    report = payload_of(db, "job-report")
    assert (report["process_outcome"], report["task_outcome"]) == classification
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]


def test_an_escalation_after_a_launch_names_the_node_and_the_session_that_ran_it(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    step = node_step([HOOK_LINE, init_line()], exit_code=1)

    outcome = traverse_issue(claude_cmd=fake_claude(build=step))

    escalation = payload_of(db, "traverse-escalation")
    assert escalation["node"] == "build"
    assert escalation["session_id"] == launched()[0]["session"]
    assert outcome.session_id == launched()[0]["session"]


def test_a_failure_the_graph_never_foresaw_closes_the_books_and_still_raises(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """A window left open would read as a live traverse for good.

    The harness breaking its own contract is not one of the ways a job comes
    back, so nothing in the graph converts it into an escalation. It still has
    to close the window on its way out — and it still has to reach the operator
    as the traceback it is, because nothing about it is understood well enough
    to be handled.
    """
    lawless = node_step([HOOK_LINE, result_line(DONE_REPORT)])

    with pytest.raises(launcher.HarnessContractViolation):
        traverse_issue(claude_cmd=fake_claude(build=lawless))

    assert kinds(db) == [
        "traverse-start",
        "job-launch",
        "traverse-escalation",
        "traverse-end",
    ]
    assert payload_of(db, "traverse-end") == {"status": "escalated"}
    assert ledger.live_jobs(db_path=db) == []


# --- what the traverse verifies for itself ---


def test_a_build_reporting_done_over_a_branch_missing_on_origin_escalates(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The node committed nothing, so origin holds no branch to review."""
    outcome = traverse_issue(claude_cmd=fake_claude(build=node_step()))

    assert outcome.status == "escalated"
    assert "not on origin" in payload_of(db, "traverse-escalation")["reason"]
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]


def test_a_build_reporting_done_over_a_branch_stale_on_origin_escalates(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Origin holds the branch at a commit the worktree does not, so the push
    never carried everything the review is about to be shown."""
    behind = "0" * 40

    outcome = traverse_issue(gh_cmd=stub_gh(shas={BRANCH: behind}))

    assert outcome.status == "escalated"
    assert behind in payload_of(db, "traverse-escalation")["reason"]
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]


def test_a_build_reporting_done_over_an_uncommitted_worktree_escalates(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The node pushed what it committed and then went on editing, so the two
    shas agree while the last of the work sits in a tree no review can read."""
    step = node_step(commit=True, push=True, dirty=True)

    outcome = traverse_issue(claude_cmd=fake_claude(build=step))

    assert outcome.status == "escalated"
    assert "uncommitted" in payload_of(db, "traverse-escalation")["reason"]
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]


def test_a_build_reporting_done_from_a_detached_head_escalates(
    checkout: Path,
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The commit went somewhere the branch does not point, so `issue-<N>` still
    holds exactly what origin holds and the sha comparison agrees with itself."""
    add_worktree(checkout, BRANCH)
    push_branch(checkout, BRANCH)

    outcome = traverse_issue(
        claude_cmd=fake_claude(build=node_step(commit=True, detach=True))
    )

    assert outcome.status == "escalated"
    assert "detached" in payload_of(db, "traverse-escalation")["reason"]
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]


def test_open_pr_reporting_done_with_no_pull_request_open_escalates(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The URL is read off GitHub, never lifted from what the node claimed."""
    outcome = traverse_issue(gh_cmd=stub_gh(pr_url=None))

    assert outcome.status == "escalated"
    assert payload_of(db, "traverse-escalation")["node"] == "open-pr"
    assert kinds(db)[-1] == "traverse-end"
    assert payload_of(db, "traverse-end") == {"status": "escalated"}


# --- the worktree ---


def test_the_worktree_is_created_on_its_own_branch_off_origin_main(
    checkout: Path, traverse_issue: Callable[..., Any]
) -> None:
    traverse_issue()

    worktree = checkout / ".claude" / "worktrees" / BRANCH
    head = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert head.stdout.strip() == BRANCH


def test_a_base_still_stale_after_the_fetch_escalates_before_any_worktree_exists(
    checkout: Path,
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(gh_cmd=stub_gh(shas={"main": "0" * 40}))

    assert outcome.status == "escalated"
    assert not (checkout / ".claude" / "worktrees" / BRANCH).exists()
    assert launched() == []
    assert "after a fetch" in payload_of(db, "traverse-escalation")["reason"]


def test_a_branch_already_on_origin_with_no_worktree_left_is_never_recut(
    checkout: Path,
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The branch missing locally is not the same as the work being missing.

    `git worktree add -b issue-<N> origin/main` fails loudly on a local branch
    that exists and succeeds silently on one that does not, so a checkout that
    was re-cloned — or whose branch the user deleted before the merge landed —
    would have every commit the last lap pushed reset to `main` underneath it,
    with no build node running to put them back.
    """
    outcome = traverse_issue(gh_cmd=stub_gh(shas={BRANCH: "0" * 40}))

    assert outcome.status == "escalated"
    assert not (checkout / ".claude" / "worktrees" / BRANCH).exists()
    assert launched() == []
    assert "on origin" in payload_of(db, "traverse-escalation")["reason"]


def test_an_existing_worktree_is_reused_exactly_as_it_was_found(
    checkout: Path, traverse_issue: Callable[..., Any]
) -> None:
    """No freshness check and no rebase: work in flight is left where it is."""
    worktree = add_worktree(checkout, BRANCH)
    carried_over = worktree / "work-in-flight.txt"
    carried_over.write_text("from the last lap\n")

    traverse_issue()

    assert carried_over.read_text() == "from the last lap\n"


def test_a_directory_git_has_no_worktree_registered_at_is_never_reused(
    checkout: Path,
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """A directory at the path is not proof of a worktree.

    `git worktree remove` refused over untracked files leaves the tree standing,
    and a re-cloned checkout leaves one whose link points nowhere. Reused, both
    break the first git command a node runs — deep inside a launch already paid
    for.
    """
    stray = checkout / ".claude" / "worktrees" / BRANCH
    stray.mkdir(parents=True)

    outcome = traverse_issue()

    assert outcome.status == "escalated"
    assert launched() == []
    assert "no worktree" in payload_of(db, "traverse-escalation")["reason"]


def test_a_worktree_found_on_another_branch_escalates_rather_than_being_worked_in(
    checkout: Path,
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    path = checkout / ".claude" / "worktrees" / BRANCH
    path.parent.mkdir(parents=True)
    subprocess.run(
        ["git", "-C", str(checkout), "worktree", "add", "-q", str(path), "-b", "other"],
        check=True,
        capture_output=True,
    )

    outcome = traverse_issue()

    assert outcome.status == "escalated"
    assert launched() == []
    assert "other" in payload_of(db, "traverse-escalation")["reason"]


# --- the command line ---


def test_a_finished_traverse_prints_one_json_line_and_exits_zero(
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    running = traverse_process()

    stdout, stderr = running.communicate(timeout=PROCESS_BUDGET)

    assert running.returncode == 0
    assert json.loads(stdout) == {"status": "pr-ready", "pr_url": PR_URL}
    assert stdout.count("\n") == 1
    assert stderr != ""


def test_an_escalated_traverse_prints_its_status_and_session_and_exits_zero(
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    """An escalation is a result the graph reached, not a failure of the script."""
    running = traverse_process(gh_cmd=stub_gh(["phase:merged"]))

    stdout, _ = running.communicate(timeout=PROCESS_BUDGET)

    assert running.returncode == 0
    assert json.loads(stdout) == {"status": "escalated", "session_id": None}


@pytest.mark.parametrize(
    "argv",
    [[], [REPO], [REPO, str(ISSUE)], [REPO, str(ISSUE), "auto", "extra"]],
)
def test_the_command_line_takes_exactly_three_arguments(argv: list[str]) -> None:
    with pytest.raises(traverse.TraverseError):
        traverse.main(argv)


@pytest.mark.parametrize(
    "argv",
    [
        ["owner/repo", "1", "spike"],
        ["owner/repo", "1"],
        ["owner/no-such-checkout-anywhere", "1", "auto"],
    ],
)
def test_the_shim_refuses_a_call_it_cannot_run_and_exits_nonzero(
    argv: list[str],
) -> None:
    """Run through the installed shim, on its own defaults.

    Nothing here reaches the real ledger or the real lock directory, because
    every one of these is refused before either is touched — which is the
    property being measured as much as the exit code is.
    """
    shim = Path(traverse.__file__).parents[3] / "scripts" / "traverse-issue"

    refused = subprocess.run(
        [sys.executable, str(shim), *argv], capture_output=True, text=True
    )

    assert refused.returncode != 0
    assert "TraverseError" in refused.stderr
    assert refused.stdout == ""


# --- one traverse per issue at a time ---


def test_a_second_traverse_of_a_live_issue_fails_at_once_and_writes_nothing(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    held = fake_claude(build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS))
    first = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)
    rows_while_running = len(ledger_rows(db))

    second = traverse_process(claude_cmd=held)
    _, stderr = second.communicate(timeout=PROCESS_BUDGET)
    first.kill()
    first.communicate(timeout=PROCESS_BUDGET)

    assert second.returncode != 0
    assert "is still running" in stderr
    assert len(ledger_rows(db)) == rows_while_running
    assert kinds(db).count("traverse-start") == 1


def test_a_traverse_of_another_issue_runs_while_one_issue_is_locked(
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    held = fake_claude(
        build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS),
        **{"open-pr": node_step()},
    )
    first = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)

    other = traverse_process(issue=441, claude_cmd=fake_claude())
    stdout, _ = other.communicate(timeout=PROCESS_BUDGET)
    first.kill()
    first.communicate(timeout=PROCESS_BUDGET)

    assert other.returncode == 0
    assert json.loads(stdout)["status"] == "pr-ready"


# --- the kill cascade and the orphan sweep ---


def test_a_traverse_sent_sigterm_kills_its_child_and_closes_its_own_window(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    held = fake_claude(build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS))
    running = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)
    child = launched()[0]

    running.send_signal(signal.SIGTERM)
    stdout, _ = running.communicate(timeout=PROCESS_BUDGET)

    assert running.returncode != 0
    assert stdout == ""
    assert wait_until(lambda: process_state(child["pid"]) in (None, "Z"))
    report = payload_of(db, "job-report")
    assert report["process_outcome"] == "died"
    assert report["swept"] == "kill-cascade"
    assert payload_of(db, "traverse-end") == {"status": "killed"}
    assert ledger.live_jobs(db_path=db) == []
    assert ledger.awaiting_merge(db_path=db) == []


def test_a_kill_cascade_that_cannot_file_a_job_still_closes_the_window_as_killed(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    """The `killed` end is written ahead of the filing that can fail.

    Filing the standing jobs has ways to raise that the trap cannot rule out —
    a probe that will not compile, a store that refuses the write. A trap that
    filed first and closed after would lose the `killed` end to any of them,
    with both signals already back at the default and no second chance at the
    books. So the end goes first and the filing follows it.

    The `[` row is planted after the traverse's own orphan sweep has already
    run, which is what leaves the kill cascade to be the thing that meets it.
    """
    held = fake_claude(build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS))
    running = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)
    ledger.job_launch(REPO, ISSUE, "build", "[", {}, db_path=db)

    running.send_signal(signal.SIGTERM)
    running.communicate(timeout=PROCESS_BUDGET)

    assert running.returncode != 0
    assert payload_of(db, "traverse-end") == {"status": "killed"}
    assert "traverse-escalation" not in kinds(db)


def test_a_traverse_destroyed_without_warning_takes_its_child_with_it(
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
) -> None:
    """`PR_SET_PDEATHSIG` is what covers the signal no trap can catch."""
    held = fake_claude(build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS))
    running = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)
    child = launched()[0]

    running.kill()
    running.communicate(timeout=PROCESS_BUDGET)

    assert wait_until(lambda: process_state(child["pid"]) in (None, "Z"))


def test_the_next_traverse_finishes_the_books_a_destroyed_one_left_open(
    db: Path,
    fake_claude: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    traverse_process: Callable[..., subprocess.Popen[str]],
    traverse_issue: Callable[..., Any],
) -> None:
    ledger.job_launch("owner/other", 999, "build", "sess-elsewhere", {}, db_path=db)
    held = fake_claude(build=node_step([HOOK_LINE, init_line()], linger=LINGER_SECONDS))
    destroyed = traverse_process(claude_cmd=held, timeout_s=PATIENT_DEADLINE)
    assert wait_until(lambda: len(launched()) == 1)
    orphaned = launched()[0]["session"]
    destroyed.kill()
    destroyed.communicate(timeout=PROCESS_BUDGET)

    traverse_issue()

    swept = [
        row.payload
        for row in ledger_rows(db)
        if row.kind == "job-report" and row.payload.get("swept") == "orphan-recovery"
    ]
    assert len(swept) == 1
    assert swept[0]["process_outcome"] == "died"
    assert orphaned not in [row.session_id for row in ledger.live_jobs(db_path=db)]
    assert [row.session_id for row in ledger.live_jobs(db_path=db)] == [
        "sess-elsewhere"
    ]


def test_a_process_probe_that_fails_for_any_reason_but_no_match_stops_the_sweep(
    db: Path, traverse_issue: Callable[..., Any]
) -> None:
    """Read as "already gone", a broken probe would file a live job as dead.

    `pgrep` exits 1 when it matched nothing and 2 when it could not go looking
    at all. Taking the second for the first files the job's terminal row while
    its claude session runs on, billed to the subscription with nobody watching
    it — so it stops the traverse instead.

    A lone `[` is what makes the probe fail here: `pgrep` compiles its pattern
    as a regular expression, and an unclosed bracket expression is not one.
    """
    ledger.job_launch(REPO, ISSUE, "build", "[", {}, db_path=db)

    with pytest.raises(traverse.TraverseError):
        traverse_issue()

    assert kinds(db) == ["job-launch"]


@pytest.mark.parametrize("missing", ["node", "session_id"])
def test_a_launch_row_missing_a_column_the_sweep_needs_stops_the_traverse(
    missing: str, db: Path, traverse_issue: Callable[..., Any]
) -> None:
    """Coerced to a string, a missing session id is a pattern the probe hunts for.

    `str(None)` is the literal `"None"`, and `pgrep -f None` then answers about
    whatever else on the machine carries that word — a probe that looked for
    the wrong thing, filing a live job as dead. The launcher writes no such
    row, so this is a store that has gone wrong, and a store that has gone
    wrong is said out loud rather than worked around.
    """
    ledger.job_launch(REPO, ISSUE, "build", "sess-1", {}, db_path=db)
    blank_column(db, missing)

    with pytest.raises(traverse.TraverseError) as raised:
        traverse_issue()

    assert missing in str(raised.value)


def test_a_sweep_writes_a_report_for_a_job_whose_process_is_already_gone(
    db: Path, traverse_issue: Callable[..., Any]
) -> None:
    """Completing the books is the duty, whether or not anything is left to kill."""
    ledger.job_launch(REPO, ISSUE, "build", "sess-long-gone", {}, db_path=db)

    traverse_issue()

    reports = [
        row
        for row in ledger_rows(db)
        if row.kind == "job-report" and row.payload.get("swept")
    ]
    assert reports[0].node == "build"
    assert reports[0].payload["process_outcome"] == "died"
    assert "kill" not in reports[0].payload


# --- the cycle headers, the loop's durable state ---


def test_a_cycle_header_is_parsed_into_the_four_fields_it_carries() -> None:
    """The header a review posts, read back exactly as the probe measured it."""
    headers = traverse.parse_cycle_headers(
        ["bug review · 4b43af9 · cycle 1 · 0198a1b2-7c3d-4e5f-8a9b-c0d1e2f3a4b5"]
    )

    assert headers == {
        "bug review": traverse.CycleHeader(
            review="bug review",
            sha="4b43af9",
            cycle=1,
            session_id="0198a1b2-7c3d-4e5f-8a9b-c0d1e2f3a4b5",
        )
    }


def test_a_track_that_sat_out_a_cycle_keeps_its_own_last_reviewed_sha() -> None:
    """Two tracks at different cycles, each answered for out of its own headers.

    The doc track sat out cycle 2, so the newest header on the pull request is
    the code track's. Handed that one it would start its delta at `bbbbbbb` — a
    commit it never read — and everything between `aaaaaaa` and there would go
    unreviewed with nobody saying so.
    """
    headers = traverse.parse_cycle_headers(
        [
            "code review · aaaaaaa · cycle 1 · sess-code-1",
            "doc review · aaaaaaa · cycle 1 · sess-doc-1",
            "code review · bbbbbbb · cycle 2 · sess-code-2",
        ]
    )

    assert headers["doc review"].sha == "aaaaaaa"
    assert headers["doc review"].cycle == 1
    assert headers["code review"].sha == "bbbbbbb"
    assert headers["code review"].cycle == 2


@pytest.mark.parametrize(
    "line",
    [
        "",
        "Looks good to me.",
        "bug review · 4b43af9 · cycle one · sess-1",
        "bug review · 4b43af9 · cycle 1",
        "bug review · 4b43af9 · round 1 · sess-1",
    ],
)
def test_a_line_that_is_not_a_cycle_header_is_passed_over(line: str) -> None:
    """A comment carrying no header is the user's, and the user writes anything."""
    assert traverse.parse_cycle_headers([line]) == {}


def test_a_pull_request_with_no_headers_yet_is_about_to_run_cycle_one() -> None:
    assert traverse.next_cycle({}) == 1


def test_the_next_cycle_is_one_past_the_highest_header_on_the_pull_request() -> None:
    """The loop's own count, across every track — not any one track's.

    The doc track is a cycle behind here, and a count taken from it would run
    cycle 2 a second time and give the cap a clock that never advances.
    """
    headers = traverse.parse_cycle_headers(
        [
            "doc review · aaaaaaa · cycle 1 · sess-doc-1",
            "code review · bbbbbbb · cycle 2 · sess-code-2",
        ]
    )

    assert traverse.next_cycle(headers) == 3


# --- electing the tracks from the changed files ---


def changed(
    path: str, *, status: str = "modified", additions: int = 1, deletions: int = 1
) -> Any:
    """One entry of the pull request's file list, as the election reads it."""
    return traverse.ChangedFile(
        path=path, status=status, additions=additions, deletions=deletions
    )


def test_a_diff_touching_code_elects_the_code_track() -> None:
    assert traverse.elect_tracks([changed("src/dev_playbook/factory/traverse.py")]) == (
        traverse.CODE_TRACK,
    )


@pytest.mark.parametrize(
    "path", ["scripts/hook", "Makefile", "run.sh", "pyproject.toml"]
)
def test_a_file_that_is_neither_markdown_nor_html_is_code(path: str) -> None:
    """Extensionless scripts, hooks, `Makefile*` and config all count as code."""
    assert traverse.elect_tracks([changed(path)]) == (traverse.CODE_TRACK,)


def test_a_documentation_only_diff_elects_the_doc_track() -> None:
    """Small, modified, incidental by every other rule — and still reviewed.

    A doc-only diff has no code track to carry it, so nothing else would read
    it at all.
    """
    assert traverse.elect_tracks(
        [changed("software-factory/factory-operations.md", additions=1, deletions=1)]
    ) == (traverse.DOC_TRACK,)


def test_a_new_document_beside_code_elects_the_doc_track() -> None:
    assert traverse.elect_tracks(
        [
            changed("src/dev_playbook/factory/traverse.py"),
            changed("software-factory/review-loop.md", status="added", additions=4),
        ]
    ) == (traverse.CODE_TRACK, traverse.DOC_TRACK)


def test_ten_changed_documentation_lines_beside_code_elect_the_doc_track() -> None:
    assert traverse.elect_tracks(
        [
            changed("src/dev_playbook/factory/traverse.py"),
            changed("software-factory/software-factory.md", additions=6, deletions=4),
        ]
    ) == (traverse.CODE_TRACK, traverse.DOC_TRACK)


def test_incidental_documentation_beside_code_leaves_the_doc_track_out() -> None:
    """Nine changed lines in an existing document is the echo a code change forces."""
    assert traverse.elect_tracks(
        [
            changed("src/dev_playbook/factory/traverse.py"),
            changed("software-factory/software-factory.md", additions=5, deletions=4),
        ]
    ) == (traverse.CODE_TRACK,)


def test_a_diff_of_ignored_files_alone_elects_no_track() -> None:
    """The caller escalates on this: the loop never converges on an unread PR."""
    assert traverse.elect_tracks([changed("dotfiles/report.html")]) == ()


def test_an_empty_diff_elects_no_track() -> None:
    assert traverse.elect_tracks([]) == ()


# --- the verdict, computed from thread state ---


def thread(
    severity: str = "Blocking",
    *,
    resolved: bool = False,
    thread_id: str = "PRRT_kwDO1",
    path: str = "src/dev_playbook/factory/traverse.py",
    line: int | None = 41,
) -> Any:
    """One review thread, shaped the way the GraphQL read hands it over."""
    return traverse.ReviewThread(
        thread_id=thread_id,
        resolved=resolved,
        path=path,
        line=line,
        body=f"{severity} — the scheme read falls back silently.\n\n"
        f"— code review · 0198a1b2-7c3d-4e5f-8a9b-0c1d2e3f4a5b",
    )


def test_an_open_blocking_thread_makes_the_cycle_a_rework_lap() -> None:
    verdict = traverse.compute_verdict([thread("Blocking")], cycle=1, baseline=0)

    assert verdict.verdict == traverse.REWORK
    assert verdict.open_blocking == (thread("Blocking"),)


def test_a_cycle_with_no_open_blocking_thread_has_converged() -> None:
    """Open Suggestions stay open — convergence is on Blocking alone."""
    verdict = traverse.compute_verdict(
        [thread("Blocking", resolved=True), thread("Suggestion")], cycle=2, baseline=0
    )

    assert verdict.verdict == traverse.CONVERGED
    assert verdict.open_blocking == ()


def test_the_verdict_tallies_both_severities_open_and_resolved() -> None:
    verdict = traverse.compute_verdict(
        [
            thread("Blocking", thread_id="PRRT_1"),
            thread("Blocking", thread_id="PRRT_2", resolved=True),
            thread("Blocking", thread_id="PRRT_3", resolved=True),
            thread("Suggestion", thread_id="PRRT_4"),
            thread("Suggestion", thread_id="PRRT_5"),
            thread("Suggestion", thread_id="PRRT_6", resolved=True),
        ],
        cycle=1,
        baseline=0,
    )

    assert verdict.blocking_open == 1
    assert verdict.blocking_resolved == 2
    assert verdict.suggestion_open == 2
    assert verdict.suggestion_resolved == 1


def test_a_thread_opening_on_neither_severity_is_tallied_as_neither() -> None:
    """A comment carrying no severity and no attribution is the user's own."""
    verdict = traverse.compute_verdict(
        [
            traverse.ReviewThread(
                thread_id="PRRT_user",
                resolved=False,
                path="README.md",
                line=1,
                body="Why is this here?",
            )
        ],
        cycle=1,
        baseline=0,
    )

    assert verdict.verdict == traverse.CONVERGED
    assert (verdict.blocking_open, verdict.suggestion_open) == (0, 0)


@pytest.mark.parametrize("written", ["Blocking", "blocking", "**Blocking**"])
def test_the_severity_is_the_first_word_however_it_is_decorated(written: str) -> None:
    """Missing a Blocking thread declares a convergence that never happened."""
    verdict = traverse.compute_verdict([thread(written)], cycle=1, baseline=0)

    assert verdict.blocking_open == 1


def test_the_third_autonomous_cycle_past_the_baseline_still_reworks() -> None:
    verdict = traverse.compute_verdict([thread("Blocking")], cycle=3, baseline=0)

    assert verdict.verdict == traverse.REWORK


def test_the_fourth_autonomous_cycle_past_the_baseline_caps_out() -> None:
    verdict = traverse.compute_verdict([thread("Blocking")], cycle=4, baseline=0)

    assert verdict.verdict == traverse.CAP_ESCALATED


def test_the_cap_counts_from_the_baseline_rather_than_from_cycle_zero() -> None:
    """A user-ordered lap moves the baseline, and the clock restarts behind it."""
    assert (
        traverse.compute_verdict([thread("Blocking")], cycle=5, baseline=2).verdict
        == traverse.REWORK
    )
    assert (
        traverse.compute_verdict([thread("Blocking")], cycle=6, baseline=2).verdict
        == traverse.CAP_ESCALATED
    )


def test_a_cycle_past_the_cap_with_nothing_blocking_still_converges() -> None:
    """The cap ends a traverse that cannot clear its findings, not one that did."""
    verdict = traverse.compute_verdict([thread("Suggestion")], cycle=9, baseline=0)

    assert verdict.verdict == traverse.CONVERGED


# --- the baseline the cap counts from ---


def starts(db: Path) -> Any:
    """This issue's `traverse-start` rows, through the reader the loop uses."""
    return ledger.traverse_starts(repo=REPO, issue=ISSUE, db_path=db)


def test_an_issue_with_no_recorded_baseline_counts_from_zero(db: Path) -> None:
    ledger.traverse_start(REPO, ISSUE, {"mode": "auto"}, db_path=db)

    assert traverse.baseline_cycle(starts(db)) == 0


def test_an_issue_that_never_started_counts_from_zero(db: Path) -> None:
    assert traverse.baseline_cycle(starts(db)) == 0


def test_the_baseline_is_the_highest_one_any_start_recorded(db: Path) -> None:
    """The newest baseline, whichever start carries it — the clock never resets."""
    ledger.traverse_start(REPO, ISSUE, {"mode": "auto"}, db_path=db)
    ledger.traverse_start(
        REPO, ISSUE, {"mode": "user-rework", "baseline_cycle": 5}, db_path=db
    )
    ledger.traverse_start(
        REPO, ISSUE, {"mode": "auto", "baseline_cycle": 2}, db_path=db
    )

    assert traverse.baseline_cycle(starts(db)) == 5


def test_a_baseline_that_is_not_a_whole_number_stops_the_traverse(db: Path) -> None:
    """Read past, it would give the cap a clock nobody can reason about."""
    ledger.traverse_start(REPO, ISSUE, {"baseline_cycle": "3"}, db_path=db)

    with pytest.raises(traverse.TraverseError):
        traverse.baseline_cycle(starts(db))


# --- the rework prompt ---


def test_the_rework_prompt_names_the_issue_and_every_thread_and_where_it_sits() -> None:
    prompt = traverse.rework_prompt(
        ISSUE,
        [
            thread(thread_id="PRRT_one", path="src/a.py", line=41),
            thread(thread_id="PRRT_two", path="docs/b.md", line=7),
        ],
    )

    assert prompt.splitlines()[0] == str(ISSUE)
    assert "PRRT_one" in prompt
    assert "src/a.py:41" in prompt
    assert "PRRT_two" in prompt
    assert "docs/b.md:7" in prompt


def test_the_rework_prompt_locates_an_outdated_thread_by_its_file() -> None:
    """A fix that edits the anchored line leaves the thread with no live line."""
    prompt = traverse.rework_prompt(
        ISSUE, [thread(thread_id="PRRT_gone", path="src/a.py", line=None)]
    )

    assert "src/a.py" in prompt


def test_the_rework_prompt_pastes_none_of_the_finding_text() -> None:
    """The thread is read from GitHub; a paste is a second copy that goes stale."""
    prompt = traverse.rework_prompt(ISSUE, [thread()])

    assert "falls back silently" not in prompt


def test_the_rework_prompt_carries_each_fix_now_item_and_the_fix_it_asks_for() -> None:
    """A fix-now ruling is written nowhere else, so the prompt carries its text.

    The address-not-content rule holds for every thread the node reads live; a
    fix-now item is the deliberate exception, because the ruling exists only in
    the report the adjudicator has just made.
    """
    prompt = traverse.rework_prompt(
        ISSUE,
        [thread(thread_id="PRRT_blocking")],
        [
            traverse.FixNow(
                thread="PRRT_suggestion", fix="name the constant as the review states"
            )
        ],
    )

    assert "PRRT_blocking" in prompt
    assert "PRRT_suggestion" in prompt
    assert "name the constant as the review states" in prompt


def test_a_rework_prompt_with_no_fix_now_item_offers_the_builder_none() -> None:
    """A lap with no suggestion ruled fix-now is the prompt as it always was."""
    prompt = traverse.rework_prompt(ISSUE, [thread()])

    assert "fix now" not in prompt.lower()


def test_the_rework_prompt_carries_the_resolution_rules() -> None:
    """Reply on what you fixed; the next cycle's reviewer resolves what it verifies."""
    prompt = traverse.rework_prompt(ISSUE, [thread()])

    assert "gh api" in prompt
    assert "Fixed in <sha>" in prompt
    assert "resolve" in prompt


# --- the review loop, through the fake claude and the stub gh ---


def head_sha(checkout: Path) -> str:
    """The short sha the issue's worktree is on — what a review headers with."""
    return subprocess.run(
        ["git", "-C", str(worktree_of(checkout)), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def worktree_of(checkout: Path) -> Path:
    """Where this issue's worktree sits inside its checkout."""
    return checkout / ".claude" / "worktrees" / BRANCH


def nodes_launched(launched: Callable[[], list[dict[str, Any]]]) -> list[str]:
    """Every node the traverse launched, sorted — a fan-out has no fixed order."""
    return sorted(launch["node"] for launch in launched())


def test_a_first_cycle_with_no_blocking_thread_converges_and_ends_pr_ready(
    db: Path,
    checkout: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Convergence is on Blocking alone, and the open Suggestion is then settled.

    The verdict is computed first and records the Suggestion as open, which is
    what it was at that moment; the adjudicator runs on that verdict and
    disposes of it, so the traverse ends with nothing left pending on it.
    """
    outcome = traverse_issue(gh_cmd=stub_gh(threads={1: [suggestion_thread()]}))

    assert nodes_launched(launched) == [
        "adjudicator",
        "bug-pr-review",
        "build",
        "code-pr-review",
        "open-pr",
    ]
    assert payload_of(db, "verdict") == {
        "pr": PR_URL,
        "cycle": 1,
        "sha": head_sha(checkout),
        "blocking_open": 0,
        "blocking_resolved": 0,
        "suggestion_open": 1,
        "suggestion_resolved": 0,
        "verdict": "converged",
    }
    assert outcome == traverse.TraverseOutcome("pr-ready", pr_url=PR_URL)


def test_an_open_blocking_thread_reworks_and_the_loop_goes_round_again(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    gh_calls: Callable[[], list[list[str]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Cycle 1 finds a Blocking thread; the lap that follows clears it.

    The board never moves inside the loop: the one label write in the whole
    traverse is the graph's own `build -> pr-review`.
    """
    outcome = traverse_issue(gh_cmd=stub_gh(threads={1: [blocking_thread()], 2: []}))

    builds = [launch for launch in launched() if launch["node"] == "build"]
    assert len(builds) == 2
    assert "PRRT_blocking" in builds[1]["prompt"]
    assert [payload["verdict"] for payload in payloads_of(db, "verdict")] == [
        "rework",
        "converged",
    ]
    assert [payload["cycle"] for payload in payloads_of(db, "verdict")] == [1, 2]
    assert len([call for call in gh_calls() if call[:2] == ["issue", "edit"]]) == 1
    assert outcome.status == "pr-ready"


def test_a_returning_track_is_prompted_with_its_own_sha_not_a_siblings(
    checkout: Path,
    world: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The code review has read this branch once; the bug review never has.

    So one of them is given a sha to take its delta from and the other is given
    the issue number alone. Handed the newest header on the pull request, the
    bug review would start at a commit it never read.
    """
    add_worktree(checkout, BRANCH)
    push_branch(checkout, BRANCH)
    seed_review(world, "code review", cycle=1, sha="deadbee")

    traverse_issue(gh_cmd=stub_gh(PR_REVIEW_LABELS))

    prompts = {launch["node"]: launch["prompt"] for launch in launched()}
    assert prompts["code-pr-review"] == f"{ISSUE} deadbee"
    assert prompts["bug-pr-review"] == str(ISSUE)


def test_a_traverse_relaunched_mid_loop_runs_the_next_cycle_through_one_path(
    db: Path,
    checkout: Path,
    world: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """A store and a pull request left at cycle 2 relaunch into cycle 3.

    No resume branch reads any of this: the cycle is one past the highest header
    the pull request carries, and the verdict is computed from live thread state.
    The cycle a crashed traverse was part-way through is burned, which is the
    accepted cost of a loop that keeps no state of its own.
    """
    add_worktree(checkout, BRANCH)
    push_branch(checkout, BRANCH)
    for cycle in (1, 2):
        seed_review(world, "bug review", cycle=cycle, sha="deadbee")
        seed_review(world, "code review", cycle=cycle, sha="deadbee")

    outcome = traverse_issue(gh_cmd=stub_gh(PR_REVIEW_LABELS))

    assert [payload["cycle"] for payload in payloads_of(db, "verdict")] == [3]
    assert outcome.status == "pr-ready"


def test_one_review_failing_lets_its_siblings_finish_before_the_traverse_ends(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The books come first, the escalation second, and nothing is retried.

    Each launch has a `job-launch` row that only its own report closes, so a
    sibling the traverse walked away from would read as live for good. Every job
    is waited out before any failure is relayed.
    """
    outcome = traverse_issue(
        claude_cmd=fake_claude(
            **{
                "bug-pr-review": node_step(
                    [HOOK_LINE, init_line(), result_line(ESCALATED_REVIEW)]
                )
            }
        )
    )

    reported = [row for row in ledger_rows(db) if row.kind == "job-report"]
    assert {row.node for row in reported} == {
        "build",
        "open-pr",
        "bug-pr-review",
        "code-pr-review",
    }
    written = kinds(db)
    assert written.index("traverse-escalation") > max(
        at for at, kind in enumerate(written) if kind == "job-report"
    )
    assert "bug-pr-review" in str(payload_of(db, "traverse-escalation")["reason"])
    assert len([launch for launch in launched() if launch["node"] == "build"]) == 1
    assert outcome.status == "escalated"


def test_a_review_that_never_spawns_is_relayed_like_any_other_failure(
    db: Path,
    agents_dir: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """One reviewer aborts before spawning; its sibling still runs and reports.

    An abort is raised rather than reported — nothing spawned, so there is no
    stream to classify — and it is the one exception a fanned-out review catches,
    exactly as the sequential path catches it. It comes back as that job's
    failure and is relayed beside anything else the cycle turned up.

    The definition here declares an effort the harness does not have, which the
    launcher refuses per node: the whole-roster check at traverse start only asks
    that each definition exists.
    """
    write_definition(
        agents_dir,
        "bug-pr-review",
        {
            "name": "bug-pr-review",
            "description": "The bug-pr-review node.",
            "model": "sonnet",
            "effort": "turbo",
        },
    )

    outcome = traverse_issue()

    assert "code-pr-review" in [launch["node"] for launch in launched()]
    assert "code-pr-review" in {
        row.node for row in ledger_rows(db) if row.kind == "job-report"
    }
    reason = str(payload_of(db, "traverse-escalation")["reason"])
    assert "bug-pr-review could not be launched" in reason
    assert outcome.status == "escalated"


def test_a_diff_no_review_reads_escalates_rather_than_converging(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Converging here would hand back a pull request nobody had read."""
    outcome = traverse_issue(
        gh_cmd=stub_gh(files=[["dotfiles/report.html", "modified", 4, 2]])
    )

    assert nodes_launched(launched) == ["build", "open-pr"]
    assert "verdict" not in kinds(db)
    assert "no review track" in str(payload_of(db, "traverse-escalation")["reason"])
    assert outcome.status == "escalated"


def test_a_thread_carrying_no_comment_stops_the_traverse(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """A thread with nothing to read a severity from is refused, never graded.

    Every severity comes from the first word of a thread's first comment, so a
    thread that arrives with no comment has no severity at all. Passed over it
    would count as neither Blocking nor Suggestion and drop out of the tally in
    silence — a convergence declared over a finding nobody read.
    """
    outcome = traverse_issue(gh_cmd=stub_gh(threads={1: [commentless_thread()]}))

    reason = str(payload_of(db, "traverse-escalation")["reason"])
    assert "PRRT_silent" in reason
    assert "verdict" not in kinds(db)
    assert outcome.status == "escalated"


def test_the_cycles_reviews_really_do_run_at_the_same_time(
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Each review refuses to finish until it can see the other one running.

    A launcher that ran them one after another could never satisfy both: the
    first would wait out its whole budget for a peer that has not been spawned
    yet, exit unmet, and end the traverse escalated.
    """
    both = {
        node: node_step(
            [HOOK_LINE, init_line(), result_line(REVIEWED_REPORT)], await_peers=4
        )
        for node in ("bug-pr-review", "code-pr-review")
    }

    outcome = traverse_issue(claude_cmd=fake_claude(**both), timeout_s=PATIENT_DEADLINE)

    assert outcome.status == "pr-ready"


def test_a_documentation_only_diff_runs_the_doc_review_alone(
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(gh_cmd=stub_gh(files=[DOC_FILE]))

    assert nodes_launched(launched) == [
        "adjudicator",
        "build",
        "doc-pr-review",
        "open-pr",
    ]
    assert outcome.status == "pr-ready"


# --- the adjudicator, launched at the loop's verdict points ---


def decisions(db: Path) -> list[str]:
    """Each verdict the loop reached and each node it launched on one, in order.

    The cycle's reviews are left out. They fan out concurrently, so their launch
    rows land in whichever order the pool finished them in, and what this is
    measuring is the sequence the loop itself decides: the verdict is recorded,
    and only then is anything launched on it.
    """
    order = []
    for row in ledger_rows(db):
        if row.kind == "verdict":
            order.append(f"verdict:{row.payload['verdict']}")
        elif row.kind == "job-launch" and row.payload["node"] not in REVIEW_NAMES:
            order.append(str(row.payload["node"]))
    return order


def prompts_to(launched: Callable[[], list[dict[str, Any]]], node: str) -> list[str]:
    """Every prompt one node was launched under, in launch order."""
    return [launch["prompt"] for launch in launched() if launch["node"] == node]


def test_a_converged_verdict_always_runs_the_adjudicator_before_the_traverse_ends(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Even with nothing open to settle: the convergence run is what makes the
    pull request's two disposition sections complete at the merge read."""
    outcome = traverse_issue(
        gh_cmd=stub_gh(threads={1: []}),
        claude_cmd=fake_claude(
            adjudicator=node_step(
                [HOOK_LINE, init_line(), result_line(NOTHING_SETTLED)]
            )
        ),
    )

    assert decisions(db) == ["build", "open-pr", "verdict:converged", "adjudicator"]
    assert prompts_to(launched, "adjudicator") == [f"{ISSUE} converged"]
    assert payload_of(db, "traverse-end") == {"status": "pr-ready", "pr_url": PR_URL}
    assert outcome == traverse.TraverseOutcome("pr-ready", pr_url=PR_URL)


def test_a_rework_verdict_with_open_suggestions_adjudicates_before_the_next_build(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The lap the Blocking threads already necessitate is what a fix now rides.

    So the adjudicator runs between the verdict and the relaunch: its ruling has
    to exist before the prompt that carries it is assembled.
    """
    outcome = traverse_issue(
        gh_cmd=stub_gh(
            threads={1: [blocking_thread(), suggestion_thread()], 2: []},
        )
    )

    assert decisions(db) == [
        "build",
        "open-pr",
        "verdict:rework",
        "adjudicator",
        "build",
        "verdict:converged",
        "adjudicator",
    ]
    assert prompts_to(launched, "adjudicator")[0] == f"{ISSUE} rework"
    relaunch = prompts_to(launched, "build")[1]
    assert "PRRT_blocking" in relaunch
    assert "PRRT_suggestion" in relaunch
    assert "name the constant as the review states" in relaunch
    assert outcome.status == "pr-ready"


def test_a_rework_verdict_with_no_open_suggestion_launches_no_adjudicator(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Nothing to settle is no job: the docket is the open Suggestion threads."""
    traverse_issue(gh_cmd=stub_gh(threads={1: [blocking_thread()], 2: []}))

    assert decisions(db) == [
        "build",
        "open-pr",
        "verdict:rework",
        "build",
        "verdict:converged",
        "adjudicator",
    ]


def test_a_cap_escalation_launches_no_adjudicator(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The traverse is ending, and nothing it settled now would be read."""
    outcome = traverse_issue(
        gh_cmd=stub_gh(threads={1: [blocking_thread(), suggestion_thread()]})
    )

    assert decisions(db)[-1] == "verdict:cap-escalated"
    assert decisions(db).count("adjudicator") == 3
    assert outcome.status == "escalated"


# Every way the adjudicator can come back other than clean and reporting done.
# One job, no retry, and what it said rides the escalation.
FAILING_ADJUDICATIONS: list[tuple[str, dict[str, Any], tuple[str, str | None]]] = [
    (
        "died",
        node_step([HOOK_LINE, init_line()], exit_code=1),
        ("died", None),
    ),
    (
        "schema-refused",
        node_step([HOOK_LINE, init_line(), result_line(None)]),
        ("schema-refused", None),
    ),
    (
        "task-escalated",
        node_step([HOOK_LINE, init_line(), result_line(ESCALATED_REPORT)]),
        ("clean", "escalated"),
    ),
]


@pytest.mark.parametrize(
    ("step", "classification"),
    [(step, classification) for _, step, classification in FAILING_ADJUDICATIONS],
    ids=[name for name, _, _ in FAILING_ADJUDICATIONS],
)
def test_an_adjudication_that_does_not_come_back_clean_and_done_ends_the_traverse(
    step: dict[str, Any],
    classification: tuple[str, str | None],
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    stub_gh: Callable[..., tuple[str, ...]],
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(
        gh_cmd=stub_gh(threads={1: []}), claude_cmd=fake_claude(adjudicator=step)
    )

    assert outcome.status == "escalated"
    assert [launch["node"] for launch in launched()].count("adjudicator") == 1
    assert payload_of(db, "traverse-end") == {"status": "escalated"}
    report = payloads_of(db, "job-report")[-1]
    assert (report["process_outcome"], report["task_outcome"]) == classification
    assert payload_of(db, "traverse-escalation")["node"] == "adjudicator"


def test_a_fix_now_ruling_carrying_no_fix_ends_the_traverse_escalated(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    fake_claude: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The ruling is written nowhere else, so an empty one is a lost finding.

    The builder would be handed a thread id it was told to fix and no statement
    of what the fix is — and the thread's own text is a suggestion nobody ruled
    on, which is what the ruling was there to replace.
    """
    silent = {
        "outcome": "done",
        "gist": "One suggestion settled on PR #12.",
        "dispositions": [{"thread": "PRRT_suggestion", "outcome": "fix-now"}],
        "callouts": [],
    }

    outcome = traverse_issue(
        gh_cmd=stub_gh(threads={1: [blocking_thread(), suggestion_thread()], 2: []}),
        claude_cmd=fake_claude(
            adjudicator=node_step([HOOK_LINE, init_line(), result_line(silent)])
        ),
    )

    assert outcome.status == "escalated"
    assert payload_of(db, "traverse-escalation")["node"] == "adjudicator"
    assert payload_of(db, "traverse-end") == {"status": "escalated"}


def test_a_graph_with_no_adjudicator_definition_is_refused_before_anything_spawns(
    db: Path,
    agents_dir: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    """The roster is checked whole, at the start, and the adjudicator is on it."""
    (agents_dir / "adjudicator.md").unlink()

    outcome = traverse_issue()

    assert launched() == []
    assert "adjudicator" in payload_of(db, "traverse-escalation")["reason"]
    assert outcome.status == "escalated"


def test_blocking_threads_that_survive_the_cap_end_the_traverse_escalated(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    traverse_issue: Callable[..., Any],
) -> None:
    """Four autonomous cycles past the baseline, and the finding is still open."""
    outcome = traverse_issue(gh_cmd=stub_gh(threads={1: [blocking_thread()]}))

    assert [payload["verdict"] for payload in payloads_of(db, "verdict")] == [
        "rework",
        "rework",
        "rework",
        "cap-escalated",
    ]
    escalation = payload_of(db, "traverse-escalation")
    assert (escalation["cycle"], escalation["baseline"]) == (4, 0)
    assert payload_of(db, "traverse-end") == {"status": "escalated"}
    assert outcome.status == "escalated"
