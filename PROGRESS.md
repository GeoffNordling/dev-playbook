# Progress log

The running memory of this Ralph loop. Each iteration appends one line to the
log — what it did and what is next — newest at the bottom. A fresh agent reads
this before starting, to see what earlier iterations did.

Two writers, two audiences. Iterations write judgment calls for the checkpoint
reviewer to read at the next checkpoint. The reviewer writes decisions for the
user to read at PR time.

## Recording a judgment call

Where the plan and its sources do not settle a point, do not stop and do not
decide it silently. Take the smallest step that keeps the check gate green, then
add one indented line under your own entry in the log, in this shape:

    - judgment: <what was unsettled> → <what you did>, because <why>

One line, every time. The entry is a pointer, not the evidence: whoever reviews
reads the diff and the artifact anyway.

Write one even when you are fairly sure. The cost of a recorded call is a line;
the cost of a silent wrong turn is every task built on top of it. A reviewer
rules on each call at the next checkpoint and writes the ruling into the plan —
accepted calls become Working notes, reverted ones become a fix task.

## Decisions

Written by the checkpoint reviewer, never by an iteration. One line for each
change that moved the plan away from the shape the user approved at setup, and
for anything the reviewer chose not to do that the user would expect. The user
reads this at PR time and nowhere earlier, so it is the whole account of how
the run drifted from what was agreed.

    - <checkpoint>: <what changed in the plan> — <what made it change>

<!-- the reviewer appends below this line -->

## Log

<!-- iterations append one line each below this line -->

- Step 1, python: `checks/python.py` with two functions and two ruff hook registrations, `test_python.py`, `style.md` edited to the triage, `python-lint` retired, report `rewrite/python.md` written; next is Step 2, testing, after the checkpoint.
    - judgment: the docstring rule's old Why was not addressed by the triage → kept it after the old sentence in the new Why, because it explains the `test_` exception that the old sentence names.
    - judgment: the triage drops the future-import exception but gives no blockquote → cut the `unless ...` clause and kept the rest of the sentence as written, because that is the smallest edit that matches the ruling.
    - judgment: the hook names for the two ruff rules → `ruff-check` and `ruff-format`, the hook ids in `.pre-commit-config.yaml`, because the triage names only the tool.
    - judgment: `docs/decisions/0011` names `python-lint` in its Consequences → dropped the name from its list, because the prompt says to remove every mention outside `working-docs/`; an Accepted record now has a changed body.
    - judgment: `pyast.py` stays, since `testing-lint` and `repo-lint` import it → rewrote its module docstring without the retired name.
