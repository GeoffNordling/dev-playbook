---
name: compact-prep
description: Commit outstanding work and get the session ready before the user runs /compact.
disable-model-invocation: true
model: inherit
effort: xhigh
argument-hint: "[what the user considers important]"
---

# Compact Prep

The user is about to run `/compact`. Get the session ready.

## Procedure

1. **Commit everything.** Invoking this skill is the user's authorization to
   commit — the standing "commit when told" rule is satisfied. Use /commit.
   Split unrelated changes into separate commits.

2. **Mention anything important at risk — only if something already stands
   out.** Compaction is itself trying to preserve the conversation and is
   usually good enough, so saying nothing here is the normal, expected
   outcome. Do not trawl back through the session hunting for candidates, and
   do not produce a list. If one thing is genuinely important and you doubt a
   summary would carry it — a decision, an approach ruled out, a plan agreed
   but never written down — name it in a line. Skip anything recoverable from
   the committed files, the issue, or `git log`.

3. **Report and stop.** State what you committed, add the one thing from step 2
   if there was one, and give a plain ready verdict. Do not persist anything
   yourself — the user decides what is worth keeping.

Be quick. This is a pre-flight check, not an audit.

## Argument

$ARGUMENTS, when given, is what the user believes matters. Confirm specifically
that it is committed or flagged, and say which.
