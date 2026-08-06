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
and commit it. The log feeds curation:
twice-felt friction becomes a curation item mapped onto the idea
archive, and only Selection scopes it into a Cycle.
Recording friction is not a commitment to fix it — record and move on.

## Friction: $ARGUMENTS

If no description was given, infer the candidate friction from recent
session context and confirm it with the user before writing anything.

## Steps

1. Read [friction/log.md](~/workspace/mission-control/friction/log.md).
   Follow the entry format defined there — the log file, not this
   skill, owns the format.
2. Write the entry in the owner's register — one or two plain lines,
   dated, stating what happened and where, and carrying a proposed
   fix only where the user gave one.
3. Commit via /commit, applied to `~/workspace/mission-control`
   (use `git -C`; the session's cwd is usually another repo). Stage
   **only** `friction/log.md` — the repo may hold unrelated work; ignore it.
   The commit skill pushes as part of the commit.
