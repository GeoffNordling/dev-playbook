---
type: General-Sheet
title: Runbook
description: What a runbook is — an invocable command written as documentation — its seven verbs, the family the Runbook doc-type serves, and where it lives
---

# Runbook

A **runbook** is an invocable command written as documentation: a
skill or an agent definition. It is invoked by name — args in, a
report out, effects on state in between — and its body is natural
imperative English commanding the executing agent.

## The verbs

Seven, each an edge from the runbook to a node:

- **read** — what it consults.
- **write** — what state it changes.
- **do** — the runbooks and scripts it runs.
- **override** — a previous clause it substitutes.
- **never** — a write it bans.
- **args** — what it takes from its caller.
- **report** — what it gives back to its caller.

## The family

The repo's harness commands: every skill and every agent definition. A
command's caller is owed a contract, so every runbook carries one,
written into its own prose as spans.

## Where a runbook lives

Where the harness loads it from. The roots are
[Claude Code Files](/standards/harness/files.md)'; the layout under them
is Runbook Conventions'
[Location](/standards/harness/runbook-conventions.md#location).
