import fcntl
import json
import signal
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import commit_all, init_repo

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

# A stand-in for gh, answering the four calls the traverse makes off a real bare
# origin repo, so a sha it reports is the sha origin genuinely holds. Every
# invocation is appended to `calls.jsonl`, which is how a test sees the single
# label move. A branch named in the plan's `shas` overrides the mirror — that is
# how a test makes `origin/main` stale after the fetch, or makes the issue
# branch missing on origin, without touching the repos themselves.
STUB_GH = """
import json
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
plan = json.loads((here / "plan.json").read_text())
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


if argv[:2] == ["issue", "view"]:
    print("\\n".join(plan["labels"]))
elif argv[:2] == ["issue", "edit"]:
    pass
elif argv[:1] == ["api"]:
    branch = argv[1].rsplit("/branches/", 1)[1]
    sha = origin_sha(branch)
    if sha is None:
        sys.stderr.write("gh: Not Found (HTTP 404)\\n")
        raise SystemExit(1)
    print(sha)
elif argv[:2] == ["pr", "list"]:
    if plan["pr_url"]:
        print(plan["pr_url"])
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

here = Path(__file__).parent
plan = json.loads((here / "plan.json").read_text())
argv = sys.argv[1:]
node = argv[argv.index("--agent") + 1]
session = argv[argv.index("--session-id") + 1]
step = plan[node]
with (here / "launched.jsonl").open("a") as log:
    log.write(
        json.dumps(
            {"node": node, "session": session, "cwd": os.getcwd(), "pid": os.getpid()}
        )
        + "\\n"
    )
if step["commit"]:
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
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
    linger: float = 0.0,
    exit_code: int = 0,
    ignore_sigterm: bool = False,
) -> dict[str, Any]:
    """One node's plan for the fake claude — what it does, says, and exits with."""
    if lines is None:
        lines = [HOOK_LINE, init_line(), result_line(DONE_REPORT)]
    return {
        "lines": lines,
        "commit": commit,
        "push": push,
        "linger": linger,
        "exit_code": exit_code,
        "ignore_sigterm": ignore_sigterm,
    }


def clean_build() -> dict[str, Any]:
    """A build that commits its work, pushes the branch, and reports done."""
    return node_step(commit=True, push=True)


# The plan every fake claude starts from: both nodes clean, the build committing
# and pushing the branch its verification then reads back off origin.
DEFAULT_STEPS: dict[str, dict[str, Any]] = {
    "build": clean_build(),
    "open-pr": node_step(),
}


def process_state(pid: int) -> str | None:
    """The single-letter process-table state of `pid`, or None once it is gone.

    Read from ``/proc`` rather than asked with ``os.kill(pid, 0)``: a signal probe
    answers "alive" for a zombie, and a child whose traverse was destroyed is
    reparented, so it is a zombie until the reaper collects it. What is under test
    is that it stopped running.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # The comm field is parenthesized and may hold spaces of its own, so the
    # split starts after the last ')' rather than at the second field.
    return stat.rpartition(")")[2].split()[0]


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


def write_definition(directory: Path, stem: str, frontmatter: dict[str, Any]) -> Path:
    """Write one agent definition, its frontmatter rendered as YAML."""
    body = "\n".join(f"{key}: {value}" for key, value in frontmatter.items())
    path = directory / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{body}\n---\n\nThe node's instructions.\n")
    return path


def ledger_rows(db: Path) -> list[tuple[str, str | None, dict[str, Any]]]:
    """Every ledger row as (kind, node, payload), in write order."""
    if not db.exists():
        return []
    with sqlite3.connect(db) as connection:
        rows = connection.execute(
            "SELECT kind, node, payload FROM ledger ORDER BY id"
        ).fetchall()
    return [(kind, node, json.loads(payload)) for kind, node, payload in rows]


def kinds(db: Path) -> list[str]:
    """The kinds the ledger holds, in write order."""
    return [kind for kind, _, _ in ledger_rows(db)]


def payload_of(db: Path, kind: str) -> dict[str, Any]:
    """The payload of the one row of `kind` the ledger holds."""
    (row,) = [payload for stored, _, payload in ledger_rows(db) if stored == kind]
    return row


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
def stub_gh(tmp_path: Path, origin: Path) -> Callable[..., tuple[str, ...]]:
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
    ) -> tuple[str, ...]:
        (here / "plan.json").write_text(
            json.dumps(
                {
                    "origin": str(origin),
                    "labels": BUILD_LABELS if labels is None else labels,
                    "shas": shas or {},
                    "pr_url": pr_url,
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
def fake_claude(tmp_path: Path) -> Callable[..., tuple[str, ...]]:
    """Write the stand-in claude for one test and return the command that runs it."""
    here = tmp_path / "fake"
    here.mkdir()
    script = here / "claude.py"
    script.write_text(FAKE_CLAUDE)

    def plan(**steps: dict[str, Any]) -> tuple[str, ...]:
        (here / "plan.json").write_text(json.dumps({**DEFAULT_STEPS, **steps}))
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


def test_a_build_phase_issue_runs_both_nodes_and_ends_pr_ready(
    db: Path,
    launched: Callable[[], list[dict[str, Any]]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue()

    assert [launch["node"] for launch in launched()] == ["build", "open-pr"]
    assert kinds(db) == [
        "traverse-start",
        "job-launch",
        "job-report",
        "phase-transition",
        "job-launch",
        "job-report",
        "traverse-end",
    ]
    assert payload_of(db, "phase-transition") == {"from": "build", "to": "pr-review"}
    assert payload_of(db, "traverse-end") == {"status": "pr-ready", "pr_url": PR_URL}
    assert outcome == traverse.TraverseOutcome("pr-ready", pr_url=PR_URL)


def test_a_pr_review_phase_issue_skips_the_build_and_launches_open_pr_alone(
    db: Path,
    stub_gh: Callable[..., tuple[str, ...]],
    launched: Callable[[], list[dict[str, Any]]],
    gh_calls: Callable[[], list[list[str]]],
    traverse_issue: Callable[..., Any],
) -> None:
    outcome = traverse_issue(gh_cmd=stub_gh(PR_REVIEW_LABELS))

    assert [launch["node"] for launch in launched()] == ["open-pr"]
    assert "phase-transition" not in kinds(db)
    assert not [call for call in gh_calls() if call[:2] == ["issue", "edit"]]
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


def test_an_existing_worktree_is_reused_exactly_as_it_was_found(
    checkout: Path, traverse_issue: Callable[..., Any]
) -> None:
    """No freshness check and no rebase: work in flight is left where it is."""
    worktree = add_worktree(checkout, BRANCH)
    carried_over = worktree / "work-in-flight.txt"
    carried_over.write_text("from the last lap\n")

    traverse_issue()

    assert carried_over.read_text() == "from the last lap\n"


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
        payload
        for kind, _, payload in ledger_rows(db)
        if kind == "job-report" and payload.get("swept") == "orphan-recovery"
    ]
    assert len(swept) == 1
    assert swept[0]["process_outcome"] == "died"
    assert orphaned not in [row.session_id for row in ledger.live_jobs(db_path=db)]
    assert [row.session_id for row in ledger.live_jobs(db_path=db)] == [
        "sess-elsewhere"
    ]


def test_a_sweep_writes_a_report_for_a_job_whose_process_is_already_gone(
    db: Path, traverse_issue: Callable[..., Any]
) -> None:
    """Completing the books is the duty, whether or not anything is left to kill."""
    ledger.job_launch(REPO, ISSUE, "build", "sess-long-gone", {}, db_path=db)

    traverse_issue()

    reports = [
        (node, payload)
        for kind, node, payload in ledger_rows(db)
        if kind == "job-report" and payload.get("swept")
    ]
    assert reports[0][1]["process_outcome"] == "died"
    assert reports[0][1]["kill"] is None
