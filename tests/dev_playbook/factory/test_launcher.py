import json
import locale
import os
import sqlite3
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import commit_all, init_repo

from dev_playbook.factory import launcher

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
    json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd()})
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

# What the one real-spawn test needs of the machine it runs on, read at import
# before any fixture redirects them. That test alone is swept against the real
# settings and runs under the real home, because a billing key on this machine
# must abort it rather than be hidden behind a temp directory nobody configured.
REAL_HOME = os.path.expanduser("~")
REAL_MANAGED_SETTINGS = launcher.MANAGED_SETTINGS
REAL_MANAGED_SETTINGS_DIR = launcher.MANAGED_SETTINGS_DIR

# The gate on the real spawn, mirroring `SKIP_JUDGMENTS`: exactly "1" skips
# visibly, anything else -- a bare `pytest` included -- runs it.
REAL_SPAWN_GATE = "SKIP_REAL_SPAWN"

# The throwaway node the real spawn launches, and the definition it resolves
# from project scope. Haiku because what is under test is the launcher, never a
# model's judgment: the cheapest model proves the contract as well as any.
HAIKU_NODE = "haiku-probe"
HAIKU_DEFINITION: dict[str, Any] = {
    "name": HAIKU_NODE,
    "description": "A throwaway node that reports and stops.",
    "model": "haiku",
    "effort": "low",
}
HAIKU_PROMPT = "Do not use any tools. Set outcome to done and gist to the word: ok."

# Generous enough for a real round trip, short enough that a wedged run fails
# the suite rather than holding it.
REAL_SPAWN_DEADLINE = 300.0

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
def real_machine(child_env: pytest.MonkeyPatch) -> None:
    """Undo this module's hermetic redirections, for the one test that spawns claude.

    The real spawn needs the machine's own home to find the subscription
    credential it runs on, and it has to be swept against the machine's real
    settings for the sweep to mean anything at all.
    """
    child_env.setenv("HOME", REAL_HOME)
    child_env.setattr(launcher, "MANAGED_SETTINGS", REAL_MANAGED_SETTINGS)
    child_env.setattr(launcher, "MANAGED_SETTINGS_DIR", REAL_MANAGED_SETTINGS_DIR)


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


def write_definition(directory: Path, stem: str, frontmatter: dict[str, Any]) -> Path:
    """Write one agent definition, its frontmatter rendered as YAML."""
    body = "\n".join(f"{key}: {value}" for key, value in frontmatter.items())
    path = directory / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{body}\n---\n\nThe node's instructions.\n")
    return path


def ledger_rows(db: Path) -> list[tuple[str, str, dict[str, Any]]]:
    """Every ledger row in the store as (kind, session_id, payload), in write order."""
    if not db.exists():
        return []
    with sqlite3.connect(db) as connection:
        rows = connection.execute(
            "SELECT kind, session_id, payload FROM ledger ORDER BY id"
        ).fetchall()
    return [
        (kind, session_id, json.loads(payload)) for kind, session_id, payload in rows
    ]


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
    assert launched == ("job-launch", outcome.session_id, LAUNCH_PAYLOAD)
    assert reported == (
        "job-report",
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
    assert ledger_rows(db)[1][2]["process_outcome"] == "schema-refused"


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
    assert "kill" not in ledger_rows(db)[1][2]


def test_a_died_run_records_the_exit_code_that_is_its_only_diagnostic(
    launch: Callable[..., launcher.JobOutcome],
    fake_claude: Callable[..., tuple[str, ...]],
    agents_dir: Path,
    db: Path,
) -> None:
    write_definition(agents_dir, NODE, DEFINITION)
    claude_cmd = fake_claude([HOOK_LINE], exit_code=3)

    launch(claude_cmd=claude_cmd)

    assert ledger_rows(db)[1][2]["exit_code"] == 3


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
    assert ledger_rows(db)[1][2]["kill"] == "sigterm"


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
    assert "kill" not in ledger_rows(db)[1][2]


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
    payload = ledger_rows(db)[1][2]
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
    assert ledger_rows(db)[1][2]["alarm"] == {
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
    assert ledger_rows(db)[1][2]["alarm"]["field"] == "apiKeySource"


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
    assert ledger_rows(db)[1][2]["kill"] == "sigkill"


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

    assert [kind for kind, _, _ in ledger_rows(db)] == ["job-launch"]


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

    assert [kind for kind, _, _ in ledger_rows(db)] == ["job-launch"]


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
    assert [kind for kind, _, _ in ledger_rows(db)] == ["job-launch"]


@pytest.mark.skipif(
    os.environ.get(REAL_SPAWN_GATE) == "1",
    reason=f"{REAL_SPAWN_GATE}=1: this test launches actual claude",
)
def test_a_real_spawn_runs_the_whole_launcher_against_the_live_harness(
    real_machine: None, worktree: Path, db: Path
) -> None:
    definitions = worktree / ".claude" / "agents"
    write_definition(definitions, HAIKU_NODE, HAIKU_DEFINITION)

    outcome = launcher.launch_job(
        REPO,
        ISSUE,
        HAIKU_NODE,
        worktree,
        HAIKU_PROMPT,
        SCHEMA,
        LAUNCH_PAYLOAD,
        db_path=db,
        agents_dir=definitions,
        timeout_s=REAL_SPAWN_DEADLINE,
    )

    assert outcome.process_outcome == "clean"
    assert outcome.task_outcome == "done"
    assert [kind for kind, _, _ in ledger_rows(db)] == ["job-launch", "job-report"]
