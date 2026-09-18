"""Behavioral tests for scripts/billing-lint.

billing-lint reads four surfaces for a credential that would meter Claude
billing: the live environment, the shell startup files, the machine's Claude
settings, and the repo's own. Its logic is pure over a home directory and a
repo root, so the tests build both under tmp_path and call the module rather
than the shim; the two end-to-end tests run the shim the way pre-commit does.

A run that cannot read a surface is a tool error rather than a pass. That is
the case the detector exists for, so it has tests of its own here.
"""

import subprocess
from pathlib import Path

import pytest

from dev_playbook import billing_lint

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "billing-lint"


@pytest.fixture
def home(tmp_path: Path) -> Path:
    """An empty home directory carrying no configuration at all."""
    made = tmp_path / "home"
    (made / ".claude").mkdir(parents=True)
    return made


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """An empty repo root carrying no .claude/ directory."""
    made = tmp_path / "repo"
    made.mkdir()
    return made


def write(path: Path, text: str) -> None:
    """Write text to path, creating the directories above it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rules(findings: list[billing_lint.Finding]) -> list[str]:
    """The rule ids of findings, in order."""
    return [finding.rule for finding in findings]


# --- no-metered-env rule ---


def test_ordinary_environment_is_clean() -> None:
    assert billing_lint.metered_env_vars({"HOME": "/home/geoff"}) == []


def test_api_key_is_caught() -> None:
    found = billing_lint.metered_env_vars({"ANTHROPIC_API_KEY": "sk-whatever"})
    assert found == ["ANTHROPIC_API_KEY"]


def test_oauth_token_is_allowed() -> None:
    """It is a subscription credential, so it must not be refused."""
    assert billing_lint.metered_env_vars({"CLAUDE_CODE_OAUTH_TOKEN": "x"}) == []


def test_empty_value_counts_as_unset() -> None:
    assert billing_lint.metered_env_vars({"ANTHROPIC_API_KEY": ""}) == []


def test_disabled_looking_flag_still_counts_as_set() -> None:
    assert billing_lint.metered_env_vars({"CLAUDE_CODE_USE_BEDROCK": "0"}) == [
        "CLAUDE_CODE_USE_BEDROCK"
    ]


@pytest.mark.parametrize("name", billing_lint.BILLING_ENV_VARS)
def test_every_listed_variable_is_caught(name: str) -> None:
    """Guards against a name being listed but misspelled."""
    assert billing_lint.metered_env_vars({name: "x"}) == [name]


def test_environment_finding_names_the_environment() -> None:
    findings = billing_lint.check_env({"ANTHROPIC_API_KEY": "sk-x"})
    assert [finding.file for finding in findings] == ["environment"]
    assert rules(findings) == [billing_lint.NO_METERED_ENV]


# --- no-metered-shell-config rule ---


def test_clean_shell_file_yields_nothing(home: Path) -> None:
    write(home / ".bashrc", "export PATH=$PATH:/usr/local/bin\n")
    assert billing_lint.check_shell_config(home) == []


def test_exported_assignment_is_caught(home: Path) -> None:
    write(home / ".bashrc", "export ANTHROPIC_BASE_URL=https://elsewhere\n")
    findings = billing_lint.check_shell_config(home)
    assert rules(findings) == [billing_lint.NO_METERED_SHELL_CONFIG]
    assert findings[0].line == 1


def test_commented_assignment_is_not_a_finding(home: Path) -> None:
    write(home / ".bashrc", "# ANTHROPIC_API_KEY=sk-old, removed 2026-01-01\n")
    assert billing_lint.check_shell_config(home) == []


def test_unset_is_not_an_assignment(home: Path) -> None:
    write(home / ".bashrc", "unset ANTHROPIC_API_KEY\n")
    assert billing_lint.check_shell_config(home) == []


def test_reference_to_the_variable_is_not_an_assignment(home: Path) -> None:
    write(home / ".bashrc", 'echo "$ANTHROPIC_API_KEY"\n')
    assert billing_lint.check_shell_config(home) == []


def test_bashrc_loader_directory_is_read(home: Path) -> None:
    """The dotfiles loader sources every file in it, so every file is read."""
    write(home / ".bashrc.d" / "10-cloud.sh", "CLAUDE_CODE_USE_VERTEX=1\n")
    findings = billing_lint.check_shell_config(home)
    assert rules(findings) == [billing_lint.NO_METERED_SHELL_CONFIG]


def test_assignment_reports_its_line(home: Path) -> None:
    write(home / ".zshrc", "# a comment\n\nANTHROPIC_AUTH_TOKEN=t\n")
    findings = billing_lint.check_shell_config(home)
    assert findings[0].line == 3


def test_assignments_in_finds_every_name_on_a_line() -> None:
    text = "ANTHROPIC_API_KEY=a ANTHROPIC_BASE_URL=b\n"
    assert billing_lint.assignments_in(text) == [
        (1, "ANTHROPIC_API_KEY"),
        (1, "ANTHROPIC_BASE_URL"),
    ]


# --- no-credential-settings rule ---


def test_ordinary_settings_are_clean(home: Path, repo: Path) -> None:
    write(home / ".claude" / "settings.json", '{"model": "opus"}')
    assert billing_lint.check_settings(home, repo) == []


@pytest.mark.parametrize("key", billing_lint.CREDENTIAL_SETTINGS_KEYS)
def test_every_credential_key_is_caught(key: str, home: Path, repo: Path) -> None:
    write(home / ".claude" / "settings.json", f'{{"{key}": "x"}}')
    findings = billing_lint.check_settings(home, repo)
    assert rules(findings) == [billing_lint.NO_CREDENTIAL_SETTINGS]


def test_env_block_carrying_a_billing_variable_is_caught(
    home: Path, repo: Path
) -> None:
    write(home / ".claude" / "settings.json", '{"env": {"ANTHROPIC_API_KEY": "sk-x"}}')
    findings = billing_lint.check_settings(home, repo)
    assert rules(findings) == [billing_lint.NO_CREDENTIAL_SETTINGS]
    assert "ANTHROPIC_API_KEY" in findings[0].message


def test_harmless_env_block_is_clean(home: Path, repo: Path) -> None:
    write(
        home / ".claude" / "settings.json",
        '{"env": {"CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"}}',
    )
    assert billing_lint.check_settings(home, repo) == []


def test_repo_settings_are_read_too(home: Path, repo: Path) -> None:
    """A clean machine must not excuse a repo that ships a credential."""
    write(repo / ".claude" / "settings.json", '{"apiKeyHelper": "/bin/mint"}')
    findings = billing_lint.check_settings(home, repo)
    assert rules(findings) == [billing_lint.NO_CREDENTIAL_SETTINGS]
    assert findings[0].file == ".claude/settings.json"


def test_local_settings_file_is_read(home: Path, repo: Path) -> None:
    write(repo / ".claude" / "settings.local.json", '{"awsAuthRefresh": "x"}')
    findings = billing_lint.check_settings(home, repo)
    assert findings[0].file == ".claude/settings.local.json"


def test_machine_settings_location_is_home_relative(home: Path, repo: Path) -> None:
    """A machine surface renders the same whichever directory HOME names."""
    write(home / ".claude" / "settings.json", '{"apiKeyHelper": "/bin/mint"}')
    findings = billing_lint.check_settings(home, repo)
    assert findings[0].file == "~/.claude/settings.json"


def test_machine_shell_location_is_home_relative(home: Path) -> None:
    write(home / ".bashrc", "ANTHROPIC_API_KEY=sk-x\n")
    findings = billing_lint.check_shell_config(home)
    assert findings[0].file == "~/.bashrc"


def test_absent_settings_file_is_clean(home: Path, repo: Path) -> None:
    assert billing_lint.check_settings(home, repo) == []


# --- a surface that cannot be read is a tool error ---


def test_unparseable_settings_file_refuses(home: Path, repo: Path) -> None:
    write(home / ".claude" / "settings.json", "{not json")
    with pytest.raises(billing_lint.CannotRun):
        billing_lint.check_settings(home, repo)


def test_settings_file_holding_a_list_refuses(home: Path, repo: Path) -> None:
    write(home / ".claude" / "settings.json", "[]")
    with pytest.raises(billing_lint.CannotRun):
        billing_lint.check_settings(home, repo)


def test_env_block_that_is_not_a_mapping_refuses() -> None:
    with pytest.raises(billing_lint.CannotRun):
        billing_lint.settings_env_vars({"env": ["ANTHROPIC_API_KEY"]})


def test_absent_home_refuses() -> None:
    with pytest.raises(billing_lint.CannotRun):
        billing_lint.home_directory({})


def test_home_naming_no_directory_refuses(tmp_path: Path) -> None:
    with pytest.raises(billing_lint.CannotRun):
        billing_lint.home_directory({"HOME": str(tmp_path / "absent")})


# --- the detector end to end ---


def test_shim_reports_clean_on_this_machine(repo: Path) -> None:
    """The machine this suite runs on carries no metered credential."""
    done = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "clean" in done.stderr


def test_shim_lists_its_rules() -> None:
    done = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), "--list-rules"],
        capture_output=True,
        text=True,
    )
    assert done.stdout.split() == sorted(billing_lint.RULES)
