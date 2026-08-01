---
name: handoff
description: Compact the current conversation into a handoff document a fresh agent can resume from. Use when the user asks to carry this session's work into a new one.
disable-model-invocation: true
model: opus
effort: medium
argument-hint: "[what the next session will focus on]"
---

# Handoff

Compact this conversation into a document a fresh agent resumes from, saved to the OS temporary directory rather than the workspace. `$ARGUMENTS`, when present, names what the next session will focus on; tailor the document to it.

The document carries a **suggested skills** section naming the skills the next agent should invoke, and points at the artifacts that already hold the detail — specs, plans, Decision Records, issues, commits, diffs — citing them by path or URL rather than restating them. Sensitive material is redacted: API keys, passwords, personally identifiable information.

A fresh agent cannot discover a temp file on its own, so the run ends by reporting the absolute path and a ready-to-paste resume line — e.g. `Read /tmp/handoff-<name>.md and continue.` The user carries that line into the new session.
