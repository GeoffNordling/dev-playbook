import json
import os
import subprocess
from pathlib import Path

import pytest
from conftest import commit_all, init_repo

from dev_playbook.factory import launcher

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


def write_settings(path: Path, settings: dict[str, object]) -> None:
    """Write one settings file, creating the scope directory it sits in."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings))


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
