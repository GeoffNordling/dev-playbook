---
name: idea
description: Deposit raw idea material verbatim into mission-control's inbox/ from any repo — a dictation, a pasted agent conversation, a dump of disjoint ideas.
disable-model-invocation: true
model: sonnet
effort: xhigh
arguments: [material]
---

# Idea

A thin pointer so /idea works from any repo on desktop without
`cd`-ing into mission-control. {Run [mission-control's idea
skill](~/workspace/mission-control/.claude/skills/idea/SKILL.md)
verbatim; it owns the routing, the deposit format, the
`CLAUDE_CODE_REMOTE` path-selection, and the receipt}. Apply only the
cwd-translation overrides below.

## Overrides

mission-control's idea skill assumes the session's cwd **is**
mission-control, so it uses repo-relative paths (`inbox/…`) and a plain
`git`. This pointer fires from another repo, so force mission-control as
the target instead — the same discipline /log-friction uses:

- **Inbox path only.** The direct path (hand-off to /curate) is
  unavailable outside mission-control; if the owner voiced direct
  filing, deposit to inbox and say so in the receipt.
- **Working repo is always `~/workspace/mission-control`**, whatever the
  session's cwd.
- **Every file write goes under `~/workspace/mission-control/inbox/`** —
  each deposit file and `inbox/index.md`.
- **Every git command runs via `git -C ~/workspace/mission-control`.**
- **Stage only `inbox/` paths.** The current repo and mission-control may
  both hold unrelated work awaiting the owner's diff review.
- **Touch nothing in the current repo.**
- Follow the mission-control skill's own `CLAUDE_CODE_REMOTE`
  path-selection — in practice always the desktop path here: a commit
  on mission-control's branch, pushed as part of the commit
  (`git -C ~/workspace/mission-control push`).
