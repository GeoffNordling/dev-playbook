---
name: compact-prep
description: Commit outstanding work and get the session ready before the user runs /compact.
disable-model-invocation: true
model: inherit
effort: xhigh
arguments: [important]
---

# Compact Prep

The user is about to run `/compact`. Get the session ready — a pre-flight
check.

## Procedure

1. {Run [/commit](~/.claude/skills/commit/SKILL.md); split unrelated
   changes into separate commits}.

2. Mention anything important at risk — only if something stands out.
   Compaction aims to preserve the conversation and is usually good enough,
   so saying nothing here is normal. Work from what is in front of you
   rather than searching the session for candidates: if one thing is
   genuinely important and you doubt a summary would carry it — a decision,
   an approach ruled out, a plan agreed but never written down — name it in
   a line. Skip anything recoverable from the committed files, the issue, or
   `git log`.

3. {Report what was committed, the one at-risk item from step 2 if there
   was one, and a plain ready verdict; persisting it is the user's call}.
   `important`, when given, is what the user believes matters — confirm
   specifically that it is committed or flagged, and say which.
