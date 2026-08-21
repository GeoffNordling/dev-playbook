import json
import locale
import os
import signal
import sqlite3
import subprocess
import sys
import time
from collections.abc import Callable, Iterator
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

from dev_playbook.factory import launcher, ledger

# The job every test launches unless it says otherwise.
REPO = "owner/repo"
ISSUE = 7
NODE = "build"
PROMPT = "Carry out issue #7."
LAUNCH_PAYLOAD: dict[str, Any] = {"phase": "build", "lap": 1}

# A node report schema in the epic's shape: a required top-level `outcome` the
# task layer reads, and a required `gist` it does not.
SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "outcome": {"type": "string", "enum": ["done", "escalated"]},
        "gist": {"type": "string"},
    },
    "required": ["outcome", "gist"],
    "additionalProperties": False,
}

# A well-formed definition for the `build` node, and the three ways the
# launcher must refuse one: a `name` that is not the filename stem (such a
# definition drops out of the roster silently), a missing `effort`, and an
# `effort` outside the harness's vocabulary (an invalid one is swallowed).
DEFINITION: dict[str, Any] = {
    "name": NODE,
    "description": "The build node.",
    "model": "opus",
    "effort": "high",
}
MISNAMED_DEFINITION = {**DEFINITION, "name": "builder"}
UNTUNED_DEFINITION = {"name": NODE, "description": "The build node.", "model": "opus"}
OVERTUNED_DEFINITION = {**DEFINITION, "effort": "turbo"}

# A launcher run driven from a separate process, so a test can kill the
# launcher itself rather than the child it supervises. The two module paths the
# suite redirects are set here by hand: a monkeypatched module attribute lives
# in this process alone, and a child that imports `launcher` fresh would
# otherwise sweep the machine's real `/etc` managed settings.
LAUNCH_RUNNER = """
import json
import sys
from pathlib import Path

arguments = json.loads(Path(sys.argv[1]).read_text())
sys.path.insert(0, arguments["src"])

from dev_playbook.factory import launcher

launcher.MANAGED_SETTINGS = Path(arguments["managed_settings"])
launcher.MANAGED_SETTINGS_DIR = Path(arguments["managed_settings_dir"])

launcher.launch_job(
    arguments["repo"],
    arguments["issue"],
    arguments["node"],
    Path(arguments["worktree"]),
    arguments["prompt"],
    arguments["schema"],
    arguments["launch_payload"],
    db_path=Path(arguments["db_path"]),
    agents_dir=Path(arguments["agents_dir"]),
    claude_cmd=tuple(arguments["claude_cmd"]),
    timeout_s=arguments["timeout_s"],
)
"""

# A stand-in for claude: it records the argv and placement it was spawned
# with, then emits a canned stream-json stream line by line and exits the way
# its plan says. `$CWD` in a canned line becomes the directory it really ran
# in, so a test can emit a truthful `init` without knowing the path. A canned
# line given as a string is printed verbatim, which is how a test emits a line
# that is not JSON at all; `undecodable` opens the stream with bytes no
# decoder accepts. `orphan_seconds` leaves a grandchild behind holding stdout
# open after this process is gone, the way a background bash task or an stdio
# MCP server does.
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
(here / "record.json").write_text(
    json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd(), "pid": os.getpid()})
)
if plan["orphan_seconds"]:
    subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(%s)" % plan["orphan_seconds"]]
    )
if plan["ignore_sigterm"]:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if plan["undecodable"]:
    sys.stdout.flush()
    sys.stdout.buffer.write(b"\\xff\\xfe\\n")
    sys.stdout.buffer.flush()
for line in plan["lines"]:
    if isinstance(line, str):
        print(line, flush=True)
        continue
    resolved = {k: (os.getcwd() if v == "$CWD" else v) for k, v in line.items()}
    print(json.dumps(resolved), flush=True)
time.sleep(plan["linger"])
sys.exit(plan["exit_code"])
"""

# An import of the launcher on a platform that is not Linux, run in its own
# interpreter so the substituted `sys.platform` reaches the module's own guard.
# The failure is printed rather than raised, so the test reads a result instead
# of a traceback.
PLATFORM_PROBE = """
import sys

sys.platform = "darwin"
sys.path.insert(0, sys.argv[1])
try:
    from dev_playbook.factory import launcher
except Exception as refusal:
    print(type(refusal).__name__)
    print(refusal)
"""

# Hook events precede `init` in a real stream, so every canned stream opens
# with one: the parser has to scan for `init` rather than read the first line.
HOOK_LINE: dict[str, Any] = {
    "type": "system",
    "subtype": "hook_started",
    "hook_event": "SessionStart",
}

# A line the launcher reads and drops, between `init` and the envelope.
NOISE_LINE: dict[str, Any] = {"type": "rate_limit_event", "subtype": None}

# An `init` cut off mid-write. Nothing can identify it as an `init`, which is
# exactly why a run that drops a line and never reads an `init` is refused
# rather than classified: its placement and billing were never declared.
TRUNCATED_INIT = '{"type": "system", "subtype": "init", "cwd": "/wor'

# The report a clean node returns, in the epic's envelope shape.
REPORT: dict[str, Any] = {"outcome": "done", "gist": "The issue is built."}

# The same report, its prose carrying the em-dash agent output is full of. It
# goes down the stream as a verbatim line, because `json.dumps` escapes every
# non-ASCII character by default and an all-ASCII stream would prove nothing.
NON_ASCII_REPORT: dict[str, Any] = {
    "outcome": "done",
    "gist": "The issue is built — cleanly.",
}

# How long a fake child lingers when the launcher is meant to be what ends it.
# Long enough that a missed kill fails the test by timing out rather than by
# passing for the wrong reason.
LINGER_SECONDS = 30.0

# The shrunk deadline and grace every supervision test runs under.
BRIEF_DEADLINE = 0.3
BRIEF_GRACE = 0.3

# How long a grandchild holds the stdout pipe open after its parent is gone,
# and the deadline the launcher watches that run under. The deadline is the
# looser of the two on purpose: what is under test is that supervision ends
# when the child exits, so the run must finish with the wall clock nowhere
# near spent and the pipe still held open.
ORPHAN_SECONDS = 5.0
ORPHANED_DEADLINE = 1.0

# How long the pdeathsig test waits — for the child to declare itself, and then
# for it to be gone after its launcher is destroyed. The budget is far shorter
# than `LINGER_SECONDS`, so a child that outlives its launcher fails the test
# rather than passing on a slow machine.
PDEATHSIG_BUDGET = 10.0
PDEATHSIG_POLL = 0.05

# How long a signal sent to this process is given to arrive. Delivery is a
# kernel round trip rather than a call, so a test that reads the record the
# instant after `os.kill` returns would find an empty one whatever the mask
# says -- and would pass on the broken behavior as readily as on the fixed one.
SIGNAL_SETTLE = 0.2

# The six settings files a launch is swept against, named by scope. Every one
# is a file `-p` merges, so a billing key in any of them meters the child.
SETTINGS_SCOPES = (
    "worktree",
    "worktree-local",
    "checkout-local",
    "user",
    "managed",
    "managed-drop-in",
)


@pytest.fixture
def home(tmp_path: Path) -> Path:
    """A throwaway home directory, so no sweep reads the real ``~/.claude``."""
    path = tmp_path / "home"
    (path / ".claude").mkdir(parents=True)
    return path


@pytest.fixture
def env(home: Path) -> dict[str, str]:
    """A child environment with no route to metered billing in it."""
    return {"HOME": str(home), "PATH": os.environ["PATH"]}


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """A throwaway main checkout with one commit, so a worktree can link to it."""
    root = tmp_path / "checkout"
    init_repo(root)
    (root / "README.md").write_text("fixture\n")
    commit_all(root)
    return root


@pytest.fixture
def worktree(checkout: Path, tmp_path: Path) -> Path:
    """A linked worktree of ``checkout`` — the placement every launch runs in.

    A real ``git worktree add`` rather than a stand-in, because the launcher
    derives the main checkout from the worktree's own git metadata and is never
    handed it. Every test that reaches ``checkout`` while passing only this
    path proves that derivation: the ``checkout-local`` settings scope, which
    the sweep finds, and the ``checkout`` shadow scope, which the shadow check
    scans.
    """
    path = tmp_path / "worktree"
    subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "worktree",
            "add",
            "-q",
            "-b",
            "issue-1",
            str(path),
        ],
        check=True,
        capture_output=True,
    )
    return path


@pytest.fixture(autouse=True)
def managed_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Point the managed-settings roster at an empty temp tree, never ``/etc``.

    Autouse, so no test in this module can read the machine's real managed
    settings by forgetting to ask. Returns the redirected file and drop-in
    directory for the tests that write into them.
    """
    settings = tmp_path / "etc" / "managed-settings.json"
    drop_in = tmp_path / "etc" / "managed-settings.d"
    monkeypatch.setattr(launcher, "MANAGED_SETTINGS", settings)
    monkeypatch.setattr(launcher, "MANAGED_SETTINGS_DIR", drop_in)
    return settings, drop_in


@pytest.fixture
def roster(
    worktree: Path, checkout: Path, home: Path, managed_settings: tuple[Path, Path]
) -> dict[str, Path]:
    """Every settings file the sweep reads, by the scope it belongs to."""
    managed, drop_in = managed_settings
    return {
        "worktree": worktree / ".claude" / "settings.json",
        "worktree-local": worktree / ".claude" / "settings.local.json",
        "checkout-local": checkout / ".claude" / "settings.local.json",
        "user": home / ".claude" / "settings.json",
        "managed": managed,
        "managed-drop-in": drop_in / "org.json",
    }


@pytest.fixture
def agents_dir(tmp_path: Path) -> Path:
    """A throwaway user agents directory, so no test reads the real one."""
    path = tmp_path / "agents"
    path.mkdir()
    return path


@pytest.fixture
def db(tmp_path: Path) -> Path:
    """A throwaway ledger, so no test writes to the real events.db."""
    return tmp_path / "ledger" / "events.db"


@pytest.fixture(autouse=True)
def child_env(home: Path, monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Make the launcher's own environment clean, since the child inherits it.

    Autouse: `launch_job` sweeps and spawns under `os.environ`, so a machine
    that happens to export a billing variable — or an effort level — must not
    decide what these tests measure. `HOME` moves to the throwaway home for the
    same reason the roster resolves it from the environment.
    """
    monkeypatch.setenv("HOME", str(home))
    for var in (*launcher.BILLING_ENV_VARS, launcher.EFFORT_LEVEL_VAR):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.fixture
def launch(
    worktree: Path, agents_dir: Path, db: Path
) -> Callable[..., launcher.JobOutcome]:
    """Launch the `build` node through the seams, naming only what a test varies."""

    def run(**seams: Any) -> launcher.JobOutcome:
        return launcher.launch_job(
            REPO,
            ISSUE,
            seams.pop("node", NODE),
            seams.pop("worktree", worktree),
            PROMPT,
            SCHEMA,
            LAUNCH_PAYLOAD,
            db_path=db,
            agents_dir=agents_dir,
            claude_cmd=seams.pop("claude_cmd", (sys.executable,)),
            **seams,
        )

    return run


@pytest.fixture
def fake_claude(tmp_path: Path) -> Callable[..., tuple[str, ...]]:
    """Write the stand-in claude for one test and return the command that runs it."""
    here = tmp_path / "fake"
    here.mkdir()
    script = here / "claude.py"
    script.write_text(FAKE_CLAUDE)

    def plan(
        lines: list[dict[str, Any] | str],
        *,
        linger: float = 0.0,
        exit_code: int = 0,
        ignore_sigterm: bool = False,
        undecodable: bool = False,
        orphan_seconds: float = 0.0,
    ) -> tuple[str, ...]:
        (here / "plan.json").write_text(
            json.dumps(
                {
                    "lines": lines,
                    "linger": linger,
                    "exit_code": exit_code,
                    "ignore_sigterm": ignore_sigterm,
                    "undecodable": undecodable,
                    "orphan_seconds": orphan_seconds,
                }
            )
        )
        return (sys.executable, str(script))

    return plan


@pytest.fixture
def trapped_sigterm() -> Iterator[list[int]]:
    """Catch SIGTERM for one test, recording each delivery, and restore after.

    A test that signals itself needs somewhere for the signal to land: the
    default action would kill the run. The record is what a test reads to see
    whether the Python-level handler ran, which is the whole question when a
    write is meant to be holding the signal off.
    """
    fired: list[int] = []
    previous = signal.signal(signal.SIGTERM, lambda number, frame: fired.append(number))
    try:
        yield fired
    finally:
        signal.signal(signal.SIGTERM, previous)


@pytest.fixture
def spawn_record(tmp_path: Path) -> Callable[[], dict[str, Any]]:
    """Read back the argv and placement the fake claude was spawned with."""

    def read() -> dict[str, Any]:
        record: dict[str, Any] = json.loads(
            (tmp_path / "fake" / "record.json").read_text()
        )
        return record

    return read


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


def write_settings(path: Path, settings: dict[str, object]) -> None:
    """Write one settings file, creating the scope directory it sits in."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings))


def wait_until_stopped(pid: int, budget: float) -> bool:
    """Poll until `pid` is gone or a zombie, within `budget` seconds."""
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        if process_state(pid) in (None, "Z"):
            return True
        time.sleep(PDEATHSIG_POLL)
    return False


def wait_for_file(path: Path, budget: float) -> bool:
    """Poll until `path` exists, within `budget` seconds."""
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(PDEATHSIG_POLL)
    return False


def test_preflight_aborts_on_a_billing_variable_in_the_child_environment(
    worktree: Path, env: dict[str, str]
) -> None:
    env["ANTHROPIC_API_KEY"] = "sk-metered"

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert "ANTHROPIC_API_KEY" in str(aborted.value)


@pytest.mark.parametrize("scope", SETTINGS_SCOPES)
def test_preflight_aborts_on_a_billing_settings_key_in_any_roster_file(
    scope: str, roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    write_settings(roster[scope], {"apiKeyHelper": "/usr/local/bin/mint-key"})

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert "apiKeyHelper" in str(aborted.value)
    assert str(roster[scope]) in str(aborted.value)


def test_preflight_aborts_on_a_billing_variable_in_a_roster_files_env_block(
    roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    write_settings(roster["user"], {"env": {"ANTHROPIC_BASE_URL": "https://proxy"}})

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert "ANTHROPIC_BASE_URL" in str(aborted.value)
    assert str(roster["user"]) in str(aborted.value)


def test_preflight_aborts_on_a_roster_file_that_will_not_parse(
    roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    unparseable = roster["worktree-local"]
    unparseable.parent.mkdir(parents=True, exist_ok=True)
    unparseable.write_text('{"env": {,}')

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert str(unparseable) in str(aborted.value)


def test_preflight_aborts_on_a_roster_file_that_exists_but_cannot_be_read(
    roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    unreadable = roster["worktree-local"]
    unreadable.mkdir(parents=True)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert str(unreadable) in str(aborted.value)


def test_preflight_faults_a_billing_variable_that_is_set_but_empty(
    worktree: Path, env: dict[str, str]
) -> None:
    env["ANTHROPIC_API_KEY"] = ""

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert "ANTHROPIC_API_KEY" in str(aborted.value)


def test_preflight_faults_a_billing_name_present_but_empty_in_a_roster_file(
    roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    write_settings(
        roster["user"], {"apiKeyHelper": "", "env": {"ANTHROPIC_BASE_URL": ""}}
    )

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert len(aborted.value.findings) == 2


def test_preflight_passes_a_clean_environment_with_no_roster_file_present(
    worktree: Path, env: dict[str, str]
) -> None:
    launcher.preflight(worktree, env)


def test_preflight_never_faults_the_subscription_oauth_token(
    worktree: Path, env: dict[str, str]
) -> None:
    env["CLAUDE_CODE_OAUTH_TOKEN"] = "sk-ant-oat-subscription"

    launcher.preflight(worktree, env)


def test_preflight_reports_every_finding_in_one_abort(
    roster: dict[str, Path], worktree: Path, env: dict[str, str]
) -> None:
    env["ANTHROPIC_API_KEY"] = "sk-metered"
    write_settings(roster["managed"], {"awsAuthRefresh": "aws sso login"})

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launcher.preflight(worktree, env)

    assert len(aborted.value.findings) == 2


def test_launch_aborts_when_the_claude_binary_does_not_resolve(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch(claude_cmd=("claude-that-is-not-installed",))

    assert "claude-that-is-not-installed" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_the_launched_nodes_definition_is_missing(
    launch: Callable[..., launcher.JobOutcome], db: Path
) -> None:
    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{NODE}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_an_effort_level_is_set_in_the_child_environment(
    launch: Callable[..., launcher.JobOutcome],
    agents_dir: Path,
    db: Path,
    child_env: pytest.MonkeyPatch,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    child_env.setenv(launcher.EFFORT_LEVEL_VAR, "low")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert launcher.EFFORT_LEVEL_VAR in str(aborted.value)
    assert ledger_rows(db) == []


@pytest.mark.parametrize("node", launcher.NODES)
@pytest.mark.parametrize("tree", ["worktree", "checkout"])
def test_launch_aborts_on_a_shadow_definition_of_any_factory_node(
    node: str,
    tree: str,
    launch: Callable[..., launcher.JobOutcome],
    agents_dir: Path,
    worktree: Path,
    checkout: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    shadowed = {"worktree": worktree, "checkout": checkout}[tree]
    write_definition(shadowed / ".claude" / "agents", node, {"name": node})

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{node}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_on_a_shadow_definition_that_is_there_but_not_a_regular_file(
    launch: Callable[..., launcher.JobOutcome],
    agents_dir: Path,
    worktree: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    shadow = worktree / ".claude" / "agents" / f"{NODE}.md"
    shadow.mkdir(parents=True)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert str(shadow) in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definitions_name_is_not_its_filename_stem(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    write_definition(agents_dir, NODE, MISNAMED_DEFINITION)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert "builder" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definition_declares_no_effort(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    write_definition(agents_dir, NODE, UNTUNED_DEFINITION)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert "effort" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definitions_effort_is_outside_the_vocabulary(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    write_definition(agents_dir, NODE, OVERTUNED_DEFINITION)

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert "turbo" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definitions_frontmatter_will_not_parse(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    (agents_dir / f"{NODE}.md").write_text("---\nname: [build\n---\n\nBody.\n")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{NODE}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definition_carries_no_frontmatter_at_all(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    (agents_dir / f"{NODE}.md").write_text("Just a body, and no fence anywhere.\n")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{NODE}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definitions_frontmatter_fence_is_never_closed(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    (agents_dir / f"{NODE}.md").write_text("---\nname: build\neffort: high\n")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{NODE}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_launch_aborts_when_a_definitions_frontmatter_is_not_a_mapping(
    launch: Callable[..., launcher.JobOutcome], agents_dir: Path, db: Path
) -> None:
    (agents_dir / f"{NODE}.md").write_text("---\n- build\n- high\n---\n\nBody.\n")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch()

    assert f"{NODE}.md" in str(aborted.value)
    assert ledger_rows(db) == []


def test_a_clean_run_lands_both_ledger_rows_on_the_minted_session_id(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line(), NOISE_LINE, result_line(REPORT)])

    outcome = launch(claude_cmd=claude_cmd)

    launched, reported = ledger_rows(db)
    assert launched == ("job-launch", NODE, outcome.session_id, LAUNCH_PAYLOAD)
    assert reported == (
        "job-report",
        NODE,
        outcome.session_id,
        {
            "process_outcome": "clean",
            "task_outcome": "done",
            "structured_output": REPORT,
            "exit_code": 0,
            "subtype": "success",
            "is_error": False,
            "duration_s": 5.432,
            "num_turns": 3,
            "usage": {"input_tokens": 100, "output_tokens": 20},
            "permission_denials": [],
        },
    )


def test_a_clean_run_returns_the_reports_own_outcome_as_the_task_outcome(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line(), result_line(REPORT)])

    outcome = launch(claude_cmd=claude_cmd)

    assert outcome.process_outcome == "clean"
    assert outcome.task_outcome == "done"
    assert outcome.structured_output == REPORT


def test_the_spawn_carries_the_fixed_flag_roster_and_nothing_else(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    spawn_record: Callable[[], dict[str, Any]],
    agents_dir: Path,
    worktree: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line(), result_line(REPORT)])

    outcome = launch(claude_cmd=claude_cmd)

    record = spawn_record()
    assert record["argv"] == [
        "--agent",
        NODE,
        "-p",
        PROMPT,
        "--output-format",
        "stream-json",
        "--verbose",
        "--session-id",
        outcome.session_id,
        "--json-schema",
        json.dumps(SCHEMA),
        "--permission-mode",
        "bypassPermissions",
    ]
    assert Path(record["cwd"]).resolve() == worktree.resolve()


def test_a_run_whose_node_returned_no_report_is_schema_refused(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line(), result_line(None)])

    outcome = launch(claude_cmd=claude_cmd)

    assert outcome.process_outcome == "schema-refused"
    assert outcome.task_outcome is None
    assert outcome.structured_output is None
    assert ledger_rows(db)[1].payload["process_outcome"] == "schema-refused"


def test_a_child_that_exits_nonzero_on_its_own_died(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE], exit_code=3)

    outcome = launch(claude_cmd=claude_cmd)

    assert outcome.process_outcome == "died"
    assert outcome.task_outcome is None
    assert "kill" not in ledger_rows(db)[1].payload


def test_a_died_run_records_the_exit_code_that_is_its_only_diagnostic(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE], exit_code=3)

    launch(claude_cmd=claude_cmd)

    assert ledger_rows(db)[1].payload["exit_code"] == 3


def test_a_child_still_running_at_the_deadline_is_timed_out(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line()], linger=LINGER_SECONDS)

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "timed-out"
    assert outcome.task_outcome is None
    assert ledger_rows(db)[1].payload["kill"] == "sigterm"


def test_a_grandchild_holding_stdout_never_makes_a_finished_run_look_timed_out(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(), result_line(REPORT)], orphan_seconds=ORPHAN_SECONDS
    )

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=ORPHANED_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "clean"
    assert outcome.task_outcome == "done"
    assert "kill" not in ledger_rows(db)[1].payload


def test_a_run_placed_outside_its_worktree_is_killed_and_misconfigured(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    worktree: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(cwd="/somewhere/else")], linger=LINGER_SECONDS
    )

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "misconfigured"
    assert outcome.task_outcome is None
    payload = ledger_rows(db)[1].payload
    assert payload["kill"] == "sigterm"
    assert payload["alarm"] == {
        "field": "cwd",
        "observed": "/somewhere/else",
        "expected": str(worktree.resolve()),
    }


def test_a_run_billed_to_anything_but_the_subscription_is_killed_and_misconfigured(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(api_key_source="ANTHROPIC_API_KEY")],
        linger=LINGER_SECONDS,
    )

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "misconfigured"
    assert ledger_rows(db)[1].payload["alarm"] == {
        "field": "apiKeySource",
        "observed": "ANTHROPIC_API_KEY",
        "expected": "none",
    }


def test_a_later_init_never_clears_an_alarm_already_standing(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(api_key_source="ANTHROPIC_API_KEY"), init_line()],
        linger=LINGER_SECONDS,
    )

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "misconfigured"
    assert ledger_rows(db)[1].payload["alarm"]["field"] == "apiKeySource"


def test_launch_runs_the_same_preflight_the_traverse_calls_standalone(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
    child_env: pytest.MonkeyPatch,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line(), result_line(REPORT)])
    child_env.setenv("ANTHROPIC_API_KEY", "sk-metered")

    with pytest.raises(launcher.LaunchAborted) as aborted:
        launch(claude_cmd=claude_cmd)

    assert "ANTHROPIC_API_KEY" in str(aborted.value)
    assert ledger_rows(db) == []


def test_a_child_that_ignores_sigterm_is_killed_after_the_grace(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line()], linger=LINGER_SECONDS, ignore_sigterm=True
    )

    outcome = launch(
        claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE
    )

    assert outcome.process_outcome == "timed-out"
    assert ledger_rows(db)[1].payload["kill"] == "sigkill"


def test_a_stream_is_read_as_utf8_whatever_the_machines_locale_prefers(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    monkeypatch.setattr(locale, "getencoding", lambda: "ascii")
    claude_cmd = fake_claude(
        [
            HOOK_LINE,
            init_line(),
            json.dumps(result_line(NON_ASCII_REPORT), ensure_ascii=False),
        ]
    )

    outcome = launch(claude_cmd=claude_cmd)

    assert outcome.structured_output == NON_ASCII_REPORT


def test_a_stream_the_decoder_rejects_leaves_as_the_failure_it_was(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(), result_line(REPORT)], undecodable=True
    )

    with pytest.raises(UnicodeDecodeError):
        launch(claude_cmd=claude_cmd, timeout_s=BRIEF_DEADLINE, grace_s=BRIEF_GRACE)


def test_a_result_envelope_with_no_init_before_it_violates_the_contract(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, result_line(REPORT)])

    with pytest.raises(launcher.HarnessContractViolation):
        launch(claude_cmd=claude_cmd)

    assert [row.kind for row in ledger_rows(db)] == ["job-launch"]


def test_a_dropped_stream_line_with_no_init_ever_read_violates_the_contract(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, TRUNCATED_INIT], exit_code=1)

    with pytest.raises(launcher.HarnessContractViolation):
        launch(claude_cmd=claude_cmd)

    assert [row.kind for row in ledger_rows(db)] == ["job-launch"]


def test_a_dropped_stream_line_after_a_readable_init_is_classified_as_usual(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(), TRUNCATED_INIT, result_line(REPORT)]
    )

    outcome = launch(claude_cmd=claude_cmd)

    assert outcome.process_outcome == "clean"


def test_a_validated_report_with_no_outcome_violates_the_contract(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(), result_line({"gist": "The issue is built."})]
    )

    with pytest.raises(launcher.HarnessContractViolation) as violated:
        launch(claude_cmd=claude_cmd)

    assert "outcome" in str(violated.value)
    assert [row.kind for row in ledger_rows(db)] == ["job-launch"]


def test_a_duration_the_harness_reports_as_a_string_violates_the_contract(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    envelope = {**result_line(REPORT), "duration_ms": "5432"}
    claude_cmd = fake_claude([HOOK_LINE, init_line(), envelope])

    with pytest.raises(launcher.HarnessContractViolation) as violated:
        launch(claude_cmd=claude_cmd)

    assert "duration_ms" in str(violated.value)


def test_a_child_dies_with_a_launcher_that_is_destroyed_without_warning(
    tmp_path: Path,
    worktree: Path,
    agents_dir: Path,
    db: Path,
    managed_settings: tuple[Path, Path],
    fake_claude: Callable[..., tuple[str, ...]],
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE, init_line()], linger=LINGER_SECONDS)
    managed, drop_in = managed_settings
    arguments = tmp_path / "launch.json"
    arguments.write_text(
        json.dumps(
            {
                "src": str(Path(launcher.__file__).parents[2]),
                "managed_settings": str(managed),
                "managed_settings_dir": str(drop_in),
                "repo": REPO,
                "issue": ISSUE,
                "node": NODE,
                "worktree": str(worktree),
                "prompt": PROMPT,
                "schema": SCHEMA,
                "launch_payload": LAUNCH_PAYLOAD,
                "db_path": str(db),
                "agents_dir": str(agents_dir),
                "claude_cmd": list(claude_cmd),
                "timeout_s": LINGER_SECONDS,
            }
        )
    )
    runner = tmp_path / "runner.py"
    runner.write_text(LAUNCH_RUNNER)
    launching = subprocess.Popen([sys.executable, str(runner), str(arguments)])
    record = tmp_path / "fake" / "record.json"
    assert wait_for_file(record, PDEATHSIG_BUDGET)
    child = json.loads(record.read_text())["pid"]

    launching.kill()
    launching.wait(timeout=PDEATHSIG_BUDGET)

    assert wait_until_stopped(child, PDEATHSIG_BUDGET)


def test_the_pump_thread_never_takes_a_signal_a_ledger_write_is_holding_off(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
    trapped_sigterm: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A signal any thread can take is a signal that lands inside the write.

    CPython runs the C-level handler on whichever thread the kernel picks, and
    the main thread then runs the Python handler at its next bytecode boundary
    whatever its own mask says. So a blocked main thread is not enough: one
    unblocked thread anywhere in the process puts the traverse's trap back
    inside the transaction it was blocked out of, where its own INSERT queues
    behind a write lock only the suspended frame can release.

    The grandchild here is what keeps the pump thread alive past the run it
    belongs to -- the same case `_die_with_parent` names, where the traverse
    launches its second node while the first launch's pump still holds the pipe.
    """
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude(
        [HOOK_LINE, init_line(), result_line(REPORT)], orphan_seconds=ORPHAN_SECONDS
    )
    launch(claude_cmd=claude_cmd, timeout_s=ORPHANED_DEADLINE, grace_s=BRIEF_GRACE)
    inside: list[list[int]] = []
    opening: Callable[..., sqlite3.Connection] = sqlite3.connect

    def watched(*arguments: Any, **keywords: Any) -> sqlite3.Connection:
        os.kill(os.getpid(), signal.SIGTERM)
        time.sleep(SIGNAL_SETTLE)
        inside.append(list(trapped_sigterm))
        return opening(*arguments, **keywords)

    monkeypatch.setattr(sqlite3, "connect", watched)

    ledger.traverse_end(REPO, ISSUE, {"status": "killed"}, db_path=db)
    time.sleep(SIGNAL_SETTLE)

    assert inside == [[]]
    assert trapped_sigterm == [signal.SIGTERM]


def test_importing_the_launcher_off_linux_names_the_platform_not_a_missing_symbol(
    tmp_path: Path,
) -> None:
    """`prctl` is Linux's, and the binding that reaches it happens at import.

    Left unguarded, a contributor on macOS gets `AttributeError: undefined
    symbol: prctl` at collection for all three factory suites and from
    `scripts/traverse-issue` before it can print its own usage — none of which
    names the requirement it is failing.

    The import runs in its own interpreter because that is the only place the
    platform can be another one: reloading the module here would rebind every
    class in it and leave the rest of the suite importing a different module
    than it started with.
    """
    probe = tmp_path / "probe.py"
    probe.write_text(PLATFORM_PROBE)

    refused = subprocess.run(
        [sys.executable, str(probe), str(Path(launcher.__file__).parents[2])],
        capture_output=True,
        text=True,
    )

    assert refused.stdout.splitlines()[0] == "LauncherError"
    assert "darwin" in refused.stdout
    assert "linux" in refused.stdout


def test_the_death_signal_syscall_is_resolved_before_any_child_is_forked() -> None:
    """The lookup between fork and exec is the deadlock this rules out.

    `CDLL.__getattr__` runs `dlsym` on the first attribute access and caches the
    result on the instance, so a cached entry with no launch yet in this process
    is the proof the lookup happened at import — and a resolution that happened
    at import cannot happen in the child, where taking the loader's lock could
    wedge it forever.
    """
    assert "prctl" in launcher.LIBC.__dict__
