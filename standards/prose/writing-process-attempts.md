---
type: General-Sheet
title: Writing Process Attempts
description: The record of attempts at a general document-writing process — what each tried and where it fell short
---

# Writing Process Attempts

The open problem: a long working conversation accumulates intent —
decisions, corrections, scope rulings — and one turn is then asked to
write the document, doing everything at once. Drafts written that way
carry the problems in
[writing-problems.md](/standards/prose/writing-problems.md). This sheet
records the attempts at a process fix, so the next attempt starts from
what is known.

## Attempts

- **Exhaustive on-screen classification.** Classify every significant
  piece of conversation information and report the full enumeration on
  screen. Found: the report is unverifiable by a human — twenty minutes
  of line-checking that will not happen — and the prompt reproduces the
  one-giant-turn disease at the extraction layer.
- **Three-checkpoint pipeline.** Classify, place, edit — user approval
  after each stage. Found: three checkpoints exceed what a user will
  genuinely review, so approvals decay into rubber stamps, and each
  checkpoint adds turns of context rot that degrade the writing it was
  meant to improve.
- **Two-attention-point process.** A spec mini-interview, an autonomous
  multi-agent write, then diff review in the IDE — user attention only
  at the ends. Tried once as a walkthrough; the interview itself
  produced a question the user could not follow, which decays into a
  rubber stamp. Neither adopted nor rejected.

## What the attempts established

- Work backwards from human verifiability. The user verifies short
  sentences in the terminal and edit diffs in the IDE. An exhaustive
  enumeration the user cannot check is meaningless to produce, whatever
  its accuracy.
- User attention is the most expensive resource in the loop. A turn
  that shows the user something must return real information — genuine
  approval, pushback, correction. A rubber-stamped checkpoint returns
  nothing and costs context rot.
- AI degrades when doing many things at once, and document writing is
  many things at once. Decompose into single-focus subagent tasks.
- Codified formats are followed once written, but rigid full
  specification cannot cover infinite scenarios — structure works as
  strong guidance plus flex, a menu of sections rather than a fixed
  list.
- Quantified back pressure — deterministic checks or scoring
  functions — helps small iterative adjustments converge.

## Considered, not wired in

A classification scheme for conversation content: every significant
item classified on three axes at once — kind (fact, decision, goal,
constraint, terminology, principle), status (settled, open, deferred),
and optional flags (corrected, excluded-from-doc). Built and audited
for overlap; no process uses it.

## Platform facts (Claude Code, researched 2026-08)

- A `fork`-type subagent inherits the full parent conversation and
  returns a result, and always runs on the parent session's model.
- Ordinary subagents and Workflow agents receive only the prompt they
  are passed, never conversation history.
- Full context on a different model exists outside the Agent tool:
  `claude -p --resume <session-id> --fork-session --model <model>`
  restores the full history, and the launch-time model wins over the
  restored one.
- A running interactive session has no first-class way to learn its own
  session ID; hooks receive it on stdin and can write it to a file the
  session reads back.
