---
name: handoff
description: Compact the current conversation into a handoff document a fresh agent can resume from.
disable-model-invocation: true
model: opus
effort: medium
arguments: [focus]
---

# Handoff

Compact this conversation into a document a fresh agent resumes from — {Write to scratch the handoff document; the OS temporary directory, not the workspace}. `focus`, when present, names what the next session will focus on; tailor the document to it.

The document carries a **suggested skills** section naming the skills the next agent should invoke, and points at the artifacts that hold the detail — specs, plans, Decision Records, issues, commits, diffs — citing them by path or URL, not restating them. Sensitive material is redacted: API keys, passwords, personally identifiable information.

A fresh agent cannot discover a temp file on its own, so {Report the absolute path of the handoff document} and {Report a ready-to-paste resume line for the user to carry into the new session; e.g. `Read /tmp/handoff-<name>.md and continue.`}
