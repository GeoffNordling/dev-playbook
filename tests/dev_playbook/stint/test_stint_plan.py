"""The plan reader counts tasks and checkpoints as the loop needs them."""

from dev_playbook.stint.plan import PlanState, plan_state

PLAN = """\
# Plan

- [x] one
<!-- [x] checkpoint -->
- [ ] two
- [ ] three
<!-- [ ] checkpoint -->
- [ ] four
<!-- [ ] checkpoint -->
"""


def test_the_open_segment_is_after_the_last_done_checkpoint() -> None:
    assert plan_state(PLAN) == PlanState(done=1, open=2, segment=2, left=3)


def test_a_plan_with_no_checkpoints_is_one_segment() -> None:
    assert plan_state("- [ ] a\n- [ ] b\n") == PlanState(0, 0, 2, 2)


def test_a_finished_plan_has_nothing_left() -> None:
    text = "- [x] a\n<!-- [x] checkpoint -->\n"
    assert plan_state(text) == PlanState(done=1, open=0, segment=0, left=0)


def test_an_indented_task_line_is_not_a_task() -> None:
    """Only a list item at the line's start counts, not a quoted example."""
    assert plan_state("    - [ ] quoted\n").left == 0
