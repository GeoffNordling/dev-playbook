---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
disable-model-invocation: true
model: opus
effort: medium
argument-hint: "[what the next session will focus on]"
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it to the OS temporary directory — not the current workspace.

A fresh agent cannot discover a temp file on its own, so finish by reporting the absolute path and a ready-to-paste resume line for the next session — e.g. `Read /tmp/handoff-<name>.md and continue.` The user carries that line into the new session.

Include a **suggested skills** section listing the skills the next agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, Decision Records, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If an argument was passed ($ARGUMENTS), treat it as a description of what the next session will focus on and tailor the document accordingly.
