"""Read a stint's plan: its tasks and the checkpoints that split them.

A plan is ``PLAN.md`` in the workstream folder. A task is a line that opens
``- [ ] `` and is checked off as ``- [x] ``. A checkpoint is a line that is
exactly ``<!-- [ ] checkpoint -->``, checked off as ``<!-- [x] checkpoint -->``.
The tasks between one checkpoint and the next are a segment: the stint works
a segment, then its reviewer and principal meet at the checkpoint.

    - [x] Add wordcount.py.
    <!-- [x] checkpoint -->
    - [ ] Add the tests.          <- the open segment: 1 task
    <!-- [ ] checkpoint -->
    - [ ] Write the README.
    <!-- [ ] checkpoint -->

The plan is read as plain text from the work copy, never through git.
"""

import re
from dataclasses import dataclass

OPEN_MARK = "<!-- [ ] checkpoint -->"
DONE_MARK = "<!-- [x] checkpoint -->"
TASK = re.compile(r"- \[ \] ")


@dataclass(frozen=True)
class PlanState:
    """What the loop needs to know about the plan at one moment."""

    done: int
    """Checkpoints checked off."""
    open: int
    """Checkpoints not yet checked off."""
    segment: int
    """Unchecked tasks before the first open checkpoint and after the last done one."""
    left: int
    """Unchecked tasks in the whole plan."""


def plan_state(text: str) -> PlanState:
    """Count the plan's checkpoints and its unchecked tasks."""
    lines = text.splitlines()
    done = [i for i, line in enumerate(lines) if line.strip() == DONE_MARK]
    open_ = [i for i, line in enumerate(lines) if line.strip() == OPEN_MARK]
    tasks = [i for i, line in enumerate(lines) if TASK.match(line)]
    start = max([i for i in done if not open_ or i < open_[0]], default=-1)
    end = open_[0] if open_ else len(lines)
    return PlanState(
        done=len(done),
        open=len(open_),
        segment=sum(1 for i in tasks if start < i < end),
        left=len(tasks),
    )
