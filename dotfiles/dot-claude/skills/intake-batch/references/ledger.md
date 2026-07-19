# The ledger, durable state, and user contact

Everything the run remembers and everything the user reads lives in two places. This
file defines both, and the protocol for talking to the user through them.

## State catalog — every fact has one home

- **`LEDGER.md`** (worktree root) — the distilled, user-facing report *and* the
  verbatim decision archive. The user's single reading surface. It holds the
  dashboard, the open asks, the delta log, and per-issue blocks. It summarizes
  evidence; it does not paste raw dumps.
- **`tmp/worker-returns/<id>.md`** — one file per worker, holding that worker's raw
  bulk evidence (a terrain map, a probe's counterexample and coverage statement, a
  prototype's answer). Written by the worker itself, not by you (see below).

The line between them: the ledger is what a user reads to steer; worker-returns is the
raw material you distilled that steer *from*. A hypothesis row in the ledger cites a
worker-return by id; it never re-types the return. Nothing is duplicated or orphaned.

**Commit both as events happen**, not batched at checkpoints — message
`intake-batch: <event>`. The branch never merges; the history is the point. Recovery
after `/clear` or compaction is "read `LEDGER.md`, resume from its stages."

## Worker returns write themselves

Each worker's leaf clause carves exactly one sanctioned write: the worker writes its
findings to `tmp/worker-returns/<id>.md` and returns only a one-line verdict plus that
path. You **read the file, verify, and commit it** — you never re-type a cheap model's
output into the ledger by hand. The single-writer invariant was always about the board
and the repo, not a scratch directory you own; the return is on disk the moment the
worker finishes, so a crash between return and checkpoint loses nothing.

## `LEDGER.md` structure

In this order — the top three sections are for the ten-second repeat scan; the per-issue
blocks are the archive underneath.

```markdown
# intake-batch ledger — <repo>

## Dashboard
| Issue | Stage | Verdict (short) | Waiting on |
|-------|-------|-----------------|------------|
| #208  | 🟡    | rename, scoped  | you — ask 1 |
| #199  | ✅    | impl-ready      | —          |

## Open asks
Every question currently waiting on the user, numbered, written out in full here —
one place. The dashboard's "Waiting on" column points into this list.
1. **#208 — …** <full-prose ask, see "Asks" below>

## Δ log
### Wave 2
- #208 · map returned: rename touches 14 files, no hook-id collision (M2)
- #199 · probe REFUTED the "spawn cap is enough" claim (P4)

## Issue <n> — <title>
stage: queued | investigating | blocked-on-user | ready-to-land | landed
verdict: <current verdict, at the user's altitude>

> ❓ **ASK** — <one sentence naming exactly what input you need> (see Open ask N)

### Hypotheses
| # | claim | status | evidence (one line, cite worker id) |
### Decisions (user, verbatim)
- "<quoted answer>" (<checkpoint>)
### Decided without the user
- <one line each — a silent call, cheaply vetoable>
### Probe log
- <tier> · <mission, one line> · <REFUTED|SURVIVED|BLOCKED> · <worker id>
```

- **Dashboard first** (one row per issue) so "where is input needed" is a glance, not a
  reread.
- **Δ log** carries one-liners of what changed per wave. Append to it *as events
  happen*; on a repeat pass the user reads only the newest wave. The issue blocks are
  the archive, not the scan surface.
- **The ASK line** is a loud blockquote on every issue block: `> ❓ **ASK** — …` when a
  real question waits (linking to its Open-asks entry), or `> ✅ **ASK** — none`
  otherwise. A bare sentence buried in prose fails — the user should never Ctrl-F for
  an ask.

## Asks are full prose, at the user's altitude

Two rules, both learned the hard way:

- **Spend words on the ask.** Compression belongs in the dashboard and Δ log. An ask the
  user must decide on gets full descriptive prose — the background, what the
  investigation established, the options spelled out **one per paragraph or bullet**,
  then your recommendation. Half a page is fine. A dense parenthetical-packed sentence
  reads as word salad and the user can't answer it.
- **Translate to the user's surfaces.** Phrase every verdict and ask in terms of what
  the user sees and owns — CLI behavior, gates, GitHub state, what changes for them —
  never black-box internals they neither wrote nor operate. Interior mechanics stay in
  the hypothesis table for audit; the verdict sentence and the ask must be parseable
  without interior knowledge.

## Checkpoint contact protocol

- **Never `AskUserQuestion`.** It blocks the terminal on questions the user isn't ready
  to answer and presupposes they've read the evidence. Instead: the ledger is the
  report; the user reads it and types prose feedback, issue by issue. You record each
  answer **verbatim** in that issue's Decisions section, then interpret.
- **Two beats.** Update and commit the ledger, then post a short terminal message that
  says only *what's new* and *what input is needed*, and stand by. The substance lives
  in the ledger, not the terminal.
- **Reading assignments at the end of the turn, never mid-flow.** Work quietly; anything
  the user must read goes into the ledger (the one reading surface) or, at most, a
  single consolidated note at the end of the turn. Never interleave content the user
  must read with work narration — it scrolls away and is never read.
