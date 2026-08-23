---
name: compact-prep
description: Commit outstanding work and get the session ready before the user runs /compact.
disable-model-invocation: true
model: inherit
effort: xhigh
argument-hint: "[what the user considers important]"
---

# Compact Prep

The user is about to run `/compact`. Get the session ready — a pre-flight
check.

## Procedure

1. **Commit everything.** Use /commit. Split unrelated changes into separate
   commits.

2. **Mention anything important at risk — only if something stands out.**
   Compaction aims to preserve the conversation and is usually good enough,
   so saying nothing here is normal. Work from what is in front of you
   rather than searching the session for candidates: if one thing is
   genuinely important and you doubt a summary would carry it — a decision,
   an approach ruled out, a plan agreed but never written down — name it in
   a line. Skip anything recoverable from the committed files, the issue, or
   `git log`.

3. **Report and stop.** State what you committed, add the one thing from
   step 2 if there was one, and give a plain ready verdict. Persisting it is
   the user's call.

## Argument

$ARGUMENTS, when given, is what the user believes matters. Confirm
specifically that it is committed or flagged, and say which.
