# intake-batch — lessons learned (first run, 2026-07-18)

Observations about the skill itself, recorded as they surface. Batch: issues
208, 207, 199, 184, 183, 169.

## 1. Checkpoint asks land before the human has read the ledger

At checkpoint 1 the orchestrator posted the report and immediately raised
`AskUserQuestion` with four decisions. The human felt overwhelmed: the
questions presuppose familiarity with evidence that lives in the ledger (and
in the long checkpoint report), which they had not read yet. The tool blocks
the terminal on questions the human isn't ready to answer.

Unresolved — candidate directions, none chosen:

- **Human-behavior fix:** the human reads the ledger first, then returns to
  the terminal where the questions are waiting. No skill change; requires the
  habit.
- **Skill-sequencing fix:** checkpoint contact becomes two-beat — post the
  report, end the turn with "say ready for the asks," and only raise
  `AskUserQuestion` after the human signals they've read enough.
- **Report-altitude fix:** make each question fully self-contained (restate
  the evidence inside the question/options) so the ledger is background, not
  prerequisite reading.

RESOLVED by lesson 2: the human chose the report-and-feedback flow. The
ledger becomes the report; typed per-issue feedback replaces question-pulling.

## 2. The ledger IS the report; feedback replaces AskUserQuestion

What actually happened at checkpoint 1: the human read the ledger and found
it natural to type feedback issue-by-issue, unprompted. That is the protocol:

- The orchestrator writes the ledger so it reads as a **self-contained
  report** — a human who reads only the ledger can respond to every open
  point without the terminal transcript.
- The human reads it and **types feedback per issue**.
- **Do not use `AskUserQuestion`** to pull answers. Decisions arrive as prose;
  the orchestrator records them verbatim and interprets.

Skill modification (later): rewrite the "Checkpoint report format" section —
the four-part terminal report and the AskUserQuestion step go away; instead
the checkpoint = "ledger updated + committed, terminal message says what's
new and what input is needed, then stand by."

Corollary: each issue block needs an explicit **ASK line** — one sentence
stating exactly what input (if any) is needed from the human. At checkpoint 1
the human read #199's block and couldn't tell what was being asked of them.

## 3. The ledger must support repeated scanning — deltas, not rereads

By wave 2 the human couldn't scan the ledger anymore: "I don't know what
changed and what didn't. It's all quite black and white with minimal
formatting and difficult to read" when diffing mentally against the version
read ten minutes earlier.

Fix applied mid-run (bake into the skill's ledger format later):

- **Dashboard table first** — one row per issue: stage glyph (✅/🟡), short
  verdict, "waiting on" column. Ten-second read of where input is needed.
- **Δ log second** — per wave, one-liners of what changed. On a repeat pass
  the human reads only the newest Δ section; issue blocks stay the archive.
- **"Open asks" section directly under the dashboard** — every question
  currently waiting on the human, written out in full, numbered, in ONE
  place. The dashboard's "waiting on" column flags who's blocking; this
  section holds the actual questions.
- **ASK per issue block** — a visually loud blockquote (`> ❓ **ASK** — …`)
  linking up to the Open-asks entry when a real question exists; a plain
  "ASK: none" line otherwise. A bare sentence buried in prose fails — the
  human had to Ctrl-F to find asks.
- Discipline: every ledger update also appends its one-liner to the current
  wave's Δ section — the Δ log is written as events happen, not reconstructed.

## 4. Reading assignments at the end only — never mid-flow

Sequence that failed: the orchestrator dumped the #199 proposal into the
terminal, followed it with ledger edits and commits, then closed wave 2, then
handled an unrelated complaint. The human never read the proposal — it sat in
the middle of a flowing work stream, scrolled away by later turns.

Rule for the skill: substantive content the human must read is never
interleaved with work narration. Work quietly; whatever needs the human's
eyes goes at the END of the turn (or, better, into the ledger — which is the
one reading surface, per lesson 2) as a single consolidated reading
assignment. A mid-stream terminal message is a status note, nothing more.

## 5. Translate to the human's altitude — no black-box internals

The human bounced off #184's block ("complaining about a problem inside a
black box"): the hypothesis table talked rule-matrix/Direction-2/citation
mechanics — implementation interior the human neither wrote nor operates.
Their mental model of judgements is exterior: "CLI operation that checks the
judgements all pass or are cached as passing."

Skill modification (later): verdict + ask lines must be phrased at the
human's surfaces (CLI behavior, gates, GitHub state, what changes for them).
Interior evidence stays in the hypothesis table for audit, but the verdict
sentence and the ask must never require interior knowledge to parse.
