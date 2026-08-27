---
type: General-Sheet
title: Writing Improvement Process
description: The document-writing problem, the intention to improve it iteratively, and the capture step that records what goes wrong each time a document is written
---

# Writing Improvement Process

The problem: a long working conversation accumulates intent —
decisions, corrections, scope rulings — and one turn is then asked to
write the document, doing everything at once. Drafts written that way
carry the problems in
[writing-improvement-problems.md](/docs/writing-improvement-process/writing-improvement-problems.md). The
attempts below showed the problem is too large to fix in one stroke, so
the intention is iterative: capture what goes wrong every time a
document is written, watch the record for patterns, and build a
mechanism for each pattern once it is known.

## Capture

Every document-writing session ends with an entry in
[writing-improvement-log.md](/docs/writing-improvement-process/writing-improvement-log.md):
which document, what went wrong, and what fixed it. When the same
problem appears across entries, it graduates into
[writing-improvement-problems.md](/docs/writing-improvement-process/writing-improvement-problems.md)
as a named pattern; a countermeasure, once built, is linked from that
pattern's entry.

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
- **Classification primitives and dimensions.** A pre-defined structure
  for conversation content, built because pointing the AI at specific
  rules — use these primitives, use these dimensions — is how we build
  AI workflows.

  The first pass was nine flat primitives, one bucket per item:

  - decision
  - fact
  - goal
  - constraint
  - term
  - open question
  - deferral
  - correction
  - exclusion

  Found: further ambiguities — the primitives were fighting one
  another, there was no clear-cut answer, and it was left inconclusive.

## Principles

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
