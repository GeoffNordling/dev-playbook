"""Guards the seam between ``judgments-run plan`` and the judgments workflow.

The workflow does no planning: the CLI emits its entire argument payload and the
orchestrating agent copies that JSON across without reading it. That makes the
payload's shape a contract between a Python function and a JavaScript file which
share no bytes and cannot import each other, so nothing at runtime would catch
them drifting apart -- the workflow would simply reject every plan, or worse,
accept one with a field quietly missing.

These tests are that check. They read the workflow source as text and assert the
two constants it validates plans against still match what ``plan`` produces, plus
the two structural invariants that keep shell commands out of the workflow layer
entirely: it spells no command of its own, and every agent it spawns is a judge.
"""

import re
from pathlib import Path

import pytest

from dev_playbook.judgments.runner import (
    CLI_PLACEHOLDER,
    ID_PLACEHOLDER,
    ROOT_PLACEHOLDER,
    plan,
)

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / "dotfiles"
    / "dot-claude"
    / "workflows"
    / "judgments.js"
)

SOURCE = WORKFLOW.read_text(encoding="utf-8")


def _string_array(name: str) -> list[str]:
    """The elements of a ``const <name> = ['a', 'b']`` array literal in the source."""
    match = re.search(rf"const {name} = \[(.*?)\]", SOURCE, re.DOTALL)
    assert match is not None, f"{name} is not declared as an array literal"
    return re.findall(r"'([^']*)'", match.group(1))


def _string_constant(name: str) -> str:
    """The value of a ``const <name> = '...'`` declaration in the source."""
    match = re.search(rf"const {name} = '([^']*)'", SOURCE)
    assert match is not None, f"{name} is not declared as a string literal"
    return match.group(1)


@pytest.fixture
def empty_plan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """A plan over no declarations: the payload's shape, against a throwaway cache."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return plan({tmp_path: []})


def test_workflow_validates_exactly_the_keys_the_cli_emits(
    empty_plan: dict[str, object],
) -> None:
    # The workflow requires all of PLAN_KEYS and rejects anything outside it, so
    # this list and plan()'s output keys must be the same set or every run fails.
    assert set(_string_array("PLAN_KEYS")) == set(empty_plan)


def test_workflow_substitutes_the_placeholders_the_cli_leaves_behind(
    empty_plan: dict[str, object],
) -> None:
    # The judge prompt ships once, with markers where each job's invocation,
    # root, and id go. The markers are authored in Python and substituted in
    # JavaScript.
    assert _string_constant("CLI_PLACEHOLDER") == CLI_PLACEHOLDER
    assert _string_constant("ROOT_PLACEHOLDER") == ROOT_PLACEHOLDER
    assert _string_constant("ID_PLACEHOLDER") == ID_PLACEHOLDER
    for placeholder in (CLI_PLACEHOLDER, ROOT_PLACEHOLDER, ID_PLACEHOLDER):
        assert placeholder in str(empty_plan["judge_prompt"])


def test_workflow_builds_every_command_from_the_plan() -> None:
    # `cli` names an absolute interpreter, and every command built from it gets
    # an explicit --root, so it runs without a PATH lookup, an activated
    # virtualenv, or a particular working directory -- none of which a judge
    # agent is guaranteed. `uv run` is the spelling that assumes all three; it
    # is what the deleted planning agent used, and what sent it looking for a
    # project to run under.
    assert "${PLAN.cli} --root ${root} record " in SOURCE
    assert "uv run" not in SOURCE


def test_every_agent_the_workflow_spawns_is_a_judge() -> None:
    # Planning and recording are shell work and belong at the layer with a shell.
    # One agent() call site means this workflow can only judge.
    assert SOURCE.count("await agent(") == 1
