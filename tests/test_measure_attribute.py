"""Behavioral tests for repo, issue and skill attribution of stored rows.

Paths are written against a workspace root passed in rather than this machine's,
so the repo rule is exercised without the tests knowing whose home they run in.
Command lines are copied in the shape the store actually holds them — the flags
and redirections and all — because reading that text is the whole technique.
"""

from pathlib import Path

import pandas as pd
import pytest
from measure_fakes import a_frame, a_payload

from dev_playbook.measure import attribute

WORKSPACE = Path("/home/geoff/workspace")
CHECKOUT = "/home/geoff/workspace/dev-playbook"


def a_bash_row(command: str, cwd: str = CHECKOUT) -> dict:
    """A `PostToolUse` payload for one Bash command line, as the store keeps it."""
    return a_payload(
        "PostToolUse",
        tool_name="Bash",
        tool_input={"command": command},
        duration_ms=12,
        cwd=cwd,
    )


# --- which repo a row worked in -----------------------------------------------


def test_a_checkout_under_the_workspace_names_its_repo() -> None:
    repo = attribute.repo_of("/home/geoff/workspace/media-tools", workspace=WORKSPACE)

    assert repo == "media-tools"


def test_a_worktree_belongs_to_the_repo_it_was_cut_from() -> None:
    cwd = "/home/geoff/workspace/dev-playbook/.claude/worktrees/issue-272-design"

    assert attribute.repo_of(cwd, workspace=WORKSPACE) == "dev-playbook"


def test_a_directory_deep_inside_a_repo_still_names_the_repo() -> None:
    cwd = "/home/geoff/workspace/dev-playbook/dotfiles/dot-claude/skills/usage-report"

    assert attribute.repo_of(cwd, workspace=WORKSPACE) == "dev-playbook"


def test_the_workspace_root_itself_belongs_to_no_repo() -> None:
    assert attribute.repo_of("/home/geoff/workspace", workspace=WORKSPACE) is None


def test_a_path_outside_the_workspace_belongs_to_no_repo() -> None:
    assert attribute.repo_of("/tmp/scratch", workspace=WORKSPACE) is None


# --- which issue a command touched ---------------------------------------------


@pytest.mark.parametrize("verb", ["edit", "close", "comment"])
def test_changing_an_issue_is_a_write(verb: str) -> None:
    issues = attribute.issue_references(f"gh issue {verb} 272 --body x", "dev-playbook")

    assert issues.writes == ("dev-playbook#272",)
    assert issues.reads == ()


def test_viewing_an_issue_is_a_read_and_never_a_write() -> None:
    command = "gh issue view 255 --comments > /tmp/scratch/255.md"

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues.reads == ("dev-playbook#255",)
    assert issues.writes == ()


def test_the_invocations_own_repo_flag_names_the_issue() -> None:
    command = "gh issue view 12 --repo GeoffNordling/story-forge --json body"

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues.reads == ("story-forge#12",)


def test_a_repo_flag_that_is_a_shell_substitution_leaves_the_rows_repo_standing() -> (
    None
):
    command = "gh issue view 293 --repo $(git remote get-url origin | sed 's|x||')"

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues.reads == ("dev-playbook#293",)


def test_two_invocations_on_one_line_each_keep_their_own_repo() -> None:
    command = (
        "gh issue view 293 --repo GeoffNordling/mission-control --json body; "
        "gh issue view 293"
    )

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues.reads == ("mission-control#293", "dev-playbook#293")


def test_the_same_issue_named_twice_on_one_line_is_one_contact() -> None:
    command = "gh issue view 279 --json title; gh issue view 279 | head -5"

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues.reads == ("dev-playbook#279",)


def test_an_issue_named_by_a_row_with_no_repo_is_left_unqualified() -> None:
    issues = attribute.issue_references("gh issue view 8", None)

    assert issues.reads == ("#8",)


def test_a_command_that_names_no_number_attributes_nothing() -> None:
    command = "gh issue list --repo GeoffNordling/dev-playbook --state open --limit 30"

    issues = attribute.issue_references(command, "dev-playbook")

    assert issues == attribute.Issues((), ())


def test_a_command_that_never_touches_gh_attributes_nothing() -> None:
    issues = attribute.issue_references("git log --oneline -5", "dev-playbook")

    assert issues == attribute.Issues((), ())


# --- which skill ran ------------------------------------------------------------


def test_a_submit_carrying_a_folded_command_name_names_the_skill() -> None:
    payload = a_payload(
        "UserPromptSubmit", prompt="/commit", command_name="commit", command_args=""
    )

    assert attribute.skill_of(payload) == "commit"


def test_a_skill_tool_row_names_the_skill_its_input_was_called_with() -> None:
    payload = a_payload(
        "PostToolUse", tool_name="Skill", tool_input={"skill": "open-pr", "args": "272"}
    )

    assert attribute.skill_of(payload) == "open-pr"


def test_a_skill_row_written_before_capture_kept_inputs_names_no_skill() -> None:
    payload = a_payload("PostToolUse", tool_name="Skill", duration_ms=8000)

    assert attribute.skill_of(payload) is None


def test_a_skill_row_whose_kept_input_names_no_skill_is_refused() -> None:
    payload = a_payload("PostToolUse", tool_name="Skill", tool_input={"args": "272"})

    with pytest.raises(attribute.AttributionError, match="no skill"):
        attribute.skill_of(payload)


def test_a_row_that_ran_no_skill_names_none() -> None:
    assert attribute.skill_of(a_bash_row("make check")) is None


# --- the whole frame ------------------------------------------------------------


def test_every_row_gets_every_attribution_column() -> None:
    events = a_frame([a_payload("SessionStart", source="startup")])

    frame = attribute.attributed(events, workspace=WORKSPACE)

    assert list(frame.columns[-4:]) == list(attribute.ATTRIBUTION_COLUMNS)
    assert frame.iloc[0]["repo"] == "dev-playbook"
    assert frame.iloc[0]["issue_writes"] == ()
    assert pd.isna(frame.iloc[0]["skill"])


def test_a_name_column_is_typed_the_same_whether_or_not_a_row_names_one() -> None:
    ran_one = a_frame(
        [a_payload("PostToolUse", tool_name="Skill", tool_input={"skill": "commit"})]
    )
    ran_none = a_frame([a_bash_row("make check")])

    named = attribute.attributed(ran_one, workspace=WORKSPACE)
    unnamed = attribute.attributed(ran_none, workspace=WORKSPACE)

    assert named["skill"].dtype == unnamed["skill"].dtype
    assert named.iloc[0]["skill"] == "commit"
    assert pd.isna(unnamed.iloc[0]["skill"])


def test_the_callers_frame_is_left_as_it_was() -> None:
    events = a_frame([a_payload("SessionStart", source="startup")])

    attribute.attributed(events, workspace=WORKSPACE)

    assert "repo" not in events.columns


def test_reads_and_writes_of_one_session_stay_in_separate_columns() -> None:
    events = a_frame(
        [
            a_bash_row("gh issue view 300 --repo GeoffNordling/dev-playbook"),
            a_bash_row("gh issue edit 272 --add-label design"),
        ]
    )

    frame = attribute.attributed(events, workspace=WORKSPACE)

    assert list(frame["issue_reads"]) == [("dev-playbook#300",), ()]
    assert list(frame["issue_writes"]) == [(), ("dev-playbook#272",)]


def test_a_rows_own_repo_qualifies_the_issue_its_command_names() -> None:
    events = a_frame(
        [a_bash_row("gh issue view 4", "/home/geoff/workspace/media-tools")]
    )

    frame = attribute.attributed(events, workspace=WORKSPACE)

    assert frame.iloc[0]["repo"] == "media-tools"
    assert frame.iloc[0]["issue_reads"] == ("media-tools#4",)


def test_a_row_that_ran_no_command_names_no_issue() -> None:
    events = a_frame([a_payload("PostToolUse", tool_name="Read", duration_ms=3)])

    frame = attribute.attributed(events, workspace=WORKSPACE)

    assert frame.iloc[0]["issue_reads"] == ()
    assert frame.iloc[0]["issue_writes"] == ()
