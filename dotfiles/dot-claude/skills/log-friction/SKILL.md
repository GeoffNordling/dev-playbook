---
name: log-friction
description: Capture a friction entry — pain felt, time lost, a manual intervention — into mission-control's friction log from any repo, commit it there, and hand the user the push. Use when the user invokes /log-friction, says "log this friction", "that was friction", "add to the friction log", or asks to record a recurring pain or intervention.
disable-model-invocation: false
model: sonnet
effort: xhigh
argument-hint: "[what bit, one line]"
---

# Log Friction

Append one entry to the friction log —
[friction-log.md](~/workspace/mission-control/friction-log.md) —
commit it, and hand the user the push. The log feeds triage:
twice-felt friction becomes a backlog candidate on board.md, and
only Selection places it as a bet.
Recording friction is not a commitment to fix it — capture and move
on; never start fixing the friction as part of logging it.

## Friction: $ARGUMENTS

If no description was given, infer the candidate friction from recent
session context and confirm it with the user before writing anything.

## Steps

1. Read [friction-log.md](~/workspace/mission-control/friction-log.md).
   Follow the entry format defined there — the log file, not this
   skill, owns the format.
2. Decide: is this a **repeat bite** of an existing entry (add a
   `Felt:` line to it) or **new friction** (new entry)? Match on what
   actually bit, not on surface wording; if genuinely ambiguous, ask.
3. Write the entry in the owner's register — one or two plain lines,
   dated, stating what happened and where. No analysis, no proposed
   fix unless the user gave one.
4. Commit via /commit, applied to `~/workspace/mission-control`
   (use `git -C`; the session's cwd is usually another repo). Stage
   **only** `friction-log.md` — the repo may hold unrelated work
   awaiting the owner's diff review.
5. Remind the user to push (their YubiKey): hand them, as one line,
   `git -C ~/workspace/mission-control push`.
