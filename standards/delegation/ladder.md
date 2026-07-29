---
type: Standard
title: Delegation Ladder
description: The three delegation tiers — orchestrator, limited intelligence, no intelligence — what each is for, and how a session dispatches to them
---

# Delegation Ladder

How a session divides work across models. Intelligence is the expensive
resource and the session's own context is the scarce one, so a session that
does its own reading and searching pays the orchestrator's rate for a
researcher's work and fills the one context window that has to stay clear.
The remedy is to sort work by the intelligence it actually needs: the session
keeps the judgment and delegates everything below it to a subagent whose model
matches the job.

## The tiers

Three tiers, each named for the intelligence the work demands rather than for
the job it happens to be.

| Tier | Model | What it is for |
|---|---|---|
| **Orchestrator** | `fable` | Owning the problem — holding the intent, forming falsifiable hypotheses, weighing the tradeoffs, and escalating to the human with specific questions and concrete examples. |
| **Limited intelligence** | `opus` | Small decisions with low ambiguity, and construction of small artifacts — mapping territory, research spikes, focused edits. |
| **No intelligence** | `sonnet` | Research and exploration that turns on no choices — reading an API, extracting information verbatim, summarizing what a source says. |

The line between the lower two rungs is whether the job requires a decision. A
job whose answer already sits in the sources and only has to be found and
reported belongs on the bottom rung. A job whose answer waits on a call
belongs on the middle one — and where that call is the human's, it goes back
up as a question rather than down as work.

## What stays at the top

The orchestrator delegates depth, never judgment. Intent, hypotheses, the
choice between options, and the escalation to the human stay with the session
that owns the problem. A subagent answers the question it is handed and never
decides which question was worth asking, so its report is evidence for the
orchestrator's call rather than the call itself.

## Dispatch

A tier is spawned through the `Agent` tool with its model pinned — `model:
opus` or `model: sonnet`. Independent jobs go out in a single message so they
run concurrently; a job that consumes another's result waits for it.

A subagent's tool output stays in its own context and only its final report
comes back, so delegation buys context as much as it buys cost. Two things
follow. The prompt carries everything the subagent needs, because it inherits
none of the dispatching session's conversation. And it asks for the
conclusion, not the material — the material is precisely what delegation
exists to keep out.
