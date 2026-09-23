---
name: ralph-checkpoint
description: Reviews a finished segment of a Ralph loop through a fresh reviewer, takes the user's ruling on its top findings, and adapts the plan through a fork of this session before releasing the next segment. Use when a ralph-loop run returns at a checkpoint and the next segment is waiting on a review.
disable-model-invocation: false
model: inherit
effort: high
arguments: [run-hint]
---

# Ralph Checkpoint

A Ralph loop has returned at a checkpoint. Review the segment it just
finished, then release the next one — or, at the last checkpoint, confirm the
finished plan actually landed what it claims.

Three agents split the work, each where its context helps:

- **A fresh reviewer finds the problems.** It carries none of this
  conversation, so it reads the work against the plan and nothing else.
- **The user rules** on the reviewer's top three findings.
- **A fork of this session adapts the plan.** It inherits the conversation
  that designed the plan, so it knows what the plan meant and acts on the
  ruling by that intent.

This session only drives. It launches each agent and relays two short
reports, and never reads the findings in full, so a run of a dozen segments
stays inside one session.

## Confirm the stop

The `ralph-loop` workflow returned. Read what it returned before anything
else:

- A `blocker` means the loop stopped without reaching a checkpoint — a red
  gate on entry, a malformed marker, an iteration that returned nothing.
  There is no segment to review. Report the blocker to the user and stop; a
  blocker is the user's call, not the review's.
- No blocker means the segment ran to its checkpoint. Continue.

The argument is a run hint: anything naming the run, usually nothing, since
this session launched it. Take the plan file, the progress file, the check
gate, and the working directory from the launch you made. Where this session
did not launch the run and cannot name those four, ask the user rather than
guess — the fork edits the plan it is pointed at.

## Name the segment

Two values go to both agents:

- **The commit range.** The segment starts after the most recent commit whose
  subject begins `checkpoint:`, or, where there is none, after the commit that
  added the plan file:

      git -C <working-directory> log -1 --format=%H --grep='^checkpoint:'
      git -C <working-directory> log -1 --format=%H --diff-filter=A -- <plan-file>

  Take the first command's hash, or the second's where the first prints
  nothing. The range is `<hash>..HEAD`.
- **The findings file.** `<scratchpad>/ralph-review-<n>.md` in this session's
  scratchpad directory, where `<n>` is one more than the count of
  `<!-- [x] checkpoint -->` lines in the plan. It lives outside the repository,
  so the iterations never read it.

## Dispatch the reviewer

{Launch [ralph-reviewer](~/.claude/agents/ralph-reviewer.md) as a fresh
subagent (`subagent_type: "ralph-reviewer"`, `model: "opus"`)}, never a fork.
Say on screen that one Opus reviewer is running.

Its launch prompt carries six things: the working directory, the plan file,
the progress file, the check gate or that there is none, the commit range,
and the findings file path. For example: "Working directory:
`<worktree path>`. Plan: `PLAN.md`. Progress: `PROGRESS.md`. Check gate:
`make check`. Segment: `a1b2c3d..HEAD`. Findings file:
`<scratchpad>/ralph-review-2.md`."

The dispatch is complete when the reviewer has returned its count and top
three.

## Take the ruling

{Report the reviewer's reply to the user verbatim}: the count by tier, the
path of the full list, and the three findings. Do not add to it or soften it.

- **Zero findings.** There is nothing to rule on. Go straight to the fork, with
  "no findings" as the ruling.
- **Any findings.** End the turn and wait. The user says which of the top three
  are real. Where the user wants to go deeper into a finding, read that one
  entry from the findings file and discuss it; read no others.

The ruling is complete when the user has said which of the top three stand.

## Dispatch the fork

{Launch [ralph-checkpointer](~/.claude/agents/ralph-checkpointer.md) as a fork
subagent (`subagent_type: "fork"`)}; the fork inherits this conversation, and
with it the ruling, but a fork reads no agent definition on its own. Build its
launch prompt from seven things:

1. The working directory.
2. The plan file path.
3. The progress file path.
4. The check gate command, or that there is none.
5. The findings file path.
6. The user's ruling, finding by finding, in the user's own words where they
   gave reasons.
7. The instruction to read
   [ralph-checkpointer](~/.claude/agents/ralph-checkpointer.md) and carry out
   its procedure.

For example: "Working directory: `<worktree path>`. Plan: `PLAN.md`.
Progress: `PROGRESS.md`. Check gate: `make check`. Findings:
`<scratchpad>/ralph-review-2.md`. Ruling: 1 confirmed, 2 confirmed, 3
rejected — the case it names is not one any repo writes. Read
`~/.claude/agents/ralph-checkpointer.md` and carry out its procedure."

The dispatch is complete when the fork has returned its report.

## Relay and release

{Report the fork's report to the user}: what the segment landed, how many
findings became fix tasks, what the fork changed in the plan and why, and what
is next. Keep it to the fork's own length — this is a relay, not a third
review.

Then act on what the fork said:

- **Tasks remain.** Launch the next segment yourself, with the same
  `Workflow` call that started the last one.
- **The plan is complete.** Say so, and say what the whole run produced. The
  plan and progress files have done their work; whether they stay in the
  history or come out in a final commit is the user's call.

Stop and hand the run back to the user in two cases only: the plan is
complete, or the loop cannot continue — a blocker, or a fork that reports the
plan is no longer worth running. Anything short of that, keep going.

The skill is complete when the plan is done, the run is blocked, or the next
segment is running.
