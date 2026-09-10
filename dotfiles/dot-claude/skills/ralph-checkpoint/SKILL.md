---
name: ralph-checkpoint
description: Reviews a finished segment of a Ralph loop through a fork of this session, then relays what it found and what the next segment holds. Use when a ralph-loop run returns at a checkpoint and the next segment is waiting on a review.
disable-model-invocation: false
model: inherit
effort: high
arguments: [run-hint]
---

# Ralph Checkpoint

A Ralph loop has returned at a checkpoint. Review the segment it just
finished, then release the next one — or, at the last checkpoint, confirm the
finished plan actually landed what it claims.

This session owns the run. It launches each segment, calls this skill between
segments, and launches the next — so the review happens in a fork, and only a
ten-line report comes back. That is what keeps a run of a dozen segments
inside one session.

## Confirm the stop

The `ralph-loop` workflow returned. Read what it returned before anything
else:

- A `blocker` means the loop stopped without reaching a checkpoint — a red
  gate on entry, a malformed marker, an iteration that returned nothing.
  There is no segment to review. Report the blocker to the user and stop; a
  blocker is the user's call, not the fork's.
- No blocker means the segment ran to its checkpoint. Continue.

The argument is a run hint: anything naming the run, usually nothing, since
this session launched it. Take the plan file, the progress file, the check
gate, and the working directory from the launch you made. Where this session
did not launch the run and cannot name those four, ask the user rather than
guess — the fork edits the plan it is pointed at.

## Dispatch the fork

{Launch [ralph-checkpointer](~/.claude/agents/ralph-checkpointer.md) as a fork
subagent (`subagent_type: "fork"`)}; the fork inherits this conversation, so
everything the run has already established reaches it without being restated.

A fork reads no agent definition on its own. Build its launch prompt from
five things:

1. The working directory.
2. The plan file path.
3. The progress file path.
4. The check gate command, or that there is none.
5. The instruction to read
   [ralph-checkpointer](~/.claude/agents/ralph-checkpointer.md) and carry out
   its procedure.

For example: "Working directory: `<worktree path>`. Plan: `PLAN.md`.
Progress: `PROGRESS.md`. Check gate: `make check`. Read
`~/.claude/agents/ralph-checkpointer.md` and carry out its procedure."

The dispatch is complete when the fork has returned its report.

## Relay and release

{Report the fork's findings to the user}: what the segment landed, anything a
Verify clause failed, what the fork changed in the plan and why, and what is
next. Keep it to the fork's own length — this is a relay, not a second review.

Then act on what the fork said:

- **Tasks remain.** State the launch command for the next segment on one
  line, ready to paste, and never run it yourself — the run is the user's to
  continue, and a checkpoint that releases itself is not a checkpoint.
- **The plan is complete.** Say so, and say what the whole run produced. The
  plan and progress files have done their work; whether they stay in the
  history or come out in a final commit is the user's call.
- **A Verify clause failed, or a task was reverted.** Lead with that. The
  fork has already written the fix task into the next segment, so the run
  continues, but the user reads the failure first.

The skill is complete when the user has the report and, where the run
continues, the one command that starts the next segment.
