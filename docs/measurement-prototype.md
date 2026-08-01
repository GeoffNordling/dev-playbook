---
type: Guide
title: Measurement Prototype
description: Initial exploration of the local hook-event store — what it contains, what can be derived from it today, and the assumptions that derivation rests on
---

# Measurement Prototype

Every Claude Code session on the primary machine appends its hook events to a
local SQLite store, raw and uninterpreted. This document records what is
actually in that store, what can be derived from it, and what cannot.

Everything here is either observed in the data or stated as an explicit
assumption. This document prescribes no metrics, mandates no report shape, and
declares no targets. An earlier draft did all three; it was written before
anyone had queried the store, and is deleted rather than carried forward.

## Goals

What we want from this data, in the order it matters:

1. **Utilization.** A continuous timeline of when Claude Code was working and
   when the human was at the machine. An actual timeline over real clock time,
   not long-run averages.
2. **Two levels.** Every number computed at either the session level or the
   global level, never ambiguously.
3. **Repository attribution.** Which repo a piece of work belonged to.
4. **GitHub issue attribution.** Which issue a piece of work belonged to.
5. **Skill attribution.** Which skills ran, and whether a human or an agent
   invoked them.
6. **File attribution.** Which files were read, written, and edited.

### Out of scope

Wanted eventually, not being built now. The design must not block them.

- **Per-issue managerial accounting** of cost and effort.
- **Which model produced a given turn.** The store records a model only on
  `SessionStart`, and switching model mid-session fires no event at all, so
  there is no path from the current data. Resolving it means experimenting with
  what the harness can be made to emit — separate work, not an analysis
  question.

## The store

The database is `~/.local/share/claude-measure/events.db` (SQLite, WAL), one
table, one row per hook invocation:

```sql
CREATE TABLE events (
    id          INTEGER PRIMARY KEY,   -- insertion order
    received_at TEXT,                  -- ISO-8601 UTC, microsecond precision
    event       TEXT,                  -- promoted from payload.hook_event_name
    session_id  TEXT,                  -- promoted
    prompt_id   TEXT,                  -- promoted
    payload     TEXT                   -- the harness's JSON
)
```

No indexes, no views, no triggers. Five of the six columns are handles for
querying; all content lives in `payload`. `event`, `session_id`, and `prompt_id`
are promoted copies kept as columns for convenience — `payload` is the authority
for every field, promoted or not. A promoted column is NULL whenever its key was
absent or arrived as something other than a string.

Scale at time of writing: ~11,000 rows, 61 sessions, 24 MB, spanning four days.

Which events reach the store is declared by the hook wiring in
[`dotfiles/settings/fedora.json`](/dotfiles/settings/fedora.json) — one
[`measure-event`](/dotfiles/dot-claude/hooks/measure-event) entry per hook, all
asynchronous. That wiring is the authority on the captured set; read it rather
than trusting a remembered list. Ten events are wired. Capture runs on the
primary machine only ([machines.md](/docs/machines.md)) and is forward-only from
the day the wiring merged — there is no backfill.

An `errors.log` may sit beside the database. A line in it is an event that
arrived and could not be recorded. Capture never fails a session, so a lost row
is silent at write time and this log is its only trace.

A reader opens the database read-only.

## What each event records

| Event | What it records | Fields that carry meaning |
|---|---|---|
| `SessionStart` | A session context beginning, including mid-session | `source` — one of `startup`, `resume`, `clear`, `compact`, `fork`. Only `startup` is a real start: a compaction fires this event inside the same `session_id`, while `clear` ends the old session id and mints a fresh one. `model` accompanies some sources but not all. |
| `SessionEnd` | A session context ending | `reason` — `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`. Not paired 1:1 with `SessionStart`. |
| `UserPromptSubmit` | A submission, with the literal typed text in `prompt` | Fires for typed prose, for skill slash commands, and for harness pseudo-prompts alike. |
| `UserPromptExpansion` | A typed command expanding, fired before its `UserPromptSubmit` and sharing its `prompt_id` | `command_name` and `command_args` — the human's own words, structured — plus `expansion_type`, `command_source`, and the full literal `prompt`. |
| `Stop` | The end of an agent turn | `prompt_id` pairs the turn with the submission that started it; `last_assistant_message` holds the full reply text. No `Stop` fires when a human interrupts with ESC. |
| `SubagentStart` | A subagent dispatch | `agent_id` — the key a real `SubagentStop` matches on. |
| `SubagentStop` | A subagent finishing, plus phantoms | `agent_id`; `agent_type` (empty on a phantom); `agent_transcript_path` — on a real stop the child transcript, on a phantom a well-formed path to nothing. |
| `PostToolUse` | An executed tool call, any tool | `tool_name` and `duration_ms`. A Bash row is byte-verbatim: `tool_input` holds the command line as it ran and `tool_response` its output. Every other tool loses `tool_response` at capture, and loses `tool_input` too unless it is `Read`, `Edit` or `Write` (which keep `file_path` alone) or `Skill` (which keeps `tool_input` whole). |
| `PostCompact` | A compaction | `trigger`, and the full `compact_summary` text. |
| `Notification` | A harness notification | `notification_type` — overwhelmingly `idle_prompt`, with occasional `permission_prompt` and `agent_needs_input`. |

There is no `PreToolUse`. Tool calls are recorded only after execution.

Every payload also carries `hook_event_name`, `session_id`, `transcript_path`,
and `cwd`.

## Identity facts

- **`prompt_id` is the join between a submission and its turn.** It appears on
  every event type, though not on every row: a `SessionStart` preceding any
  prompt has no `prompt_id`, and a `SessionEnd` fired by a UI builtin mints a
  fresh one matching no submission. Positional pairing of the Nth `Stop` with
  the Nth prompt is wrong, which shows up as sessions with more Stops than
  prompts.
- **`cwd` is per event, not per session.** A session moves between checkouts
  mid-flight, so anything keyed on a session-level cwd is wrong.
- **A subagent's tool events carry the parent's `session_id`** and
  `transcript_path`, but their own `agent_id` and `agent_type`. So a subagent's
  work is attributable through `agent_id`, and the *absence* of `agent_type`
  marks the parent's own work.

## Known blind spots

- **UI slash builtins** such as `/model`, `/compact`, and `/exit` fire neither
  `UserPromptSubmit` nor `UserPromptExpansion`.
- **ESC interrupts fire nothing at all.** An interrupted turn can still be
  detected after the fact — two submits with no `Stop` between them — but the
  interrupt itself leaves no event.
- Together these are roughly a fifth of human actions. Any count of human
  activity is a lower bound.
- **The hook stream outranks the transcript.** Resubmitting an edited prompt
  creates a sibling branch that the transcript's live path hides, so a
  transcript walk undercounts submissions by around 8 %. The human really did
  submit twice.

## Techniques for cleaning rows

Not mandates — the four adjustments a reader will generally want, and why.

| Technique | What it does | Why |
|---|---|---|
| Collapse expansion/submit pairs | Treat rows sharing a `prompt_id` as one submission; take `command_name`/`command_args` from the expansion and the literal text from the submit. | A skill slash command fires both. Counting both doubles every skill invocation. |
| Drop phantom `SubagentStop` | Drop rows with an empty `agent_type`, or with no `SubagentStart` in the same session matching on `agent_id`. | Hidden auxiliary model calls emit them. Each carries its own distinct `agent_id`, and its `agent_transcript_path` points at nothing on disk. |
| Drop task-notification pseudo-prompts | Drop submissions whose `prompt` begins with the `<task-notification>` marker. | Harness-generated, not human, but they do fire `UserPromptSubmit`. |
| Drop ghost sessions | Drop session ids with zero human submissions after the above. | `SessionStart` fires for session slots that never materialize. |

## The two levels

Every derived number is computed at one of two levels, and the level is never
implicit:

- **Session level** — one session id.
- **Global level** — all sessions unioned across the machine.

The same assumption can hold at both levels and mean different things, so each
one below names its level. Getting this wrong is the easiest way to produce a
confidently wrong number.

The two levels are the same interval table grouped differently, so they cannot
disagree. Session rows carry a session id; global rows are a union and carry
none. Because session rows keep their id, any later work that attributes a
session to an issue makes per-issue accounting fall out of the same table with
no change to the model.

## Utilization — the assumptions

### Definitive — facts in the data

| # | Assumption | Level |
|---|---|---|
| 1 | A submit proves the human was at the computer at that instant. | Both. Session: present in that session. Global: present at the machine. |
| 2 | Between a submit and its `Stop`, Claude Code was working. | Session. Global is the union of these intervals. |
| 3 | Outside a session's first and last event, that session does not exist. | Session. Globally, a moment is dormant only when every session is dormant. |
| 4 | Activity in any session proves the human is at the machine. | Global only. Meaningless at session level. |

Assumption 2 counts the model and its tools together. The distinction between
"the model is thinking" and "a tool is running" is not interesting here — both
are Claude Code working.

### Assumed — reasonable, not provable

| # | Assumption | Level |
|---|---|---|
| 5 | Two submits with no `Stop` between them means the human interrupted that turn. | Session. |
| 6 | A short gap after a `Stop` means the human was still there; a long gap means they left. | Both, with different thresholds. A gap that looks long in one session may be covered by work in another. |
| 7 | An `idle_prompt` notification means Claude was waiting with no response. | Session. Soft evidence of absence, and only if no other session was active. |

### Approximate — a probability, not a rule

| # | Assumption | Level |
|---|---|---|
| 8 | Each gap between a `Stop` and the next submit gets a probability that the human was present, fitted from the observed distribution rather than a hand-picked cutoff. | Session first, then rolled up. Globally, presence is the complement of all sessions being absent at once. |

The gap distribution is bimodal — a working mode of a couple of minutes and an
away mode of hours — so a two-component mixture gives a graded answer instead of
an arbitrary threshold. Fitted, those two modes are 1 m 13 s and 5 h 45 m, and
the crossover between them lands at 2 h 14 m rather than anywhere a person would
have picked; the fit is below.

### The asymmetry that shapes all of this

A submit is hard evidence of presence at an instant. **Nothing is hard evidence
of absence.** `Stop` proves only that Claude stopped; it says nothing about the
human. So presence is observed at points and inferred over intervals, and the
inference is a probability rather than a state.

### What these buy

- 1 and 2 give a hard timeline of Claude's working intervals with no inference.
- 3 lets the clock run continuously rather than only during sessions.
- 4 is the whole reason the global level exists: one active terminal proves
  presence while four others sit idle.
- 5 recovers turns that would otherwise look like they never ended.
- 6, 7 and 8 turn an unknown gap into a graded belief instead of a guess.

## Attribution

### Repository — definitive, available today

Every row carries `cwd`. 33 distinct values in the current store, all repo or
worktree paths. Repo attribution needs no capture change and no inference. It
resolves per row, never per session, because `cwd` moves mid-session.

The repo is the first path segment under `~/workspace`, which spares a worktree
a rule of its own: one sits at `<repo>/.claude/worktrees/<name>`, so it and every
subdirectory attribute to the repo they belong to. A cwd that is the workspace
root itself, or anywhere outside it, belongs to no repo. That is 27 rows of the
cleaned store, and a real state rather than a bad row — a session can start
anywhere.

### GitHub issue — approximate, available today

`gh` runs through Bash, and Bash is the one tool captured byte-verbatim, so
every `gh` command and its output is already stored. Two signals, of different
strength:

| Signal | Meaning | Strength |
|---|---|---|
| `gh issue edit / close / comment N` | The session changed that issue. | Strong. Evidence of work. |
| `gh issue view N` | The session looked at that issue. | Weak. Evidence of contact only. |

Measured coverage in the current store:

| | sessions bound | distinct issues |
|---|---|---|
| writes only | 15 | 25 |
| writes and reads | 23 | 38 |

That is 23 of the 55 sessions that ran any Bash. Reads roughly double coverage
and are far more frequent — 287 `gh issue view` calls against 73
`gh issue edit`. Thirteen issues are reachable only through a read.

**The two signals must stay separate.** One orchestrator session in the store
reads 25 different issues; it was not working 25 issues. Reads give coverage,
writes give intent, and averaging them into one number would mislead.

Recovery requires parsing shell text, so it is approximate by construction. A
session that worked an issue without running any `gh` command against it leaves
no trace, and a comment body quoting a `gh issue view` line leaves the trace of a
contact that never happened. `gh issue create` and `gh issue list` attribute
nothing at all: neither names a number on the command line, create's being in the
response.

An issue is recorded as `<repo>#<number>` rather than as a bare number, because
issue numbers collide across repos and a report keyed on `272` would merge two
repos' work into one. The repo is the invocation's own `--repo` where it carries
one — read within that invocation's own bounds, since one line can chain two `gh`
calls against different repos — and the row's own repo otherwise, with the owner
dropped from both so that the two forms name one issue.

### Skills — both paths, one of them forward-only

| Invocation | Visible? |
|---|---|
| Human types `/skill` | Fully, over the whole store. `UserPromptExpansion` carries `command_name` and `command_args`. 109 invocations, 13 distinct skills. |
| Agent calls the Skill tool | Since capture was extended: the row keeps `tool_input` whole, which names the skill. The 81 `Skill` rows written before that keep timing and calling agent alone. |

The asymmetry was backwards for a factory meant to run hands-off — the human's
own skill use fully measured and the agents' invisible — which is why capture
changed. It closes going forward; the older rows stay as they are.

### Files — forward-only

`Read`, `Edit` and `Write` rows keep `file_path` and nothing else: no content,
no diff, no offsets. Rows written before capture was extended carry no path at
all, and there is no backfill, so file attribution begins at the change rather
than at the store's first row.

### Cost — not in this store

No token counts and no cost anywhere. A separate database at
`~/.agentsview/sessions.db` holds `sessions`, `messages`, and `model_pricing`,
which would let cost be computed rather than read, joining on
`sessions.id = session_id` and rolling up through `parent_session_id`. Subagent
sessions are reachable from either side, since `SubagentStop`'s
`agent_transcript_path` equals agentsview's `sessions.file_path`. Nothing here
depends on it being present.

## The pipeline

Everything above is built, in [`src/dev_playbook/measure/`](/src/dev_playbook/measure/),
and one command runs it end to end:

```bash
uv sync --extra measure                  # pandas and plotly, once
uv run measure-timeline activity.html    # the whole store, one lane per session
```

`--since` and `--until` choose the window and are read as UTC, as the store
keeps it; either one left out falls back to the store's own edge. `--lane`
pivots the picture to `repo`, `issue_writes`, `issue_reads` or `skill` instead
of sessions, `--title` names the page, and `--db` reads a store somewhere else.
Nothing is written but the page: the store is opened read-only, and the interval
table is recomputed from it on every run rather than persisted, because the
derivation is still moving and a stale table would be believed.

The page is self-contained — plotly is inlined, so it is a few megabytes and
opens with no network.

Each run prints what the page cannot show: how many rows were read and how many
each cleaning removed, how many turns are still open, the fitted presence model,
and each state's totals at both levels, as wall clock and confidence-weighted.
Every figure quoted in this document comes from such a run; the store is live,
so a rerun moves them a little.

| Stage | Module | What it does |
|---|---|---|
| Load | [`measure/store.py`](/src/dev_playbook/measure/store.py) | The `events` table through a `mode=ro` URI into one tidy frame |
| Clean | [`measure/clean.py`](/src/dev_playbook/measure/clean.py) | The four techniques above, each reporting its own removed count |
| Attribute | [`measure/attribute.py`](/src/dev_playbook/measure/attribute.py) | `repo`, `issue_writes`, `issue_reads` and `skill` per event row |
| Definitive intervals | [`measure/intervals.py`](/src/dev_playbook/measure/intervals.py) | `claude_active`, `interrupted` and `dormant` rows at confidence 1.0 |
| Graded intervals | [`measure/presence.py`](/src/dev_playbook/measure/presence.py) | One `human_present` row per gap, at the fitted probability |
| Roll up | [`measure/rollup.py`](/src/dev_playbook/measure/rollup.py) | The same table across the machine, and the totals at either level |
| Draw | [`measure/timeline.py`](/src/dev_playbook/measure/timeline.py) | Lanes, gapped bars, confidence as opacity |
| Run | [`measure/cli.py`](/src/dev_playbook/measure/cli.py) | The window, the report, and the page |

### 1. Capture beyond Bash

The hook dropped `tool_input` and `tool_response` wholesale for non-Bash tools.
That was right for volume — `Read` responses carry whole files and `Edit` inputs
carry both sides of every diff — but it discarded cheap identifiers along with
the bulk. It now keeps the identifier and still drops the content:

- `Read`, `Edit`, `Write` — `file_path` alone.
- `Skill` — `tool_input` whole. It is a skill name and short arguments.

That unblocked file attribution and agent-invoked skill attribution at
negligible storage cost. Forward-only: existing rows stay as they are, so code
reading either field must treat its absence on an older row as a fact about
capture history rather than an error.

### 2. The interval table

One table: `start`, `end`, `state`, `session_id`, `confidence`. Every report and
both levels are a grouping of it.

It is computed in memory on each run rather than persisted. The derivation will
change as the assumptions are tuned, and a stale persisted table is worse than
none. The store is small enough that recomputing from scratch is free.

The rows that need no inference exist, in three states: `claude_active` for a
submit and the `Stop` carrying its `prompt_id` (assumption 2), `interrupted` for
a submit whose turn produced no `Stop`, closed at the next submit in that session
(assumption 5), and `dormant` for the window either side of a session's own
events (assumption 3). All three carry confidence 1.0.

Pairing is by `prompt_id` throughout, and the whole derivation is pandas over the
loaded frame — no SQL beyond the loader's single `SELECT`, since the payloads are
already parsed by the time any interval logic runs.

One caveat the numbers make sharp: an `interrupted` row's end is an upper bound,
not the interrupt instant, and summing it into Claude-active time is wrong. Its
median across the store is 29 seconds and its maximum 15.7 hours — an interrupt
before the human left for the night swallows the night. Tightening it needs the
fitting the next item gives a gap: after the interrupt, the two are the same
unobserved thing. That is not done.

The global level is that same table cut across the machine, not a second
derivation. Each state combines by its own rule: `claude_active`, `interrupted`
and `human_present` union, so a moment belongs to the machine if any session
claims it, while `dormant` intersects, since the machine is only dormant when
every session is — including the sessions that ran the whole window and so have
no dormant row of their own. Where graded rows overlap, their confidences
combine by complement, which is assumption 8's global form: presence is one
minus the chance every session was absent at once. That takes the sessions as
independent evidence about one human, so two terminals idle through the same
hour read as two chances the human was there rather than one absence. Global
rows carry no session id.

What the level costs is what overlapping sessions were double-counted below it.
Over the store's 99-hour window and 62 sessions, 14.6 session-hours of
Claude-active time are 12.6 hours of the machine's clock, and 35.9 expected
present session-hours are 25.5 expected hours globally; the machine is dormant —
no session in existence at all — for 11.5 of the 99. Wall clock only falls going
up a level, and expected presence falls with it, because a union charges one
moment once however many sessions were idle through it.

### 3. The presence mixture

A `Stop` with a submit next after it in the same session bounds a span nothing
observes. There are 533 of them over the store, 128 hours in total against 15
hours of Claude-active time, so how that silence is counted decides most of the
answer. Each gap becomes one `human_present` row whose confidence is the fitted
probability — the graded rows the interval table was given a `confidence` column
for. Gaps tile the session against the turns and never overlap them.

The model is two lognormal components over gap length, fitted by
expectation-maximization. Over the whole store:

| Mode | Share of gaps | Median gap |
|---|---|---|
| Working — read the reply, typed the next prompt | 98.3 % | 1 m 13 s |
| Away — came back later | 1.7 % | 5 h 45 m |

The shared log standard deviation is 1.61, which puts presence at even odds at
2 h 14 m, 0.85 at an hour and 0.006 at a day. Expected present time across the
128 gap hours is 36 hours.

**The two components share one variance, and that constraint is the point.**
Free variances fit better — log-likelihood -1030 against -1046 — but they split
the gaps into a narrow component over the bulk and a broad one over everything
else, and the shortest gaps in the store then belong to the *broad* component,
so a two-second gap reads as absence. A presence probability that is not
monotone in gap length is not a presence probability. Tying the variance makes
the posterior a logistic function of log gap length: monotone, with both the
crossover and its sharpness fitted. That is what assumption 8 promised — a
threshold taken from the data instead of picked.

Two properties of the fitting are worth knowing before trusting a number from
it. EM finds a local optimum, and on this store all but the widest start fall
into a valley where both means collapse onto the overall mean and the posterior
goes flat; the fit therefore runs several deterministic starts and keeps the
best-scoring one that converged. And the fit cannot decline: two modes are what
it looks for, so two modes are what it reports, over a window that was worked
straight through as readily as over one holding a night's sleep. The fitted
parameters travel with the rows they graded so a reader can see which they got.

## What remains

Nothing below blocks a run; each is a place the answer is weaker than it looks.

- **File attribution.** Capture keeps `file_path` on every `Read`, `Edit` and
  `Write` written since the change, and nothing reads it yet. It is the one goal
  above with no derivation behind it.
- **The `interrupted` upper bound.** An interrupted turn still ends at the next
  submit, which can be a night away. The tail after an interrupt is the same
  unobserved thing as a `Stop`-to-submit gap and could take the same fitted
  probability instead of being counted whole.
- **Presence at the global level is optimistic.** Sessions combine by
  complement, which reads two terminals idle through one hour as two chances the
  human was there rather than one absence. Correcting it needs a model of how
  sessions share a human, and the numbers are reported uncorrected until there
  is one.
- **Cost and which model did the work.** Both are out of scope above, and both
  would come from the agentsview join rather than from this store.
- **No backfill.** The forward-only fields — file paths, agent-invoked skills —
  begin at the capture change. Rows before it stay as they are.
- **One window at a time.** The command answers a question and writes a page; it
  is not a recurring device. Shipping it as one is a separate decision (see the
  instrument and skill references below).

## What this gives us

How long Claude Code worked. How long the human was at the machine. How much
those overlap. How many sessions ran at once. What a day looks like by hour.
Broken down by repository today, and by issue approximately.

## What it does not give us

Which model did the work. What anything cost. Which files changed, or which
skill an agent invoked, in any row written before capture was extended — both
start at that change, with no backfill behind it.

And it can never prove absence — only that nothing was observed.

## References

- [`dotfiles/dot-claude/hooks/measure-event`](/dotfiles/dot-claude/hooks/measure-event)
  — the capture hook. The trim rule lives in its `for_storage` and `kept_input`
  functions; this is the file that changes to extend capture again.
- [`dotfiles/settings/fedora.json`](/dotfiles/settings/fedora.json) — the hook
  wiring, and the authority on which events are captured.
- [Machines](/docs/machines.md) — capture runs on the primary machine only.
- [Instruments and Instrument Specs](/standards/instrument/format.md) — if this
  ships as a recurring device rather than a prototype.
- [Skill Conventions](/standards/claude-code/skill-conventions.md) — if it ships
  as a skill.
- [Python Style](/standards/python/style.md) and
  [Testing Conventions](/standards/testing/conventions.md) — for any code.
