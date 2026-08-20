import json
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
    """A linked worktree of ``checkout`` — the placement every launch runs in."""
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


def test_the_main_checkout_resolves_from_a_linked_worktree(
    worktree: Path, checkout: Path
) -> None:
    assert launcher.main_checkout(worktree) == checkout.resolve()


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
