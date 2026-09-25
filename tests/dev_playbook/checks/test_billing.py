"""Unit tests for the billing family's checks.

The checks read the machine, so every test points ``HOME`` at a directory
under ``tmp_path`` and clears the billing variables from the environment;
the repo is a model rooted at another directory under ``tmp_path``.
"""

from collections.abc import Iterable
from pathlib import Path

import pytest

from dev_playbook.check_registry import Finding
from dev_playbook.checks import billing
from dev_playbook.checks.billing import (
    CannotRead,
    no_credential_in_a_claude_settings_file,
    no_metered_variable_in_a_shell_startup_file,
    no_metered_variable_in_the_environment,
)
from dev_playbook.model import Repo


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty home directory, named by ``HOME``, in a clean environment."""
    made = tmp_path / "home"
    (made / ".claude").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(made))
    for name in billing.BILLING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    return made


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    """A repo model whose root holds no .claude/ directory."""
    root = tmp_path / "repo"
    root.mkdir()
    return Repo.from_files(root, {})


def write(path: Path, text: str) -> None:
    """Write text to path, creating the directories above it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def found(findings: Iterable[Finding]) -> list[tuple[str, int | None]]:
    """Each finding as (path, line)."""
    return [(f.path, f.line) for f in findings]


def test_no_metered_variable_in_the_environment(
    home: Path, repo: Repo, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-x")
    monkeypatch.setenv("CLAUDE_CODE_USE_BEDROCK", "0")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "subscription")
    findings = list(no_metered_variable_in_the_environment(repo))
    assert [f.message.split()[0] for f in findings] == [
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_USE_BEDROCK",
    ]
    assert {f.path for f in findings} == {"environment"}


@pytest.mark.parametrize("name", billing.BILLING_ENV_VARS)
def test_every_listed_variable_is_caught(name: str) -> None:
    """Guards against a name being listed but misspelled."""
    assert billing.metered_env_vars({name: "x"}) == [name]


def test_no_metered_variable_in_a_shell_startup_file(home: Path, repo: Repo) -> None:
    write(
        home / ".bashrc", "export PATH=$PATH:/usr/local/bin\nunset ANTHROPIC_API_KEY\n"
    )
    write(home / ".profile", 'echo "$ANTHROPIC_API_KEY"\n# ANTHROPIC_API_KEY=sk-old\n')
    write(home / ".zshrc", "# a comment\n\nexport ANTHROPIC_AUTH_TOKEN=t\n")
    write(home / ".bashrc.d" / "10-cloud.sh", "CLAUDE_CODE_USE_VERTEX=1\n")
    assert found(no_metered_variable_in_a_shell_startup_file(repo)) == [
        ("~/.zshrc", 3),
        ("~/.bashrc.d/10-cloud.sh", 1),
    ]


def test_assignments_in_finds_every_name_on_a_line() -> None:
    text = "ANTHROPIC_API_KEY=a ANTHROPIC_BASE_URL=b\n"
    assert billing.assignments_in(text) == [
        (1, "ANTHROPIC_API_KEY"),
        (1, "ANTHROPIC_BASE_URL"),
    ]


def test_no_credential_in_a_claude_settings_file(home: Path, repo: Repo) -> None:
    write(
        home / ".claude" / "settings.json",
        '{"model": "opus", "env": {"CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"}}',
    )
    write(
        home / ".claude" / "settings.local.json", '{"env": {"ANTHROPIC_API_KEY": "sk"}}'
    )
    write(repo.root / ".claude" / "settings.json", '{"apiKeyHelper": "/bin/mint"}')
    write(repo.root / ".claude" / "settings.local.json", '{"awsAuthRefresh": "x"}')
    assert found(no_credential_in_a_claude_settings_file(repo)) == [
        ("~/.claude/settings.local.json", None),
        (".claude/settings.json", None),
        (".claude/settings.local.json", None),
    ]


@pytest.mark.parametrize("key", billing.CREDENTIAL_SETTINGS_KEYS)
def test_every_credential_key_is_caught(key: str, home: Path, repo: Repo) -> None:
    write(home / ".claude" / "settings.json", f'{{"{key}": "x"}}')
    assert found(no_credential_in_a_claude_settings_file(repo)) == [
        ("~/.claude/settings.json", None)
    ]


@pytest.mark.parametrize("text", ["{not json", "[]", '{"env": ["ANTHROPIC_API_KEY"]}'])
def test_unreadable_settings_file_raises(text: str, home: Path, repo: Repo) -> None:
    write(home / ".claude" / "settings.json", text)
    with pytest.raises(CannotRead):
        list(no_credential_in_a_claude_settings_file(repo))


def test_absent_home_raises(repo: Repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HOME")
    with pytest.raises(CannotRead):
        list(no_metered_variable_in_a_shell_startup_file(repo))


def test_home_naming_no_directory_raises(
    tmp_path: Path, repo: Repo, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "absent"))
    with pytest.raises(CannotRead):
        list(no_credential_in_a_claude_settings_file(repo))
