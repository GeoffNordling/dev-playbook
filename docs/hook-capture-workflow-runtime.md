---
type: Survey
title: Hook capture under the Workflow runtime
description: Whether the measure-event store sees workflow-spawned agents, what it can and cannot attribute to an issue, and what shape the supplemental attribution record should take
---

# Hook capture under the Workflow runtime

Three questions from [dev-playbook#333](https://github.com/GeoffNordling/dev-playbook/issues/333):
does the hook-event store capture agents a Workflow script spawns; what shape a
supplemental store for issue and epic attribution should take; and whether the
factory should emit explicit binding records or leave attribution to be inferred
from captured commands.

Job 1 is settled empirically against rows already in the store — the 2026-08-03
probe traverses from [#324](https://github.com/GeoffNordling/dev-playbook/issues/324),
[#325](https://github.com/GeoffNordling/dev-playbook/issues/325) and
[#328](https://github.com/GeoffNordling/dev-playbook/issues/328) ran on this
machine and their rows are captured. Jobs 2 and 3 are recommendations resting on
what Job 1 found.

**Citation key.** `[db: <query summary>]` — read out of
`~/.local/share/claude-measure/events.db` opened `mode=ro` on 2026-08-04, when
the store held 15,631 rows over 2026-07-28 → 2026-08-04. `[file: <path>]` — read
in this repo. `[#N: <where>]` — recorded on that issue. `[disk: <path>]` — read
off the machine's filesystem outside the store.

Prototype input is `docs/measurement-prototype.md` on the `issue-272-design`
branch ([#272](https://github.com/GeoffNordling/dev-playbook/issues/272),
canceled). Main's `measurement-derivation.md` is outdated and is not cited here.

## What capture actually is

Ten hooks are wired, every one asynchronous, every one running the same script
[file: `dotfiles/settings/fedora.json`]: `SessionStart`, `SessionEnd`,
`UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStart`,
`SubagentStop`, `PostToolUse` (matcher `*`), `PostCompact`, `Notification`.

The script appends one row per invocation and interprets nothing
[file: `dotfiles/dot-claude/hooks/measure-event`]. Table:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY, received_at TEXT, event TEXT,
    session_id TEXT, prompt_id TEXT, payload TEXT
)
```

`hook_event_name`, `session_id` and `prompt_id` are promoted to columns; every
other field stays in `payload` only. One trim happens at write time: a
`PostToolUse` whose `tool_name` is not `Bash` loses `tool_input` and
`tool_response` before storage.

**The trim is wider than the prototype doc says.** That doc describes capture as
extended — `file_path` kept on `Read`/`Edit`/`Write`, `tool_input` kept whole for
`Skill`. That extension exists only on the `issue-272-design` branch (its hook
has `kept_input()` and `KEPT_INPUT_KEYS`), was never merged, and is not deployed:
`/home/geoff/.claude/hooks/measure-event` is byte-identical to main's copy
[disk: `diff` of the two, no output], and the store holds **zero** non-Bash
`PostToolUse` rows carrying `tool_input` [db: 6,469 Bash rows have both
`tool_input` and `tool_response`; all 3,914 non-Bash rows have neither].

So today, **Bash is the only tool whose content is captured at all.** Every
`Skill`, `Agent`, `Workflow`, `Read`, `Edit` and `Write` row is an envelope:
`tool_name`, `duration_ms`, identity fields, nothing else.

## Job 1 — capture holds under the Workflow runtime

**Verdict: capture holds, and workflow rows are distinguishable — but the
workflow `runId` reaches the store on exactly one event type, and the traverse's
own arguments and return value never reach it at all.**

### Workflow agents fire the full hook set

The store holds `workflow-subagent` rows from 2026-07-30 onward
[db: agent_type by day]:

| Event | `workflow-subagent` rows |
|---|---|
| `SubagentStart` | 176 |
| `SubagentStop` | 164 |
| `PostToolUse` | 1,514 |

Two complete probe traverses from 2026-08-03 are captured end to end
[db: rows whose `agent_id` maps to each run]:

| Run | Agents | Rows | Events | Window (UTC) |
|---|---|---|---|---|
| `wf_65272d91-9a5` (#324 run 1, escalated) | 6 | 33 | 6 Start / 21 PostToolUse / 6 Stop | 18:06:35 → 18:13:23 |
| `wf_82f710cd-3fa` (#324 run 2, DONE) | 4 | 24 | 4 Start / 16 PostToolUse / 4 Stop | 18:14:27 → 18:17:32 |

Every row of both runs carries `session_id =
013a8d6a-6664-43b6-a3e9-0fd97cf3b650` — the launching interactive session. There
is no separate session id for a workflow run.

A single fenced node's lifecycle, verbatim from the store, is the shape in
miniature [db: rows with `cwd LIKE '%/worktrees/wf_%'`]:

```
18:12:51  SubagentStart  013a8d6a  workflow-subagent  a04d89c8f4b2b4691  cwd=.../worktrees/wf_65272d91-9a5-6
18:12:56  PostToolUse    013a8d6a  workflow-subagent  a04d89c8f4b2b4691  Bash
18:13:01  PostToolUse    013a8d6a  workflow-subagent  a04d89c8f4b2b4691  Bash
   … four more Bash rows …
18:13:23  PostToolUse    013a8d6a  workflow-subagent  a04d89c8f4b2b4691  StructuredOutput
18:13:23  SubagentStop   013a8d6a  workflow-subagent  a04d89c8f4b2b4691  cwd=.../worktrees/wf_65272d91-9a5-6
```

### `agent_id` and `agent_type` are present, and `agent_type` is the discriminator

Every `SubagentStart`, `SubagentStop` and agent-issued `PostToolUse` row carries
both fields [db: payload-key census — `agent_id` and `agent_type` on 326/326
`SubagentStart` and 1,925/1,925 `SubagentStop`]. The distinct `agent_type` values
across the store:

| `agent_type` | Where it comes from |
|---|---|
| `workflow-subagent` | a workflow `agent()` call with no explicit type |
| `gate-probe-node`, `fence-probe` | a workflow `agent()` call naming an agent definition |
| `general-purpose`, `Explore`, `claude`, `fork`, `claude-code-guide` | Agent-tool spawns |
| `""` (empty) | phantom `SubagentStop` — see below |

**A workflow node's declared agent type reaches the hook payload.** The
`gate-probe-node` rows were spawned by a workflow node written
`agentType: 'gate-probe-node'` [#324: the commit-gate probe matrix, row T2, and
the preserved `agents/gate-probe-node.md`], and their `SubagentStop`'s
`agent_transcript_path` sits under `workflows/wf_708b3f8f-889/` — a workflow
agent whose captured type is its definition name, not `workflow-subagent`. This
is the single cheapest lever the factory has: **name each traverse node's agent
definition and the node name lands in the store for free, on every row that node
produces.**

### The `runId` reaches the store on `SubagentStop` only

`SubagentStop` carries `agent_transcript_path`, and the workflow `runId` is a
path segment in it:

```
Agent-tool subagent:
  …/projects/<project>/<session-uuid>/subagents/agent-<agent_id>.jsonl
Workflow agent:
  …/projects/<project>/<session-uuid>/subagents/workflows/wf_<runId>/agent-<agent_id>.jsonl
```

166 rows carry a `runId` this way [db: regex over `agent_transcript_path`]. That
is the whole supply. `SubagentStart` has no `agent_transcript_path` at all [db:
its seven payload keys are `session_id`, `transcript_path`, `cwd`, `prompt_id`,
`agent_id`, `agent_type`, `hook_event_name`], and a `PostToolUse` row's
`transcript_path` is always the **launching session's** transcript, never the
agent's [db: no `PostToolUse` row's `transcript_path` contains `workflows/` or
`/subagents/`].

So a workflow `PostToolUse` row reaches its `runId` only by joining
`agent_id → SubagentStop.agent_transcript_path`. That join covers 1,482 of 1,530
workflow `PostToolUse` rows (96.9 %); 48 rows over 13 `agent_id`s are orphaned
because their agent never produced a captured `SubagentStop` [db: bridge test].
**An agent that dies, is killed, or whose stop hook is lost takes its whole
`runId` attribution with it.**

### `cwd` attribution holds, and the worktree name carries the `runId`

`cwd` is per event and correct on every row. 59 distinct values in the store; the
harness-made worktrees appear by their own names [db: distinct `cwd`]:

- Workflow isolation worktrees: `…/dev-playbook/.claude/worktrees/wf_<runId>-<n>`
  — e.g. `wf_65272d91-9a5-2`, `-4`, `-6`, matching the `-<agentNo>` numbering
  ruled on [#324: probe fact 5].
- Agent-tool `isolation: worktree`: `…/.claude/worktrees/agent-<agent_id>` —
  e.g. `agent-a131e7e9fec2195d0`, 138 rows.

For a fenced workflow node, therefore, `cwd` alone recovers the `runId` without
touching `SubagentStop`. For an unfenced one it does not: those rows carry the
launching session's `cwd`. In run `wf_65272d91-9a5`, 21 of 33 rows sit in a
`wf_`-named worktree and 12 sit at `/home/geoff/workspace/dev-playbook`.

Nothing about worktrees breaks repo attribution — a workflow worktree lives under
`<repo>/.claude/worktrees/`, so the prototype doc's rule (first path segment
under `~/workspace`) resolves it to `dev-playbook` unchanged.

### What the store cannot see

- **The traverse's arguments.** All 60 `Workflow` `PostToolUse` rows are
  envelopes — ten keys, no `tool_input` [db: key census on `tool_name='Workflow'`].
  The issue number the manager passed to `traverse.js` is nowhere in the store.
- **The traverse's outcome.** Same rows, no `tool_response`. `outcome: DONE`, the
  ESCALATE payload, the thrown-error text — none of it is captured. The
  three-lane error contract ruled on [#328] is invisible to measurement.
- **Which skill an agent invoked.** 109 `Skill` rows, zero with `tool_input`.
- **Which files were touched.** 1,649 `Read`, 1,255 `Edit`, 311 `Write` rows,
  none with a `file_path`.
- **The nested judgments run's parentage.** A nested `workflow()` gets its own
  `runId`; nothing in the store links it to the traverse that called it.

### Two hazards a reader must handle

**Phantom `SubagentStop` is the dominant row shape.** 1,633 of 1,925
`SubagentStop` rows carry `agent_type = ''`, an `agent_id` that appears in no
other row in the store, and an `agent_transcript_path` that does not exist on
disk. Exactly the 285 `agent_id`s that also have a `SubagentStart` carry a real
`agent_type`; the 1,634 that do not are all empty [db: cross-tab]. The prototype
doc already names these phantoms and prescribes dropping them.

This survey can say what they are, which the prototype doc could not. Reading the
store *from inside a running subagent*, the three most recent phantoms under this
session's id carried `last_assistant_message` values of
`"Sequencing SubagentStop rows in events.db"`,
`"Grouping empty vs typed agent_type per session"` and
`"Comparing SubagentStart/Stop rows in events.db"` — this agent's own tool-call
descriptions, one per turn, arriving in turn order [db: `SubagentStop` rows for
session `c7fd4a3d…` on 2026-08-04]. **A phantom is a subagent's per-turn stop,
minted with a throwaway `agent_id`.** The single typed row is the agent's actual
completion. The ratio follows: 1,633 / 296 ≈ 5.5 turns per agent. Any count of
agents that does not drop phantoms overcounts by roughly six-fold, and any
per-agent duration computed from the phantom's timestamps measures a turn.

**`prompt_id` is not a run key.** Run `wf_65272d91-9a5`'s 33 rows span two
`prompt_id`s, because the manager submitted another prompt while the run was in
flight; run `wf_82f710cd-3fa`'s 24 rows span one. 1,495 of 1,514 workflow
`PostToolUse` rows carry a `prompt_id` matching a captured `UserPromptSubmit`,
but the match points at *whatever the human last typed*, not at the launch.

### Job 1 summary table

| Question from #333 | Answer | Evidence |
|---|---|---|
| Do workflow agents fire `SubagentStart`/`SubagentStop`/`PostToolUse`? | Yes, all three | 176 / 164 / 1,514 rows |
| Do rows carry `agent_id` and `agent_type`? | Yes, on 100 % of subagent rows | payload-key census |
| Is the type `workflow-subagent`? | For default-type nodes, yes; a node naming an agent definition reports that name | `gate-probe-node`, `fence-probe` |
| Under the launching session's `session_id`? | Yes, always; no separate session id exists | both 08-03 runs, one `session_id` |
| Does per-event `cwd` hold in harness-made worktrees? | Yes — `wf_<runId>-<n>` for workflow, `agent-<id>` for Agent-tool | distinct-`cwd` census |
| Are workflow rows distinguishable from Agent-tool rows? | Yes, two independent ways | `agent_type`, and `workflows/` in `SubagentStop.agent_transcript_path` |
| Does the `runId` reach the store? | On `SubagentStop` only, plus in fenced nodes' `cwd`; 96.9 % bridgeable to `PostToolUse` | bridge test |

## Job 2 — supplemental store shape

**Recommendation: a new table in the same database, keyed on `agent_id` first and
`session_id` + a time window second. Not added columns; not a separate database.**

### Against added columns on `events`

An added column has to be filled by the writer, and the writer is `measure-event`
— which sees one hook payload and nothing else. It cannot know an issue number:
Job 1 established that the issue reaches the store only as text inside a Bash
command, at whatever moment some agent happens to run one. Filling an
`issue` column would mean the capture hook parsing shell text at write time,
which is exactly the interpretation the contract forbids ("capture appends raw
and never interprets", #333 constraints; the hook's own docstring calls storage
"append-only and uninterpreted").

A nullable column filled by a *second* writer is worse: it makes every binding
record an `UPDATE` against rows another process is appending to, under a 5-second
busy timeout, on a store that took 15,631 rows in seven days. Capture must never
fail a session, and update contention is the one way a supplemental write can
make it fail.

### Against a separate database

The whole reason to store binding records is to join them to hook rows. Two
SQLite files means either `ATTACH` on every read or two frames merged in pandas —
a cost paid on every query, forever, to avoid a cost paid once. It also splits
the retention story: nothing then guarantees the binding record and the rows it
binds are pruned together.

The argument *for* a separate database is write isolation, and it is real. But
WAL already gives one writer and many readers concurrently, and the binding
writer is low-rate by construction — a handful of rows per traverse against
thousands of hook rows. Contention between one append-only writer and another
append-only writer on separate tables in a WAL database is not a live risk at
this volume.

### For a new table in the same database

```sql
CREATE TABLE IF NOT EXISTS bindings (
    id INTEGER PRIMARY KEY,
    received_at TEXT,     -- when the record was written, hook-store format
    kind TEXT,            -- what the record asserts; readers switch on this
    session_id TEXT,      -- the launching session, as hook rows carry it
    run_id TEXT,          -- wf_<runId>, or NULL outside a workflow
    agent_id TEXT,        -- the emitting agent, or NULL
    payload TEXT          -- the record's own JSON, uninterpreted
);
```

The shape deliberately mirrors `events`: promoted handles plus one opaque
`payload`, so the same contract holds on both sides — the emitter appends raw,
the reader interprets. Adding it does not disturb capture: the hook's
`CREATE TABLE IF NOT EXISTS events` is a no-op against a database with extra
tables, and its `INSERT` names its columns explicitly.

Join keys, in the order a reader should try them, each grounded in Job 1:

1. **`agent_id`** — the strongest. Present on 100 % of subagent rows, unique, and
   already the bridge that carries `runId` from `SubagentStop` to `PostToolUse`.
   An emitting node binds its own `agent_id`, and every row that node produced is
   attributed exactly.
2. **`run_id`** — binds a whole traverse. Recoverable from the store on
   `SubagentStop` (166 rows) and from fenced nodes' `cwd`, so a `run_id`-keyed
   record attributes the 96.9 % of workflow rows the bridge reaches.
3. **`session_id` + `received_at` window** — the fallback for the 3.1 % of
   workflow rows whose agent produced no `SubagentStop`, and for the manager
   session's own work between two phase closes.

**`prompt_id` should not be a join key.** Job 1 showed a single run spanning two
of them.

## Job 3 — explicit binding records, emitted by the clerk

**Recommendation: emit explicit binding records, and put the emit point on the
clerk, as #328's close proposed. Keep post-hoc inference as the fallback it
already is, not as the design.**

### Post-hoc inference works better than expected, and that is a trap

The 2026-08-03 traverse of stub issue #337 is fully reconstructible from captured
Bash today, because the clerk's `gh` calls are Bash and Bash is captured
byte-verbatim [db: `gh issue` commands by workflow agents]:

```
18:06:38  aea1cf9f9  gh issue view 337 --json labels --jq '[.labels[].name]'
             -> ["mode:direct","tests:no","phase:build"]
18:11:32  aef460c89  gh issue edit 337 --remove-label "phase:build"     --add-label "phase:judgments"
18:12:30  a8605bfc7  gh issue edit 337 --remove-label "phase:judgments" --add-label "phase:pr-review"
18:13:12  a04d89c8f  gh issue view 337                                  (pr-review node, then ESCALATE)
18:14:29  ae93ab0bf  gh issue view 337 --json labels --jq '[.labels[].name]'   (run 2 reads cold)
18:15:11  a818bfbc8  gh issue view 337 --comments                       (resolution found)
18:16:49  a2c1c6aa1  gh issue edit 337 --remove-label "phase:pr-review" (lane complete)
```

Issue number, phase-close timestamps to the second, and the transition direction
all fall out. The non-clerk nodes are attributable too, because the ruled carrier
mechanics make them name the branch: the build node ran
`git branch -f issue-337 HEAD` and both later nodes ran `git reset --hard
issue-337`.

That completeness is an accident of this traverse's ruled steps, not a property
of the design. What it costs and what it misses:

- **Every reader re-parses shell text.** The prototype doc already carries the
  `gh issue view` / `gh issue edit` parser and its caveats — approximate by
  construction, defeated by a quoted command in a comment body, blind to
  `gh issue create` and `gh issue list`.
- **Change a command, silently lose the measurement.** The clerk's `gh issue
  edit` line is written for GitHub, not for the store. A future clerk that
  batches two label moves, or moves labels through the API, breaks every
  historical query with no error anywhere.
- **The rework-cycle index is not there.** The judgments loop is `for` rounds in
  `traverse.js` [#324: the judgments phase]; nothing in a captured command says
  which round it is.
- **The node name is not there.** Non-clerk nodes are all `workflow-subagent`.
  Which node a `git reset --hard issue-337` belongs to is inferable only by
  reading the phase labels around it.
- **Escalations and outcomes are not there at all.** The ESCALATE payload is the
  Workflow run's return value, and Job 1 showed `Workflow` rows lose
  `tool_response` at capture. The single most expensive event the factory
  produces — a run that stopped and needs a human — leaves no direct trace.
- **Judgments verdicts are not there.** They ride the judged node's structured
  output, and `StructuredOutput` is a non-Bash tool: envelope only.

### The clerk is the right emitter

The clerk already exists, is factory-only, and acts at exactly the boundaries
worth recording: it reads the phase labels as the traverse's first act and moves
them at every phase close, because the script cannot run `gh` itself [#328: the
clerk ruling; #324: `clerkRead()` / `clerkAdvance()`]. Every fact a binding record
wants — issue number, node just closed, node next, `runId`, timestamp — is
already in the clerk's hand at the moment it acts. Nothing else in the traverse
knows all of them at once.

Three properties make the emission cheap and safe:

- **It is a Bash write, so it fails the way capture does.** A clerk that appends
  one row and ignores the result cannot fail a phase; a lost binding row is a gap
  in the data, which is the same loud-at-read-time signal the capture hook
  already contracts for.
- **It rides the phase close, so it inherits the ordering the labels already
  enforce.** Single-writer discipline on labels is ruled [#328]; the binding
  record is written by the same single writer.
- **Its own rows are captured too.** The clerk's append is a Bash command, so the
  hook records it as a `PostToolUse` — the binding record and its own provenance
  land in the same store.

### What the clerk should emit, and what it cannot

At run start (one record) and at each phase close (one record each):

`run_id`, `issue`, `repo`, `node` just closed, `next_node`, `rework_cycle` where
the loop supplies one, `phase_close_at`, and the clerk's own `agent_id`.

Two facts the clerk is the wrong emitter for, because it does not see them:

- **The escalation payload.** The escalating node returns it and `traverse.js`
  short-circuits — labels untouched, no clerk advance [#328: the three-lane error
  contract]. The clerk never runs. Either the escalating node writes its own
  record before returning, or the manager writes one when it receives the
  payload. The manager is the better place: it is where the human's resolution
  lands too, and #324's own probe found that resolutions must trace to a genuine
  human turn.
- **Judgments verdicts.** They belong to the nested judgments run. The fixer node
  already handles `judgments-run record` and holds the verdicts as text; it, not
  the clerk, is the emitter.

### Two mechanisms to take for free first

Neither needs a new store, and both should be adopted whatever else is decided:

1. **Give every traverse node its own agent definition, and name it.** Job 1
   proved a workflow node's declared `agentType` lands in the hook payload
   (`gate-probe-node`). Naming nodes turns `agent_type` into the node name on
   every row the node produces — the node dimension, for free, with no
   supplemental write and no parsing.
2. **Write the `runId` into `.factory/state.json` beside the issue number.** The
   manager already keeps that file for reaping [#328]. It is the cheapest
   `runId → issue` map there is, and it makes the 3.1 % of rows the
   `SubagentStop` bridge misses recoverable through `cwd` and time instead.

### The journal is a poor join key

`journal.jsonl` is real and per-run, at
`~/.claude/projects/<project>/<session-uuid>/subagents/workflows/wf_<runId>/journal.jsonl`
— 126 of them on this machine. Across all of them there are exactly four
top-level fields [disk: full survey of 1,405 records]:

```json
{"type": "started", "key": "v2:ab512b69…", "agentId": "aea1cf9f9ddf4fede"}
{"type": "result",  "key": "v2:ab512b69…", "agentId": "aea1cf9f9ddf4fede",
 "result": {"status": "done", "labels": ["mode:direct","tests:no","phase:build"]}}
```

`type` is `started` or `result`; `key` is a content hash for the resume cache;
`agentId` matches the store's `agent_id` exactly; `result` is the node's own
structured output. **There is no timestamp, no node name, and no issue number
anywhere in it** — no field whose name contains any of those. It is a resume
journal, not an audit log.

Two consequences. It is genuinely useful as a *supplement*: it holds node results
the store drops on the floor, including the escalation `reason` and `brief`, and
`agentId` joins it to hook rows for free. But it cannot be the binding record: it
carries neither the issue nor the clock, its path is the only place the `runId`
lives, and it sits in the harness's transcript tree where nothing this repo
controls governs its retention.

## What this leaves open

- **The escalation emit point** — clerk-adjacent but not the clerk; manager
  versus escalating node is a factory-manager design question, not a measurement
  one.
- **Whether to revive the #272 capture extension.** `file_path` on
  `Read`/`Edit`/`Write` and whole `tool_input` on `Skill` are written and tested
  on the `issue-272-design` branch and were never merged. File attribution and
  agent-invoked skill attribution both stay dead until they are. Independent of
  everything above.
- **Retention.** 38 MB in seven days, no pruning, no indexes. Not urgent; it will
  be.

## References

- [`dotfiles/dot-claude/hooks/measure-event`](/dotfiles/dot-claude/hooks/measure-event)
  — the capture hook; `for_storage` holds the trim rule.
- [`dotfiles/settings/fedora.json`](/dotfiles/settings/fedora.json) — the hook
  wiring, and the authority on which events are captured.
- `docs/measurement-prototype.md` on the `issue-272-design` branch — the store's
  current documentation, and the source of the phantom-`SubagentStop` and
  `gh`-parsing analysis this survey builds on.
- [dev-playbook#324](https://github.com/GeoffNordling/dev-playbook/issues/324) —
  traverse build facts, the clerk's `gh` calls, worktree naming, the probe runs
  measured here.
- [dev-playbook#328](https://github.com/GeoffNordling/dev-playbook/issues/328) —
  the clerk ruling, the three-lane error contract, `.factory/state.json`.
- [Machines](/docs/machines.md) — capture runs on the primary machine only.
