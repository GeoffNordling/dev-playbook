---
name: log-friction
description: Record a friction entry — pain felt, time lost, a manual intervention — in mission-control's friction log from any repo. Use when the user says to log friction, or asks to record a recurring pain or manual intervention.
disable-model-invocation: false
model: sonnet
effort: xhigh
argument-hint: "[what bit, one line]"
---

# Log Friction

Append one entry to the friction log —
[friction/log.md](~/workspace/mission-control/friction/log.md) —
and commit it. The log feeds curation: twice-felt friction becomes a
curation item mapped onto the idea archive, and only Selection scopes
it into a Cycle.

## Friction: $ARGUMENTS

Run to completion without asking the user anything. This skill is
fire-and-forget: the user typed one line and moved on, so a
clarifying question stalls the work unanswered.

- Where the input is long, rambling, or vents several complaints at
  once, distil it to the log's entry format without losing the
  owner's actual point.
- Where several distinct frictions arrived in one message, write one
  entry each.
- Where no description was given, infer the friction from recent
  session context and write it.
- Where there is genuinely nothing to record, say so and stop.

An imperfect entry is cheap: the log is append-only prose, curation
reads it later, and the owner can correct it in seconds.

## Steps

1. Read [friction/log.md](~/workspace/mission-control/friction/log.md).
   Follow the entry format defined there — the log file owns the
   format. That includes its rule for repeat bites: where the
   friction already has an entry, add a `Felt:` line to that entry
   rather than opening a new one.
2. Write the entry in the owner's register — one or two plain lines,
   dated from `date +%F`, stating what happened and where, and
   carrying a proposed fix only where the user gave one.
3. Commit and push, {only where there is something to record}. Stage
   **only** `friction/log.md` — the repo may
   hold unrelated work; leave it alone. One line, `git` leading so it
   keeps its credential access, and `-C` throughout because the
   session's cwd is some other repo:

       git -C ~/workspace/mission-control add friction/log.md && git -C ~/workspace/mission-control commit -m "<subject>" -m "Co-Authored-By: Claude <noreply@anthropic.com>" && git -C ~/workspace/mission-control push

4. Report in one line: the entry's short name, and that the push
   landed.
