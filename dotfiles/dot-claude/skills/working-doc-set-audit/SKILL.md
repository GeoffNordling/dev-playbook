---
name: working-doc-set-audit
description: Audit a working documentation set — the in-process Markdown files of one work stream — against the working-documentation-sets standard, reporting findings without editing. Use when working docs have drifted, or when asked to audit a set of planning files for duplication, staleness, conflicts, or term drift.
disable-model-invocation: false
model: sonnet
effort: high
argument-hint: "[set-hint]"
---

# Working Doc Set Audit

Send one working documentation set to the `set-auditor` subagent, which
audits it against
[Working Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md)
and reports findings without editing.

## Target

The invocation may carry a hint identifying the set: its root file, its
directory, or a description such as "the no-more-slop working files."

- **No hint.** Operate on the set most clearly in focus in the current
  conversation. Where none is, ask which.
- **Hint.** Resolve it to a root file. Where it matches nothing, ask.

## Dispatch

Launch the `set-auditor` subagent (Agent tool,
`subagent_type: set-auditor`, `model: opus`), naming the working
directory and the set's root file in the prompt.

This skill edits nothing and commits nothing.

## Relay

Deliver the agent's report to the user unchanged.
