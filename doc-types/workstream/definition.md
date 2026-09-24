---
type: General-Sheet
title: Workstream
description: What a workstream is — one line of work, its ideas, target state, and context — driven by a loop and adding no verb, the family it serves, and where it lives
---

# Workstream

A **workstream** holds one line of work: the ideas, the target state,
and the context of one job, and the record of the stints that advanced
it.

## The verbs

None. A workstream is driven: a [loop](/doc-types/loop/definition.md)
drives it, as a standard is held to and a runbook is invoked. It points
at whatever its work needs, and each of its stints names the loop that
drove it, but none of those pointers is a verb.

## The family

The head files typed `Workstream`, one per line of work. The loop and
its driver belong to a stint, not to the workstream: one loop drives
many workstreams, and each stint records which loop drove it. A
workstream ends when the user accepts or deletes it.

## Where a workstream lives

A workstream is a directory under `workstreams/`, and its head file is
`WORKSTREAM.md` in it, named for its type as `SKILL.md` is. A child
workstream is a subdirectory with a head file of its own. The rename of
`working-docs/` to `workstreams/`, and of each `ROOT.md` to
`WORKSTREAM.md`, is planned, so no instance exists yet.
