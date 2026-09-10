# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what earlier iterations did.

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

## Log

<!-- iterations append one line each below this line -->
