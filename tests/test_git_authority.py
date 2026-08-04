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
    "git -C ~/workspace/dev-playbook/.claude/worktrees/issue-342 push --no-verify -u origin issue-342",
    "git fetch --prune origin",
    "git pull --ff-only origin main",
    "git -C ~/workspace/dev-playbook pull --ff-only origin main",
]


def hook(stdin: str) -> dict | None:
    """The hook's PreToolUse output for a raw stdin payload, or None when silent.

    None is the no-opinion verdict: the hook printed nothing, so the harness
    falls through to the permission rules. Raw text is the seam because a
    payload that will not parse is one of the verdicts under test.
    """
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    if not result.stdout.strip():
        return None
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    return dict(output)


def decision(command: str, tool_name: str = "Bash", **payload: object) -> str | None:
    """The hook's permission decision for one command, or None when it has none.

    ``payload`` adds the session fields the harness writes beside the command —
    ``agent_type`` for a subagent, ``transcript_path`` for the session's
    transcript — which is what the commit lanes are read from.
    """
    event: dict[str, object] = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": command},
    }
    event.update(payload)
    output = hook(json.dumps(event))
    return None if output is None else str(output["permissionDecision"])


# The harness-written marker a typed slash command leaves in the transcript,
# assembled from pieces here and in the hook. No authored file in this repo may
# carry it whole: a file that did could be pasted into a user turn and read as a
# grant nobody typed.
MARKER_OPEN = "<command-" + "name>"
MARKER_CLOSE = "</command-" + "name>"


def marker(command_name: str) -> str:
    """The transcript marker the harness writes when the user types the command."""
    return MARKER_OPEN + "/" + command_name + MARKER_CLOSE


def user_turn(text: str) -> dict:
    """One genuine user turn, as the harness records it — plain string content."""
    return {"type": "user", "message": {"role": "user", "content": text}}


def transcript(path: Path, entries: list[dict]) -> str:
    """Write a JSONL transcript and give back the path the hook payload names."""
    path.write_text(
        "".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8"
    )
    return str(path)


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
        "/usr/bin/git push origin main",
        "GIT_DIR=x git push origin main",
        "(git push origin main)",
        "cd /tmp && (git push origin main)",
        "git push origin heads/main",
        "git push origin issue-342:heads/main",
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
        "sudo git push origin main",
        "command git push origin main",
        "nohup git push origin main",
        "time git push origin main",
        "echo $(git status; git push origin main)",
        "x=$(cd /tmp; git push --force origin issue-1)",
        "echo `git status && git push origin main`",
        'echo "$(git push origin main)"',
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
        "echo don't && ls",
        'echo "the cost is $(date)"',
        'echo "$(git log --grep=push)"',
        "git log --oneline | grep push",
    ],
)
def test_a_command_that_pushes_nothing_draws_no_opinion(command: str) -> None:
    assert decision(command) is None


def test_a_tool_other_than_bash_draws_no_opinion() -> None:
    assert decision("git push origin main", tool_name="Edit") is None


# --- the commit family: what counts as a commit -----------------------------
#
# Detection is the false-deny guard: "commit" in a path, a message, or another
# command's output is ordinary work, and denying it would stop work this hook
# has no authority over. Only the git subcommand makes a command a commit.


@pytest.mark.parametrize(
    "command",
    [
        "git status",
        "git -C /tmp/commit-gate/repo log --oneline -1",
        "git log --oneline | head",
        "grep -rn commit tests/",
        'gh pr comment 345 --body "the commit lane is deny-by-default"',
        "git add -A && git status",
    ],
)
def test_a_command_that_commits_nothing_draws_no_opinion(command: str) -> None:
    assert decision(command) is None


@pytest.mark.parametrize(
    "command",
    [
        'git commit -m "push authority" && git status',
        'git commit -m "push authority; landed"',
        "git commit -m \"$(printf 'see git push rules')\"",
    ],
)
def test_a_commit_mentioning_push_is_no_push(command: str) -> None:
    # Read through an open commit lane, so the only verdict left to draw is the
    # push family's: a message carrying the word "push" pushes nothing.
    assert decision(command, agent_type="builder") is None


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m t",
        "cd /x && git commit -m t",
        "git -C /tmp/commit-gate/repo commit --allow-empty -m probe",
        'git commit -m "commit the commit family"',
        "git -c user.name=x commit -m t",
        "/usr/bin/git commit -m t",
        "git add -A; git commit -m t",
    ],
)
def test_a_commit_with_no_lane_open_is_denied(command: str) -> None:
    assert decision(command) == "deny"


# --- the commit family: lane 1, the factory's committing agent types ---------


@pytest.mark.parametrize("agent_type", ["builder", "judgment-facilitator"])
def test_a_committing_factory_type_may_commit(agent_type: str) -> None:
    assert decision("git commit -m t", agent_type=agent_type) is None


def test_a_subagent_of_another_type_may_not_commit() -> None:
    assert decision("git commit -m t", agent_type="general-purpose") == "deny"


def test_a_subagent_never_commits_on_a_parents_grant(tmp_path: Path) -> None:
    granted = transcript(tmp_path / "granted.jsonl", [user_turn(marker("commit-on"))])

    verdict = decision(
        "git commit -m t", agent_type="general-purpose", transcript_path=granted
    )

    assert verdict == "deny"


# --- the commit family: lane 2, the marker the user typed --------------------


def test_a_typed_grant_opens_the_lane(tmp_path: Path) -> None:
    granted = transcript(tmp_path / "granted.jsonl", [user_turn(marker("commit-on"))])

    assert decision("git commit -m t", transcript_path=granted) is None


def test_a_grant_typed_without_its_slash_opens_the_lane(tmp_path: Path) -> None:
    granted = transcript(
        tmp_path / "granted.jsonl",
        [user_turn(MARKER_OPEN + "commit-on" + MARKER_CLOSE)],
    )

    assert decision("git commit -m t", transcript_path=granted) is None


def test_a_grant_written_as_a_text_block_opens_the_lane(tmp_path: Path) -> None:
    granted = transcript(
        tmp_path / "granted.jsonl",
        [
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": marker("commit-on")}],
                },
            }
        ],
    )

    assert decision("git commit -m t", transcript_path=granted) is None


def test_a_transcript_holding_no_grant_keeps_the_lane_shut(tmp_path: Path) -> None:
    plain = transcript(tmp_path / "plain.jsonl", [user_turn("commit that for me")])

    assert decision("git commit -m t", transcript_path=plain) == "deny"


def test_a_marker_echoed_in_a_tool_result_is_no_grant(tmp_path: Path) -> None:
    echoed = transcript(
        tmp_path / "echoed.jsonl",
        [
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "x",
                            "content": marker("commit-on"),
                        }
                    ],
                },
            }
        ],
    )

    assert decision("git commit -m t", transcript_path=echoed) == "deny"


def test_a_marker_the_assistant_wrote_is_no_grant(tmp_path: Path) -> None:
    echoed = transcript(
        tmp_path / "echoed.jsonl",
        [
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "decoy " + marker("commit-on")}
                    ],
                },
            }
        ],
    )

    assert decision("git commit -m t", transcript_path=echoed) == "deny"


def test_a_session_with_no_transcript_to_read_is_denied() -> None:
    assert decision("git commit -m t") == "deny"


def test_a_revoked_grant_shuts_the_lane(tmp_path: Path) -> None:
    revoked = transcript(
        tmp_path / "revoked.jsonl",
        [user_turn(marker("commit-on")), user_turn(marker("commit-off"))],
    )

    assert decision("git commit -m t", transcript_path=revoked) == "deny"


def test_a_grant_typed_after_a_revocation_opens_the_lane(tmp_path: Path) -> None:
    renewed = transcript(
        tmp_path / "renewed.jsonl",
        [user_turn(marker("commit-off")), user_turn(marker("commit-on"))],
    )

    assert decision("git commit -m t", transcript_path=renewed) is None


# --- the commit family fails closed -----------------------------------------


def test_an_event_that_will_not_parse_is_denied() -> None:
    output = hook("{ this is not an event")

    assert output is not None
    assert output["permissionDecision"] == "deny"


def test_an_internal_failure_denies_with_the_fault_named(tmp_path: Path) -> None:
    # A transcript path naming a directory: the read raises where the hook
    # expects a file, standing in for any fault in the hook's own machinery.
    event = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m t"},
        "transcript_path": str(tmp_path),
    }

    output = hook(json.dumps(event))

    assert output is not None
    assert output["permissionDecision"] == "deny"
    assert "IsADirectoryError" in output["permissionDecisionReason"]


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
