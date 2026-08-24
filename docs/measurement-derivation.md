---
type: General-Sheet
title: Measurement Derivation
description: How raw captured hook events become measurements — the store, the assertions every report runs first, event semantics, filters, and metric formulas
---

# Measurement Derivation

Every Claude Code session on the primary machine appends its hook events to a
local SQLite store, raw and uninterpreted. This document turns that store into
numbers: what a report asserts before it computes anything, what each captured
event means, which rows it excludes and why, how hands-on minutes, waiting
latency, and interventions are computed, how a session binds to an issue, and
how cost is joined in. Each rule carries the issue that settled it, so a
reporting session derives from here rather than re-researching.

All interpretation happens at report time. Capture appends rows and does
nothing else beyond one mechanical trim (issue #255, rulings 16 and 23), which
is what makes a metric change a query change rather than lost data — and what
makes every rule below a query's obligation rather than a guarantee the store
meets.

## Standing and amendment

The rules here come from transcript research and live hook probes, not yet
from the capture store itself. Issue #270 re-validates every one of them
against live captured data — per-session event counts by type, each filter's
identifiability, the identity joins — and any mismatch amends this document,
with the underlying defect raised as a bug against capture.

## The store

The database is `~/.local/share/claude-measure/events.db` (SQLite, WAL). The
`events` table holds one row per hook invocation: `received_at` (UTC ISO-8601,
stamped when the hook received the event), `event`, `session_id`, `prompt_id`,
`payload`. `event`, `session_id`, and `prompt_id` are promoted copies of the
payload's `hook_event_name`, `session_id`, and `prompt_id`, kept as columns
for querying convenience; `payload` holds the harness's JSON byte-verbatim —
bar the single trim named under
[Event semantics](/docs/measurement-derivation.md#event-semantics) (#255,
ruling 23) — and is the authority for every field, promoted or not. A
promoted column is NULL whenever its key was absent or arrived as something
other than a string — including the whole-row case where stdin was not
parseable JSON at all. The sibling `ledger` table is the software factory's
run ledger — written and read only by `dev_playbook.factory.ledger` — and is
outside this document's scope.

Which events reach the store is declared by the hook wiring in
`/dotfiles/settings/fedora.json`, one [`measure-event`](/dotfiles/dot-claude/hooks/measure-event)
entry per hook, all asynchronous. That wiring is the authority on the captured
set: a report reads it rather than trusting a remembered list. Capture runs on
the primary machine only ([machines.md](/docs/machines.md)) and is
forward-only from the day the wiring merged — there is no backfill.

An `errors.log` sits beside the database. A line in it is an event that
arrived and could not be recorded. Capture never fails a session (#255, ruling
3), so a lost row is silent at write time and this log is the only trace of
it.

A report opens the database read-only.

## Assertions before any metric

A report asserts the store's shape before computing anything, and stops on the
first violation:

| Assertion | A violation means |
|---|---|
| Every `events` row has a non-NULL `event`. | The hook received something it could not parse as a JSON object; the raw text is in `payload`. |
| Every distinct `event` value appears in the hook wiring. | The captured set moved — a hook renamed upstream, or wiring changed — and rows exist that no rule here covers. |
| Every `events` row of a known event type carries the fields [Event semantics](/docs/measurement-derivation.md#event-semantics) names for that type. | A Claude Code release changed a payload shape, so a filter or formula reading that field is now reading nothing. |
| `errors.log` is absent or empty. | Events were lost; every count is a lower bound of unknown depth. |

**Fail-loud contract.** An assertion failure aborts the report and names the
event type, the offending row ids, and their count. It never drops, skips,
coerces, or defaults the offending rows, and never publishes a metric computed
over whatever remained. **A report that silently skips non-conforming rows is
a bug.** Capture stores payloads verbatim and never fails, so query time is
the only place payload drift can surface, and it surfaces only if queries
assert instead of filter — a number computed over "the rows that happened to
parse" is indistinguishable from a correct one and quietly wrong.

Exclusions under [Filters](/docs/measurement-derivation.md#filters) are the
opposite case, and the distinction carries the contract: a filter removes rows
this document names, for a rationale it states. Any other non-conforming row
is a stop.

## Event semantics

Every payload carries `hook_event_name`, `session_id`, `transcript_path`, and
`cwd`. `prompt_id` appears on every event type, not only the prompt-bearing
ones — but not on every row: a `SessionStart` that precedes any prompt
(`startup`, `clear`) has no `prompt_id` key at all, and a `SessionEnd` fired
by a UI builtin mints a fresh `prompt_id` that matches no submission (#270).
`cwd` is per event rather than per session — a
session moves between checkouts mid-flight and `gitBranch` moves with it — so
attribution never keys on a session-level cwd (#266). `prompt_id` is the exact
join between a submission and the events of the turn it started; positional
pairing of the Nth `Stop` with the Nth prompt is wrong in every session
studied, which shows up as sessions with more Stops than prompts (#266).

The fields named per event below are the ones the filters and formulas read,
so their presence in a payload of that type is exactly what the third
assertion checks.

| Event | What it records | Fields that carry meaning |
|---|---|---|
| `SessionStart` | A session context beginning, including mid-session | `source` — one of `startup`, `resume`, `clear`, `compact`, `fork`. Only `startup` is a real start: a compaction fires this event inside the same `session_id`, while `clear` ends the old session id and mints a fresh one. `model` accompanies some sources but not `clear`, so only `source` is asserted (#270). |
| `SessionEnd` | A session context ending | `reason` — `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`. Not paired 1:1 with `SessionStart`: closing the agent view emitted it for session ids that never emitted a start. |
| `UserPromptSubmit` | A submission, with the literal typed text in `prompt` | Fires for typed prose, for skill slash commands, and for harness pseudo-prompts alike — the last two are separated by the filters below. |
| `UserPromptExpansion` | A typed command expanding, fired before its `UserPromptSubmit` and sharing its `prompt_id` | `command_name` and `command_args` — the user's own words, structured, when a skill is invoked with prose arguments — plus `expansion_type`, `command_source`, and the full literal `prompt`. |
| `Stop` | The end of an agent turn | `prompt_id` pairs the turn with the submission that started it. No `Stop` fires when a user interrupts with ESC; the turn simply ends. |
| `SubagentStart` | A subagent dispatch — the dispatch signal | `agent_id` — the key a real `SubagentStop` matches on. Dispatches are counted here, never at `SubagentStop`. |
| `SubagentStop` | A subagent finishing, plus phantoms | `agent_id`, which matches the stop to its `SubagentStart`; `agent_type` (empty on a phantom); and `agent_transcript_path` — on a real stop the child transcript outright, on a phantom a well-formed path to nothing, so any reader handles non-existence (#270). |
| `PostToolUse` | An executed tool call, any tool | `tool_name` and `duration_ms` on every row. A Bash row is byte-verbatim: `tool_input` holds the command line as it ran — the source of phase transitions and session-to-issue binding — and `tool_response` its output. Every other tool's row is the envelope alone, with `tool_input` and `tool_response` dropped at capture and so deliberately absent — the one exception to byte-verbatim payloads (#255, ruling 23). The third assertion therefore expects `tool_input` on Bash rows only; on the rest, `tool_name` and `duration_ms` are the fields that carry meaning. |
| `PostCompact` | A compaction — the context-pressure signal | — |
| `Notification` | A harness notification, including the permission-request and waiting-on-user moments the bell announces | Unverified: capture of this event begins with the wiring that added it (#255, ruling 23), so no field is named here — and none asserted — until real payloads are read. |

Identity facts constrain all of the above. A subagent's own tool events
carry the **parent** session's `session_id` and `transcript_path` (#258) —
but also their own `agent_id` and `agent_type`, so a subagent's tool work is
directly attributable to it by `agent_id` (#270). And `agent_type` on a
payload marks subagent work, not the agent view: ordinary interactive
sessions carry it on every subagent-issued event, and its absence marks the
parent's own work (#270, overriding #258's agent-view reading).

## Filters

Exclusions apply to conforming rows before any metric is computed:

| Filter | Rule | Why |
|---|---|---|
| Expansion/submit pairs | Collapse rows sharing a `prompt_id` into one user submission; take `command_name`/`command_args` from the expansion and the literal text from the submit. | A skill slash command fires `UserPromptExpansion` then `UserPromptSubmit` with the same `prompt_id`. Both describe one act, and counting both doubles every skill invocation (#258). |
| Phantom `SubagentStop` | Drop rows with an empty `agent_type` or with no `SubagentStart` in the same session matching on `agent_id`. | Hidden auxiliary model calls emit them (#258). Each phantom carries its own distinct `agent_id` — they are not repeat firings of real subagents — and the drop is verifiable: a phantom's `agent_id` is absent from agentsview and its `agent_transcript_path` points at nothing on disk (#270). |
| Task-notification pseudo-prompts | Drop submissions whose `prompt` begins with the `<task-notification>` marker. | Harness-generated, not user, and they do fire `UserPromptSubmit` (#258). |
| Ghost sessions | Drop session ids with zero user submissions after the filters above. | `SessionStart` fires for session slots that never materialize — no transcript is ever written, and `SessionEnd` follows on close (#258). |

**Known blind spots.** UI slash builtins such as `/model`, `/compact`, and
`/exit` fire neither `UserPromptSubmit` nor `UserPromptExpansion`, and ESC
interrupts fire nothing at all. Together they are roughly a fifth of user
actions, all of it low-signal (#258). Skill commands and the prose inside
their arguments are fully captured. A report states this blind spot rather
than presenting counts as complete; interrupts are the one intervention
signal with no capture path.

**The hook stream outranks the transcript.** Resubmitting an edited prompt
creates a sibling branch that the transcript's live path hides, so a
transcript walk undercounts submissions by around 8 % against the hook stream.
The user submitted twice — two interventions, two attention windows — so the
hook stream is the accurate source and is never reconciled toward the
transcript (#266).

## Metrics

Definitions, caps, and censoring below are the settled recommendations of the
metric-definitions study (#266); the targets they feed are declared in
[telemetry.md](~/workspace/mission-control/telemetry.md).

### Hands-on minutes

```
hands_on_seconds(work item) =
    Σ over user submissions s in the work item:
        min( t(s) − boundary_before(s),  180 )

boundary_before(s) = the latest Stop or SessionStart event of the same session,
                     strictly before t(s)
```

A user submission is one deduplicated row from the filters above, so a skill
invocation counts once.

Uncapped, the metric spans 34× between its 10th and 90th percentile across
sessions; at 180 s it spans 2.7×, and no amount of overnight idling,
resumption, or weekend can inflate it. The value 180 s is Claude Code's own
away threshold, the modal lag of 876 measured `away_summary` firings. The
metric charges the user for no agent time, needs only hook events, and
degrades gracefully — a missing `Stop` after an interrupt, or a late
timestamp on a queued prompt, costs at most one 180 s window instead of
corrupting the session.

Published beside it as a sanity check: submissions × 1.7 min. A divergence
beyond about 2× on one work item means something is odd about that item, and
is investigated rather than smoothed.

Cap sensitivity, if 180 s ever proves too tight: 300 s raises every session by
about 35 % and loosens stability (CV 0.32 → 0.39); 120 s is the most stable
but collapses toward a plain submission count; 600 s leaks away-time back in
and is rejected.

A queued prompt's `UserPromptSubmit` may fire at dequeue rather than at the
moment enter was pressed, which lets its window absorb some agent working
time. Queued prompts are rare, the cap bounds the error to one window, and no
correction would be possible even with the timing known — so the bias is
documented here and deliberately not investigated (#255, ruling 21).

### Waiting-on-user latency

```
gaps = { t(s) − t(prev Stop) : for each user submission s }

report:  median and p90 over gaps ≤ 14400 s
         plus the count and total duration of gaps > 14400 s, separately, as away time
```

The raw distribution is bimodal — a working mode near two minutes and an away
mode of hours — so a single statistic over both describes neither. Censoring
at four hours retains 98.7 % of observations, leaves the median unmoved (112 s
→ 110 s), and stabilizes the p90 (1005 s → 811 s). Four hours also separates a
long lunch from an overnight resumption cleanly: the shortest observed
overnight gap is 6.6 h, and the one-to-four-hour band is 2.6 % of gaps. The
censored gaps are reported as away time, never discarded. `prev Stop` is the
chronological predecessor — the latest `Stop` of the same session strictly
before t(s). Pairing by `prompt_id` is wrong here: a `Stop` shares its
`prompt_id` with the submission that started its turn, so that join measures
the agent's turn duration, not the user's waiting (#270).

### Interventions per issue

Interventions are the user submissions in the session bound to the issue,
beyond the launch prompt that started the overwatch (#255). The count is a
lower bound, since ESC interrupts leave no event; the target is zero, so any
nonzero count is real regardless.

## Session-to-issue binding

A session binds to an issue through executed commands, not prose. A Bash
`PostToolUse` row whose `tool_input` holds a `gh issue edit <N> … phase:*`
command is deterministic evidence that a phase moved for issue `<N>` in that
session (#255, ruling 2). A command that never ran records nothing, and
GitHub's own issue timeline stays the corroborating record.

The session tree carries attribution: subagent sessions attach to their
parent through `SubagentStart`/`SubagentStop` in the hook stream and through
`parent_session_id` in agentsview. `cwd` and git branch corroborate and never
decide (#255, ruling 5) — the traverse that motivated this rule ran its
overwatch from the main checkout on `main` while its nodes worked in
worktrees.

Sessions and work items are different units, so binding resolves per event.
`/clear` ends one session and starts another mid-work-item, a compaction fires
`SessionStart` inside one session, and a single session can touch several
issues.

The binding grammar is a coupling point: it holds only while phase labels keep
moving through executed `gh issue edit` commands (#255, ruling 13). Tests
pinning those command shapes land when measurement consolidates with the
skills sweep (#255, ruling 19). A session that plainly worked an issue but
carries no binding command is reported as an unbound session, never guessed
into place.

## Cost enrichment

Cost joins in at report time from agentsview, opened read-only as
`file:…?mode=ro` (#259): match agentsview `sessions` on `id = session_id`,
roll the tree up through
`sessions.parent_session_id`, and price `messages.token_usage` against
`model_pricing`. Cost is computed, never read — `usage_events` holds nothing.
Subagent sessions are reachable from either side, since `SubagentStop`'s
`agent_transcript_path` equals agentsview's `sessions.file_path` and that
path's filename stem is the agentsview session id.

Enrichment is the one input whose absence is not an assertion failure. Capture
never depends on agentsview (#255, ruling 8), so when agentsview is
unavailable the cost columns read "unavailable" and every other metric still
reports in full.
