"""Behavioral tests for the git-authority hook and the push permission rows.

Two artifacts, two seams. The hook is exercised as the harness exercises it — a
subprocess fed one PreToolUse event on stdin — so what is asserted is the
verdict a real session would get. The permission rows are asserted verbatim
against base.json, because pytest cannot invoke Claude Code's pattern engine and
a row that quietly changes spelling stops binding without any test noticing.

Scope is deliberately narrow: this guards the hook and the rows, nothing else.
The routine spellings below are a copy of what the skills prescribe; drift
between skill prose and these fixtures is not tested by ruling, and surfaces
operationally instead.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "dotfiles" / "dot-claude" / "hooks" / "git-authority"
BASE_SETTINGS = REPO_ROOT / "dotfiles" / "settings" / "base.json"

# The routine spellings, exactly as the factory's skills issue them. These must
# draw no opinion at all: they fall through the hook to the allowlist.
ROUTINE = [
    "git push -u origin issue-342",
    "git push origin issue-342",
    "git push --no-verify -u origin issue-342",
    "git push --no-verify origin issue-342",
    "git -C ~/workspace/dev-playbook/.claude/worktrees/issue-342 push origin issue-342",
    "git fetch --prune origin",
    "git pull --ff-only origin main",
]


def decision(command: str, tool_name: str = "Bash") -> str | None:
    """The hook's permission decision for one command, or None when it has none.

    None is the no-opinion verdict: the hook printed nothing, so the harness
    falls through to the permission rules.
    """
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": command},
    }
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    payload = json.loads(result.stdout)
    output = payload["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    return str(output["permissionDecision"])


# --- routine spellings draw no opinion --------------------------------------


@pytest.mark.parametrize("command", ROUTINE)
def test_routine_spelling_draws_no_opinion(command: str) -> None:
    assert decision(command) is None


# --- forbidden spellings are denied -----------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin",
        "git push --no-verify",
        "git -C ~/workspace/mission-control push",
    ],
)
def test_push_without_an_explicit_remote_and_ref_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push origin main",
        "git push -u origin main",
        "git push origin HEAD:main",
        "git push origin issue-342:main",
        "git push origin HEAD:refs/heads/main",
        "git push origin issue-342 main",
        "git -C ~/workspace/dev-playbook push origin main",
    ],
)
def test_main_targeting_push_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push --force origin issue-342",
        "git push origin issue-342 --force",
        "git push -f origin issue-342",
        "git push -fu origin issue-342",
        "git push --force-with-lease origin issue-342",
        "git push --force-with-lease=issue-342 origin issue-342",
        "git push --force-if-includes origin issue-342",
        "git push origin +issue-342",
        "git push origin +HEAD:issue-342",
    ],
)
def test_forced_push_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push --delete origin issue-342",
        "git push origin --delete issue-342",
        "git push -d origin issue-342",
        "git push origin :issue-342",
        "git push origin :refs/heads/issue-342",
    ],
)
def test_remote_deleting_push_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        'bash -c "git push origin issue-342"',
        "sh -c 'git push --force origin issue-342'",
        'eval "git push origin issue-342"',
        "echo $(git push origin issue-342)",
        "timeout 5 git push origin issue-342",
        "git push origin ${BRANCH}",
        'git push origin "issue-342',
    ],
)
def test_push_the_hook_cannot_read_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push origin HEAD",
        "git push origin @",
        "git push -u origin HEAD",
        "git push origin issue-342:HEAD",
        "git -C ~/workspace/mission-control push origin HEAD",
    ],
)
def test_push_to_a_symbolic_destination_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push origin $TARGET",
        'git push -u origin "$branch"',
        "git push $REMOTE issue-342",
        "git push origin $(git branch --show-current)",
    ],
)
def test_push_to_a_target_the_hook_cannot_expand_is_denied(command: str) -> None:
    assert decision(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "cd /tmp && git push origin main",
        "git status; git push --force origin issue-342",
        "git log | head && git push origin :issue-342",
        "git log --format='%h | %s' && git push origin main:main",
        "echo don't && git push origin issue-342:main",
    ],
)
def test_a_forbidden_push_is_found_in_any_segment(command: str) -> None:
    assert decision(command) == "deny"


# --- what the hook stays out of ---------------------------------------------


def test_a_chained_routine_push_still_draws_no_opinion() -> None:
    assert decision("git add -A && git push -u origin issue-342") is None


def test_a_commit_mentioning_push_draws_no_opinion() -> None:
    assert decision('git commit -m "push authority" && git status') is None


@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "gh pr list --jq '.[] | .number'",
        "rg 'push|pull' -n",
        "grep -n 'push|pull' file",
        "sed -n '1,5p;10p' file",
        'echo "a && b"',
        "git log --format='%h | %s'",
        'gh pr comment 345 --body "covers A & B"',
        'gh pr comment 345 --body "the push & the pull"',
        'git commit -m "push authority; landed"',
        "echo don't && ls",
        'echo "the cost is $(date)"',
    ],
)
def test_a_command_that_pushes_nothing_draws_no_opinion(command: str) -> None:
    assert decision(command) is None


def test_a_tool_other_than_bash_draws_no_opinion() -> None:
    assert decision("git push origin main", tool_name="Edit") is None


# --- the permission rows ----------------------------------------------------
#
# Asserted character-for-character, because pytest cannot invoke Claude Code's
# pattern engine: a row that changes spelling stops binding silently, and only
# a verbatim comparison catches that.
#
# The pairing every family shows — a `... X` row beside each `... X *` row, and
# a `git -C * push ...` row beside each `git push ...` row — is not decoration.
# Both come from measured behavior of the engine, recorded in
# software-factory/git-authority.md: a trailing ` *` needs a following space, so
# it cannot match the end of a command, and nothing normalizes `git -C <path>
# push` into `git push`.

DENY_ROWS = [
    "Bash(git push)",
    "Bash(git push * main)",
    "Bash(git push * main *)",
    "Bash(git push * HEAD:main)",
    "Bash(git push * HEAD:main *)",
    "Bash(git push --force)",
    "Bash(git push --force *)",
    "Bash(git push * --force)",
    "Bash(git push * --force *)",
    "Bash(git push -f)",
    "Bash(git push -f *)",
    "Bash(git push * -f)",
    "Bash(git push * -f *)",
    "Bash(git push --force-with-lease)",
    "Bash(git push --force-with-lease *)",
    "Bash(git push * --force-with-lease)",
    "Bash(git push * --force-with-lease *)",
    "Bash(git push --delete)",
    "Bash(git push --delete *)",
    "Bash(git push * --delete)",
    "Bash(git push * --delete *)",
    "Bash(git push -d)",
    "Bash(git push -d *)",
    "Bash(git push * -d)",
    "Bash(git push * -d *)",
    "Bash(git -C * push)",
    "Bash(git -C * push * main)",
    "Bash(git -C * push * main *)",
    "Bash(git -C * push * HEAD:main)",
    "Bash(git -C * push * HEAD:main *)",
    "Bash(git -C * push --force)",
    "Bash(git -C * push --force *)",
    "Bash(git -C * push * --force)",
    "Bash(git -C * push * --force *)",
    "Bash(git -C * push -f)",
    "Bash(git -C * push -f *)",
    "Bash(git -C * push * -f)",
    "Bash(git -C * push * -f *)",
    "Bash(git -C * push --force-with-lease)",
    "Bash(git -C * push --force-with-lease *)",
    "Bash(git -C * push * --force-with-lease)",
    "Bash(git -C * push * --force-with-lease *)",
    "Bash(git -C * push --delete)",
    "Bash(git -C * push --delete *)",
    "Bash(git -C * push * --delete)",
    "Bash(git -C * push * --delete *)",
    "Bash(git -C * push -d)",
    "Bash(git -C * push -d *)",
    "Bash(git -C * push * -d)",
    "Bash(git -C * push * -d *)",
]

ALLOW_ROWS = [
    "Bash(git push origin *)",
    "Bash(git push -u origin *)",
    "Bash(git push --no-verify -u origin *)",
    "Bash(git push --no-verify origin *)",
    "Bash(git -C * push origin *)",
    "Bash(git -C * push -u origin *)",
    "Bash(git -C * push --no-verify -u origin *)",
    "Bash(git -C * push --no-verify origin *)",
    "Bash(git fetch)",
    "Bash(git fetch *)",
    "Bash(git -C * fetch)",
    "Bash(git -C * fetch *)",
    "Bash(git pull --ff-only origin main)",
    "Bash(git -C * pull --ff-only origin main)",
]


def base_settings() -> dict:
    """The machine-agnostic settings layer, parsed."""
    return dict(json.loads(BASE_SETTINGS.read_text(encoding="utf-8")))


@pytest.mark.parametrize("row", DENY_ROWS)
def test_deny_row_is_present_verbatim(row: str) -> None:
    assert row in base_settings()["permissions"]["deny"]


@pytest.mark.parametrize("row", ALLOW_ROWS)
def test_allow_row_is_present_verbatim(row: str) -> None:
    assert row in base_settings()["permissions"]["allow"]


def test_the_hook_is_wired_as_a_pretooluse_bash_hook() -> None:
    entries = base_settings()["hooks"]["PreToolUse"]

    commands = [
        hook["command"]
        for entry in entries
        if entry["matcher"] == "Bash"
        for hook in entry["hooks"]
    ]

    assert 'python3 "$HOME/.claude/hooks/git-authority"' in commands
