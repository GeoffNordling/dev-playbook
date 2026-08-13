---
type: Survey
title: Confirmation Re-measure of Decision-Critical Facts
description: The empirical ground beneath the traverse-architecture and review-loop decisions, graded fresh or probed live on Claude Code 2.1.229
---

# Confirmation re-measure of decision-critical facts (#410)

*Measured 2026-08-12 by the confirmation-pass session working
[map #403](https://github.com/GeoffNordling/dev-playbook/issues/403). Harness:
**Claude Code 2.1.229** (`claude --version`) — the version has moved since
[#405](https://github.com/GeoffNordling/dev-playbook/issues/405)'s records
(2.1.227) and since [#415](https://github.com/GeoffNordling/dev-playbook/issues/415)'s
(2.1.227/2.1.228). git 2.55.0. Probing position: a **subagent at spawn depth 1**
of an interactive main session seated at the dev-playbook main checkout
(`/home/geoff/workspace/dev-playbook`) — the harness's own transcript metadata
records the probe children at `spawnDepth: 2`, so this session is depth 1, its
children are depth 2 and their children depth 3: exactly the depths the
factory's node and helper tiers occupy. **No headless `claude -p` was used
anywhere** — ruled out by the user, since production runs interactive sessions
and a headless probe smuggles in an unmeasured equivalence assumption. Facts
reachable only by launching a fresh or differently-rooted session are recorded
as NOT MEASURABLE FROM HERE, never guessed.*

## Summary

**50 empirical facts** enumerated across the two decisions and their #419 boundary.

| Grade | Count |
|---|---|
| **PROBED HERE** — measured live in this session | 33 |
| **FRESH** — an existing record covers it, nothing added | 6 |
| **NOT MEASURABLE FROM HERE** — reason recorded, never guessed | 4 |
| **NOT RE-MEASURED** — calibration context, no ruling turns on it | 1 |
| **DEFERRED to [#419](https://github.com/GeoffNordling/dev-playbook/issues/419)** | 6 |

Of the 33 probed here: **27 CONFIRMED**, **2 PARTIALLY confirmed**,
**2 REFUTED as stated**, **1 new fact** neither decision had considered, and
**1 inconclusive** (A9 — the probe reached an existence check, not the fact).

### The headlines — what goes back

Both refutations are against
[#408](https://github.com/GeoffNordling/dev-playbook/issues/408); nothing under
[#409](https://github.com/GeoffNordling/dev-playbook/issues/409) is refuted.

1. **REFUTED — "placement by instruction" does not survive a second tool call.**
   (A11) In an agent thread a standalone `cd` **does not persist to the next Bash
   call**: cwd resets to the main conversation's cwd every call — measured at
   depth 1 and depth 2, for an in-repo target as well as an out-of-repo one.
   #415 verdict 7's "a node told the worktree path `cd`'d into it and operated
   there correctly" holds only *within a single Bash invocation*. #408 §3's "its
   first act is `cd` plus a placement self-check" reads as a one-time act that
   places the node for the rest of its run; that is false. Node instructions must
   carry the worktree path into **every** command (`git -C <wt>`, absolute paths,
   or `cd <wt> && …` chained inside each call). The unfenced-nodes ruling
   survives; how it is implemented changes, and #416's guardrail surface grows —
   a forgotten path is a once-per-call risk, not a once-per-node one.

2. **REFUTED as stated — `agent_type` is empty on 86% of `SubagentStop` events.**
   (A21) #408 §6 claims "`agent_type`/`agent_id` on hook events give the
   accounting join its keys". Measured against the live store: `SubagentStop`
   carries `agent_id` on 4598/4598 rows but `agent_type` as an **empty string**
   on 3977 of them (86.5%); `SubagentStart` carries both on 663/663. The node's
   terminal event — the natural "node finished" marker — cannot supply the type.
   The join must key on `agent_id` and resolve type from `SubagentStart` or
   `PostToolUse`. This also answers #405 R6's explicitly-open question ("cannot
   prove a phantom empty `agent_type` never appears") in the negative, on
   thousands of rows.

3. **NEW FACT — a parent agent cannot stop a stalled child, and a stalled child
   may wake.** (A24) `TaskStop` on this session's own stalled child was refused:
   `Task <id> is owned by <id>; agent <parent-id> cannot stop it.` The child was
   abandoned and its work redone in a fresh agent — then it woke 9 hours 51
   minutes later and completed normally. #408's relaunch-fresh recovery ("a
   stalled or dead issue manager is never resumed — the factory manager spawns a
   fresh one") is sound as a policy about not resuming, but the stalled agent
   **cannot be reaped by its parent** and **may not be dead**: a relaunch adds a
   second live issue manager rather than replacing the first, and the older one
   can wake last and overwrite the newer one's work.

Everything else the two decisions lean on is confirmed at 2.1.229 — including
all four constraints that forced the unfenced-node relaxation, re-measured here
rather than inherited.

### How to read a record

- **PROBED HERE** — setup, commands, verbatim output, verdict.
- **FRESH** — an existing probe record covers it; cited, not re-run.
- **NOT MEASURABLE FROM HERE** — the reason, and who covers it.
- Verdicts: **CONFIRMED** / **PARTIALLY confirmed** (with the delta) /
  **REFUTED** (with the delta).

---

## Part 1 — facts under #408 (Greenfield traverse architecture)

### A1. Spawning works to depth 3; at depth 3 the `Agent` tool is withheld, so depth 4 is impossible and fails loud

**PROBED HERE — CONFIRMED at 2.1.229** (fresh record: #415 verdict 1, on
2.1.227/228). Probe: this session (depth 1) spawned a child (depth 2) which
spawned a leaf (depth 3); each reported its own toolset. Verbatim from the
depth-3 leaf:

```
Top-level (fully loaded): Artifact, Bash, Edit, Read, Skill, ToolSearch, Write
Deferred: EnterWorktree, ExitWorktree, Monitor, NotebookEdit, SendMessage,
          TaskStop, WebFetch, WebSearch

A tool named `Agent` is NOT available to me — it does not appear in either the
top-level list or the deferred-tools list.

(b) ToolSearch `select:Agent` exact response:
No matching deferred tools found

(c) Since no tool named `Agent` is available, I did not attempt to spawn a
subagent.
```

The depth-2 child, by contrast, reported `Agent` present among its top-level
tools. **CONFIRMED**: the cap bites exactly at depth 3 by withholding the tool,
so a depth-4 spawn cannot be attempted at all. Two notes: the depth-3 toolset
differs slightly from #415's 2.1.227 inventory (which listed `ListAgents` and
`ReportFindings`, absent here; `Artifact` present here) — ordinary version drift,
the `Agent`-withheld property unchanged. And the probe child labelled the tiers
from its own vantage ("I am depth-1, the leaf is depth-2"); the harness's
transcript metadata is authoritative and records that child at `spawnDepth: 2`.

### A2. The depth cap defaults to 3 and is configurable via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`

**PROBED HERE — CONFIRMED, and sharpened.** #408 §1 leans on the documented
default and on the knob ("the design need not ride an unpinned default").

Setup: string-grep the running harness binary
(`/home/geoff/.local/share/claude/versions/2.1.229`, 311 MB ELF, not stripped),
plus a read of live settings.

```
$ grep -aoc "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH" .../versions/2.1.229
5
$ grep -ao "CLAUDE_CODE_MAX_[A-Z_]*" .../versions/2.1.229 | sort -u
CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS
CLAUDE_CODE_MAX_CONTEXT_TOKENS
CLAUDE_CODE_MAX_OUTPUT_TOKENS
CLAUDE_CODE_MAX_RETRIES
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH
CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION
CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY
CLAUDE_CODE_MAX_TURNS
CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION
```

Two live strings, verbatim from the binary:

```
…pawning another agent. If the user explicitly requested deeper nesting, ask
them to raise CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH.

function EK(){let e=Q.CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH;if(e!==void 0)return e;
if(Gzs===null){let{getFeatureValue_CACHED_MAY_BE_STALE:t}=(gn(),on…
```

Live settings (`~/.claude/settings.json`): `env` is
`{"CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"}` — **no spawn-depth pin**.

**Verdict — CONFIRMED, sharpened.** The knob exists and the harness's own
refusal text names it. But the measured resolution order is: env var if set,
**otherwise a remote feature-value lookup** (`getFeatureValue_CACHED_MAY_BE_STALE`)
— the default is served, not a local constant, and the workspace pins nothing.
The factory's budget (manager 0 → issue manager 1 → node 2 → helpers 3) sits
exactly at the cap, so a server-side default change silently costs the design
its bottom tier. Pin the variable explicitly. (Scope: string evidence for the
resolution order; the numeric default was not read out.)

### A3. Concurrent subagents are capped session-wide, default 20, via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`

**PROBED HERE — PARTIALLY confirmed.** Same binary: the name exists (5
occurrences), with refusal text `…If the user wants more concurrent subagents,
ask them to increase CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS.` and resolution
`function bgd(){return Q.CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS??jM_}` — a local
constant fallback, unlike A2's remote lookup. **The number 20 was not measured**
(it would take 21 concurrent spawns) and is not readable from the strings.
Also surfaced: a third knob the design has not considered,
`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` — a *cumulative* per-session cap
distinct from concurrency, which a long-running factory manager spawning one
issue manager per issue could plausibly meet. Default likewise unmeasured. The
parallel fast-follow sizes against both.

### A4. The Workflow tool is stripped from subagents

**PROBED HERE — CONFIRMED at 2.1.229** (fresh record: #405 H2, with verbatim
refusal text). This session is itself a subagent: `Workflow` is absent from its
toolset, and `ToolSearch("select:Workflow")` returns, verbatim,
`No matching deferred tools found`. Load-bearing only for #408's *rejection* of
the workflow shape.

### A5. `workflow()` nesting is limited to one level, failing loud

**FRESH** — #405 H6 (2.1.227), verbatim error quoted there. **NOT MEASURABLE
FROM HERE**: the Workflow tool is stripped from subagents (A4), so no probe from
this position can reach it. Immaterial to the ruling — the chosen architecture
contains no workflow.

### A6. Subagents always start in the main conversation's cwd

**PROBED HERE — CONFIRMED at 2.1.229** (fresh record: #415 verdict 4). Four
independent observations, every spawned agent reporting `pwd`:

```
A7's child (depth 2, cwd input passed):      /home/geoff/workspace/dev-playbook
A14's Explore agent (depth 2):               /home/geoff/workspace/dev-playbook
A11/A12's probe child (depth 2):             /home/geoff/workspace/dev-playbook
A1's leaf (depth 3):                         /home/geoff/workspace/dev-playbook
```

All four landed at the main conversation's cwd, including the depth-3 leaf whose
parent is itself a subagent. Position caveat stated honestly: this session's own
cwd *is* the main conversation's cwd, so the discriminating case (a child
starting at its parent's cwd rather than the root's) is not separable from here
for depth-2 children — but the **depth-3 leaf is decisive**: its parent (depth 2)
could not have been at the repo root by any other mechanism, and #415 separated
the cases directly.

### A7. The Agent tool's `cwd` input is accepted and silently ignored

**PROBED HERE — CONFIRMED at 2.1.229, discharging #415's "re-probe on upgrade".**
#408 §3 constraint 2 records this as a harness gap; #415 measured it on
2.1.227/2.1.228 and flagged a re-probe. The harness has since moved two versions.

Probe, run twice — depth 1→2 and depth 2→3 — passing
`cwd: /home/geoff/workspace/dev-playbook/standards` alongside
`subagent_type: general-purpose`, `model: sonnet`, prompt
`Make one Bash call: pwd. Reply with only its exact output.`

Depth 1→2: **no validation error**; the spawn launched normally; the child's
entire reply was `/home/geoff/workspace/dev-playbook`.

Depth 2→3, reported verbatim by the spawning child:

```
The harness did NOT reject the call. No validation/error text was returned. …
no complaint about the extra `cwd` field despite the Agent tool's declared
schema having `additionalProperties: false`. The call was therefore ACCEPTED
(silently — extra field ignored by validation, not honored). The child's own
`pwd` output … was:
/home/geoff/workspace/dev-playbook
```

**Verdict — CONFIRMED, unchanged on 2.1.229, at two tiers.** Sharper form of the
gap than #415 recorded: the tool's declared schema sets `additionalProperties:
false` and does not list `cwd` at all, yet the extra input passes validation
silently rather than being rejected. Nothing may rely on `cwd` until a probe
shows it working.

### A8. `EnterWorktree`'s name (creation) form is refused outright from a subagent

**PROBED HERE — CONFIRMED at 2.1.229, byte-identical refusal.** A depth-2
subagent called `EnterWorktree(name: "probe410wt")`. Verbatim tool error:

```
EnterWorktree cannot create a worktree from a subagent with a cwd override
(isolation: "worktree" or explicit cwd) — it would mutate the parent session's
process-wide working directory. To work in a different directory (including a
worktree), spawn an Agent with `cwd` set to it.
```

Identical to #415's 2.1.227/228 text — and note it still recommends the input A7
measures as inert.

### A9. `EnterWorktree`'s path (attach) form is closed to subagents

**FRESH, not re-measured here — this session's probe missed the target, and its
first reading of the result was wrong.** #415 verdict 3 recorded an immediate
refusal naming the subagent's cwd ("the current working directory <MAIN> is the
repository root, not an isolated worktree"). This session's probe passed a path
that does not exist:

```
EnterWorktree(path: "/home/geoff/workspace/dev-playbook/.claude/worktrees/does-not-exist-410")

→ Cannot enter worktree: /home/geoff/workspace/dev-playbook/.claude/worktrees/does-not-exist-410:
  ENOENT: no such file or directory, lstat
  '/home/geoff/workspace/dev-playbook/.claude/worktrees/does-not-exist-410'
```

That is an **existence** refusal, reached before any subagent-eligibility check,
so it neither confirms nor refutes #415 verdict 3 — which stands as the fresh
record, un-re-measured at 2.1.229. A probe wanting to re-measure it must pass the
path of a worktree that really exists.

**Two things the probe did measure, both worth keeping.** First, the refusal is
**loud** — correcting this record's own earlier reading, which was written while
the call was still outstanding and called it fail-silent. Second, it was
**extraordinarily slow**: issued at 23:03 on 2026-08-12, returned at 08:54 the
following morning — 9 hours 51 minutes (the harness's own usage report puts the
agent's total duration at 35,627,636 ms) for a failed `lstat`. Throughout those
hours the call was indistinguishable from a hang; this session concluded it had
hung, abandoned the agent, and re-ran the remaining steps in a fresh one. A
factory manager watching a node behave that way would reach the same conclusion.
That is A24's problem, and this is its measured basis.

### A10. No write fence binds any subagent in this shape

**PROBED HERE — CONFIRMED at 2.1.229, both tiers.** #408 §3 constraint 4 is the
load-bearing one behind the unfenced-node ruling.

- **Depth 1 (this session).** `Write` to
  `/home/geoff/workspace/dev-playbook/FENCE-410-depth1.txt` →
  `File created successfully at: /home/geoff/workspace/dev-playbook/FENCE-410-depth1.txt`.
  Ground truth: `-rw-r--r--. 1 geoff geoff 23 … FENCE-410-depth1.txt`. Removed.
- **Depth 2 (a spawned node).** `Write` to
  `/home/geoff/workspace/dev-playbook/FENCE-410-depth2.txt` →
  `File created successfully at: /home/geoff/workspace/dev-playbook/FENCE-410-depth2.txt`.
  Removed by the child; `ls` after:
  `ls: cannot access '…/FENCE-410-depth2.txt': No such file or directory`.

Both writes landed in the repo's **main checkout** from agents that never entered
a worktree. The exposure #416 must guardrail is real and unchanged.

### A11. Nodes are "placed by instruction" — first act `cd` plus a placement self-check

**PROBED HERE — REFUTED AS STATED.** This is the mechanism the whole unfenced
design runs on, so it was probed at both node tiers.

**Probe (depth 1, this session).** Two consecutive Bash calls, the `cd`
standalone as the workspace's bash discipline requires:

```
call 1:  cd /home/geoff/workspace
         (Bash completed with no output)
call 2:  pwd
         /home/geoff/workspace/dev-playbook
```

Repeated with an **in-repo** target, to rule out "the harness only resets a `cd`
that leaves the repo root":

```
call 1:  cd /home/geoff/workspace/dev-playbook/standards
         (Bash completed with no output)
call 2:  pwd; ls | head -5
         /home/geoff/workspace/dev-playbook
         CLAUDE.md
         CONTEXT.md
         docs
         dotfiles
         harness-recipes
```

**Probe (depth 2, a spawned node).** Identical steps, verbatim from the child's
transcript:

```
>>> Bash {"command": "pwd"}
<<< /home/geoff/workspace/dev-playbook
>>> Bash {"command": "cd /home/geoff/workspace/dev-playbook/standards"}
<<< (Bash completed with no output)
>>> Bash {"command": "pwd"}
<<< /home/geoff/workspace/dev-playbook
>>> Bash {"command": "cd /home/geoff/workspace/dev-playbook/standards && pwd && ls | head -3"}
<<< /home/geoff/workspace/dev-playbook/standards
    build
    build.md
    claude-code
```

**Verdict — REFUTED as stated; the underlying capability survives in a narrower
form.** A `cd` **binds only within the single Bash call that issues it**; the
next call starts back at the main conversation's cwd. The reset is blanket — not
the "harness resets any `cd` beyond the repo root" behavior #418 observed from a
main session; an in-repo `cd` is reset too. The harness states the rule itself in
an agent thread's system prompt ("Agent threads always have their cwd reset
between bash calls, as a result please only use absolute file paths"), and this
probe measures it true at both node tiers.

#415 verdict 7 remains true as measured — a node *can* work in the worktree
(third call above). What is false is the implied persistence. Consequences for
the build epic:

- A node's launch line cannot say "first act: `cd` into the worktree" and
  consider the node placed. Placement must be re-asserted on **every** call:
  `git -C <worktree> …` for git, absolute paths for file tools, and
  `cd <worktree> && …` chained inside each Bash call that needs a cwd.
- The placement self-check is still worth keeping, but it verifies one call, not
  a state.
- #416's blast-radius work grows: the forgotten-path accident is a once-per-call
  risk across a node's whole run, not a once-at-startup risk — and under the
  workspace-scoped root ruled at #418, each lapse lands as a loud
  `fatal: not a git repository` (W6) rather than a silent write into a main
  checkout, which is exactly the mitigation that ruling bought.

### A12. The terminal report contract transports `DONE:` / `ESCALATE:` verbatim through the tiers

**PROBED HERE — CONFIRMED at 2.1.229, through two tiers** (fresh record: #415
verdict 8). Probe: the depth-3 leaf was instructed that its final message must
begin at character one with exactly `ESCALATE: probe-410 leaf reporting`; the
depth-2 child was instructed to relay that message verbatim and to begin its own
final message with `ESCALATE: probe-410 depth-2 relaying leaf`.

What arrived at this session, first characters of the child's final message:

```
ESCALATE: probe-410 depth-2 relaying leaf
```

and inside it, the leaf's message reproduced with its own first line intact:

```
ESCALATE: probe-410 leaf reporting

(a) Complete visible toolset: …
```

**CONFIRMED**: the prefix survived at character one at both hops, and the body
survived verbatim across the depth-3 → depth-2 → depth-1 relay. As #415 noted,
transport is instruction-following, not harness enforcement — the
malformed-fails-safe rule remains the backstop. One observation supporting that
caution: the relaying child *also* appended its own summary paragraph after the
relayed content, and in it mislabelled the tiers from its own vantage. Content
survives; a relay's framing is the relayer's own and cannot be trusted as data.

### A13. A typed spawn with no `model` inherits the definition's pin; a passed `model` overrides it

**FRESH** — #405 R8 (2.1.227), ground-truthed against transcript `model` fields.
Not re-run: a re-measure needs a throwaway agent definition plus a session that
loads it, and definitions resolve at session start — unreachable from inside a
running subagent without launching a session. #408 §6's "model pins ride the
definitions" rests on it unchanged.

### A14. A named agent definition that omits `Agent` from its tools cannot spawn at all

**PROBED HERE — CONFIRMED, and sharpened.** #408 §6 carries this as a
documentation claim ("documented"), never measured. Probe: spawn the built-in
`Explore` definition, whose tool list is *all tools except Agent* — the exact
shape the claim describes — and have it try to spawn. Its verbatim report:

```
STEP 1 — Complete visible toolset
Directly-available tools: Bash, Read, Skill, ToolSearch
Deferred tools: EnterWorktree, ExitWorktree, Monitor, SendMessage, TaskStop,
WebFetch, WebSearch
A tool named `Agent` does not appear in either list.

STEP 2 — ToolSearch query `select:Agent`
No matching deferred tools found

STEP 3 — Attempt to invoke tool `Agent`
Error: No such tool available: Agent. Agent is disabled for this session, in
subagents as well as here.

STEP 4 — Bash `pwd`
/home/geoff/workspace/dev-playbook
```

**Verdict — CONFIRMED.** A definition without `Agent` cannot spawn: the tool is
absent, undiscoverable, and refused by name. **Sharpening the design needs**: the
refusal says *"in subagents as well as here"* — the disablement is **inherited by
that agent's own children**. An issue-manager definition omitting `Agent` would
not merely fail to spawn nodes; it would disable spawning for everything beneath
it. #408 §6's "definitions keep `Agent` in their tools" is a requirement at every
tier that has descendants, not only at the issue manager.

### A15. The factory manager's worktree spelling works with the repo named from outside

**PROBED HERE — CONFIRMED.** #408 §3 pins the exact command; #418 measured a
neighbouring spelling (`git -C <repo> worktree add --detach <path>`). This probe
runs the spelling as written, then reverses it.

```
$ git -C /home/geoff/workspace/dev-playbook worktree add .claude/worktrees/issue-999410 -b issue-999410 origin/main
Preparing worktree (new branch 'issue-999410')
branch 'issue-999410' set up to track 'origin/main'.
HEAD is now at 5e5b617 The glossary defines the factory manager by what it is: rejected-alternative names cut
rc=0

$ git -C /home/geoff/workspace/dev-playbook worktree list
/home/geoff/workspace/dev-playbook                                5e5b617 [main]
/home/geoff/workspace/dev-playbook/.claude/worktrees/issue-999410 5e5b617 [issue-999410]

$ git -C … worktree remove .claude/worktrees/issue-999410      → rc=0
$ git -C … branch -D issue-999410
Deleted branch issue-999410 (was 5e5b617).
```

**CONFIRMED.** The relative worktree path resolves **inside the repo** (`git -C`
chdirs first), the branch is created at `origin/main` and set to track it, the
main checkout stays on `main`, and worktree and branch both remove cleanly.
Position note: this session's cwd is the repo root rather than `~/workspace`;
`-C` makes the caller's cwd irrelevant to the outcome, and #418 measured the
workspace-root caller directly. Observed live alongside it: the parallel #419
session's own `.claude/worktrees/issue-419` registered as a second worktree of
the same main checkout — two agents' worktrees coexisting under one repo, as the
design assumes.

### A16. The stale-base check before worktree creation

**PROBED HERE — CONFIRMED.** #408 §3 gates worktree creation on "the live
worktree contract's stale-base check". The contract
(`software-factory/factory-operations.md` §The worktree contract) spells it:
"check that the local `origin/main` ref matches origin (`git rev-parse
origin/main` against `gh api …/branches/main`)".

```
$ git -C /home/geoff/workspace/dev-playbook rev-parse origin/main
5e5b6175e3101611f3fae146737f52d078851de1
$ gh api repos/GeoffNordling/dev-playbook/branches/main --jq .commit.sha
5e5b6175e3101611f3fae146737f52d078851de1
```

Both spellings work from an agent's Bash and returned agreeing, directly
comparable values. The check is executable exactly as written. Standing caveat
unchanged (#415 verdict 12): `git worktree add … origin/main` reads the *local*
remote-tracking ref, which moves only on fetch — which is why the check is
mandatory. One live-text note for the doc slice: the same worktree contract
still prescribes `EnterWorktree(name=issue-<N>)` for creation — the form A8
measures as closed to subagents.

### A17. `worktree.baseRef: "fresh"` is live configuration

**PROBED HERE — CONFIRMED, context only.** `~/.claude/settings.json` carries
`worktree: {'baseRef': 'fresh'}` at 2.1.229, unchanged since #405 R4 read it. It
governs `EnterWorktree` and `isolation:'worktree'` spawns — neither of which the
ruled design uses — so it is now context, not a load-bearing input.

### A18. Nothing reaps the persistent issue worktree

**NOT MEASURABLE FROM HERE.** #415 verdict 11 grades this **REASONED FROM DOCS,
not measured**, and #408 §3 relies on the reasoning ("being user-created, it sits
outside the documented sweep's scope"). A real test needs a
`cleanupPeriodDays`-scale observation across sessions and days, which no single
session can produce.

Two supporting facts measured here: `cleanupPeriodDays` is **unset** in
`~/.claude/settings.json`, so the documented 30-day default governs; and the A15
spelling creates **no `worktree-`-prefixed branch**, so the Agent-view
prefix-keyed cleanup has nothing to match. The gap stays exactly where #415 left
it: if a factory worktree ever vanishes idle, probe this first.

### A19. The tapless PAT cannot push workflow files

**NOT MEASURABLE FROM HERE non-mutatingly.** #408 §4 has the builder escalate
"naming the PAT scope constraint". What is measurable:

```
$ gh auth status
github.com
  ✓ Logged in to github.com account GeoffNordling (keyring)
  - Git operations protocol: https
  - Token: github_pat_****…

$ gh api -i user   (headers)
Github-Authentication-Token-Expiration: 2026-08-23 19:58:30 UTC
X-Accepted-Github-Permissions: allows_permissionless_access=true
(no X-OAuth-Scopes header)
```

The credential is a **fine-grained PAT** (`github_pat_` prefix) and the API
returns no `X-OAuth-Scopes` header — so the classic `workflow` OAuth scope does
not apply here at all; the fine-grained analogue is the repository **Workflows**
permission, which has no read-only introspection endpoint. Confirming the refusal
would require actually pushing a `.github/workflows` change — a mutating act,
out of bounds for a probe. The case is live: the repo has
`.github/workflows/ci.yml`.

**The decision does not depend on this resolving** — #408 §4 already rules that
*any* push refusal is an operational escalation, so the mechanism fails loud
either way. Two text notes: the claim should read "may be refused by the PAT's
Workflows permission" until a real push measures it; and the credential expires
**2026-08-23**, eleven days out — an expiring PAT is a whole-factory stop.

### A20. The run ledger can be a sibling table beside the hook-event store's `events` table

**PROBED HERE — CONFIRMED.**

```
$ ls -la ~/.local/share/claude-measure/
-rw-r--r--. 1 geoff geoff 88526848 Aug 12 22:59 events.db

sqlite_master:             ('table', 'events')     — exactly one table
pragma table_info(events): (0,'id','INTEGER',pk) (1,'received_at','TEXT')
                           (2,'event','TEXT') (3,'session_id','TEXT')
                           (4,'prompt_id','TEXT') (5,'payload','TEXT')
indexes:                   []                      — none
select count(*):           36043
distinct event:            UserPromptSubmit, PostToolUse, Stop, SubagentStop,
                           SubagentStart, SessionStart, PostCompact,
                           UserPromptExpansion, SessionEnd, Notification
```

The writer (`dotfiles/dot-claude/hooks/measure-event`) documents its own
discipline in its module docstring — quoted, because #408 §5 contrasts the
ledger's fail-loud against it:

> Failure discipline — the one sanctioned exception to this workspace's
> fail-loud rule: a session must never fail because measurement did. Every path
> exits 0; a failure to record appends a line to errors.log beside the database,
> and a failure to write even that is swallowed.

and it already handles concurrent writers: "Concurrent sessions write to one
database. WAL lets their readers and this writer coexist, and the busy timeout
makes a collision queue rather than fail" (`BUSY_TIMEOUT_SECONDS = 5.0`).

**CONFIRMED**: one database, one table, no indexes, a documented fail-quiet
writer under WAL with a busy timeout. A sibling `runs` table is free, and #408
§5's fail-loud contrast is drawn against a real, documented behavior. (#417 pins
the schema; the `repo` promoted column #418 mentions does not exist yet — that is
#417's forward work, not a present-tense fact.)

### A21. `agent_type` / `agent_id` on hook events give the accounting join its keys

**PROBED HERE — REFUTED AS STATED.** #408 §6 asserts this satisfied by
construction. Measured against the live store, 2026-08-12:

```
event                agent_type            rows
-------------------  --------------------  -----
PostToolUse          present               14459
PostToolUse          MISSING (no key)         75
SubagentStart        present                 663
SubagentStop         present                 621
SubagentStop         EMPTY STRING           3977
Stop                 MISSING                 347
Stop                 present                 115
UserPromptSubmit     present / MISSING    124/31
SessionStart / End   present                20/12
Notification         present                  51
PostCompact          MISSING / present      12/2
UserPromptExpansion  present                   6

cross-tab on the two subagent events:
SubagentStart  agent_id:present  agent_type:present    663  (100%)
SubagentStop   agent_id:present  agent_type:EMPTY     3977  (86.5%)
SubagentStop   agent_id:present  agent_type:present    621  (13.5%)
```

A verbatim empty-type payload, captured from this very session's probe agents:

```json
{"session_id": "233b5c93-…", "cwd": "/home/geoff/workspace/dev-playbook",
 "agent_id": "a12841996ce0ab5e0", "agent_type": "",
 "effort": {"level": "xhigh"}, "hook_event_name": "SubagentStop"}
```

Distinct non-empty `agent_type` values, most common first: `general-purpose`
(9591), `workflow-subagent` (3392), `claude` (1469), `Explore` (1191), `builder`
(159), `claude-code-guide` (112), `fork` (72) — typed definitions do appear, so
type-keyed accounting is possible in principle.

**Verdict — REFUTED as stated, with the repair in hand.** `agent_id` is a sound
join key on both subagent events (4598/4598 and 663/663). `agent_type` is **not**
usable from `SubagentStop` — precisely the event that marks a node finishing —
being an empty string 86.5% of the time. Bookkeeping must resolve a run's node
type from `SubagentStart` (or `PostToolUse`) by `agent_id`, never from the
terminal event. Two knock-ons: #405 R6's open never-empty question is answered —
the phantom empty `agent_type` is real, common, and lives on `SubagentStop`
exactly where B10 first saw it — and
[#411](https://github.com/GeoffNordling/dev-playbook/issues/411)'s fitness check
should treat this as a known join constraint rather than rediscover it.

### A22. Today's issue overwatch already drives build→review→rework this way (agents, no workflow)

**PROBED HERE — CONFIRMED.** #408 §1's "the no-workflow shape is also the
exercised one". From `dotfiles/dot-claude/skills/issue-overwatch/SKILL.md`,
verbatim:

- "You own one issue's traverse through the factory: read the software factory
  graph, execute it node by node, and stop wherever the user must act or decide.
  You sequence every node — nothing launches itself — and you are the issue's
  single writing session: subagents and inline skills do the work and report,
  and every label move is yours."
- "Spawn a subagent whose prompt is the launch line, nothing more"
- "Parse the subagent's final message per the terminal report contract"

No Workflow invocation anywhere in the skill. **CONFIRMED** — with one delta for
the doc slice: the skill also says *"From then on the worktree is inherited:
subagents get it as cwd"*. That is true **only because today's overwatch is a
main session** that entered the worktree — the "main conversation's cwd"
mechanism of A6. The issue manager, being itself a subagent, cannot inherit that,
which is exactly why #408 §3's relaxation is forced. The retiring skill's
sentence must not be copied forward into the issue-manager definition.

### A23. Reviewer definitions can carry the same read-only enforcement the review skills carry today

**PROBED HERE — PARTIALLY confirmed.** #408 §6. The three review skills'
frontmatter, verbatim and identical across `bug-pr-review`, `code-pr-review`,
`doc-pr-review`:

```yaml
model: opus
effort: xhigh
disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
allowed-tools: Write(//tmp/**)
```

**Confirmed**: the enforcement exists today exactly as described, with a concrete
rule string to migrate. **Not confirmed**: that an *agent definition* honors
`disallowed-tools` / `allowed-tools` with the same semantics — a definition's
documented tool control is the `tools:` allowlist, and testing the deny form
needs a definition plus a session that loads it (definitions resolve at session
start), unreachable from inside a running subagent. Evidence that
definition-level tool restriction works at all is strong (A14: the `Explore`
definition's restriction held and propagated to children). Treat "reviewer
definitions carry `disallowed-tools`" as a claim to verify when the first
definition is written, not as measured.

### A24. A parent agent cannot stop a stalled child

**PROBED HERE — NEW FACT**, unasked by either decision but load-bearing for
#408's recovery ruling. When the A9 probe stalled, this session tried to reap it:

```
TaskStop(task_id: <child agent id>)
→ Task a8830…d7b is owned by a8830…d7b; agent af717…057 cannot stop it.
```

The reap was refused across the ownership boundary. The session abandoned the
child and re-ran its remaining steps in a fresh agent — and the abandoned child
**woke 9 hours 51 minutes later and completed normally**, reporting its full
results long after that work had been redone elsewhere.

**Verdict — #408's relaunch-fresh recovery is sound but incomplete, and the
stall it must survive is real.** "A stalled or dead issue manager is never
resumed — the factory manager spawns a fresh one" is a policy about not
resuming, and it stands. Three measured facts complicate it: the factory manager
**cannot terminate** the stalled one (`TaskStop` refuses across the ownership
boundary); the stalled one may be **not dead but merely slow**, resuming and
running to completion hours later; and each stall holds one of the session-wide
concurrency slots (A3) meanwhile. A relaunch therefore risks two live issue
managers writing the same issue's labels, worktree, and PR threads — against the
single-writer discipline — with the older one waking last and overwriting. The
guardrail design ([#416](https://github.com/GeoffNordling/dev-playbook/issues/416))
and the relaunch procedure need an explicit answer: the ledger's double-dispatch
prevention (#408 §5) read *and written* before any relaunch, and a woken-late
node detecting that its run was superseded and exiting without writing.

### A25. The branches the resolution cites as prior art and design seed exist

**PROBED HERE — CONFIRMED.**

```
$ git -C … ls-remote --heads origin research/hook-capture-workflow-runtime issue-349 prototype/412-review-thread-mechanics
d2de342413e0e36d52c5465dfcb146747d223ec0  refs/heads/issue-349
856836f0c4077567fbfb8bcb5d636f861ab43d68  refs/heads/prototype/412-review-thread-mechanics
e10c2056e30274bc287509392f31689fec94eba6  refs/heads/research/hook-capture-workflow-runtime
```

All three on origin: attempt one's traverse implementation (#408's prior art),
#412's never-pruned capture branch, and the `bindings` proposal #408 §5 names as
the ledger's design seed.

---

## Part 2 — facts under #409 (The review-loop apparatus)

Every GitHub mechanic #409 leans on was verified live at
[#412](https://github.com/GeoffNordling/dev-playbook/issues/412) the same day
against throwaway [PR #414](https://github.com/GeoffNordling/dev-playbook/pull/414).
Those are cited, not re-run — except where this session could re-observe them for
free against the still-open PR #414, which it did as an independent check
(B2–B6).

### The independent re-observation of PR #414 (backs B2–B6)

One GraphQL read from this session, 2026-08-12:

```
$ gh api graphql -f query='query { repository(owner:"GeoffNordling", name:"dev-playbook")
    { pullRequest(number:414) { state isDraft reviewThreads(first:20) { totalCount
      nodes { isResolved isOutdated path line originalLine subjectType
              comments(first:1){nodes{body}} } } } } }'

{"state":"OPEN","isDraft":false,"total":4,"threads":[
 {"first":"Blocking: (test fixture) line 01 is deliberately \"wrong\". Te",
  "isResolved":true,"isOutdated":true,"line":null,"originalLine":13,
  "path":"prototype-412/alpha.md","subjectType":"LINE"},
 {"first":"Suggestion: (test fixture) line 03 is deliberately \"improvab",
  "isResolved":true,"isOutdated":false,"line":16,"originalLine":15,
  "path":"prototype-412/alpha.md","subjectType":"LINE"},
 {"first":"Blocking: (test fixture) subject — fixture beta as a whole; ",
  "isResolved":true,"isOutdated":false,"line":1,"originalLine":1,
  "path":"prototype-412/beta.md","subjectType":"FILE"},
 {"first":"Blocking: (test fixture) line 02b was inserted deliberately ",
  "isResolved":true,"isOutdated":true,"line":null,"originalLine":15,
  "path":"prototype-412/alpha.md","subjectType":"LINE"}]}
```

### B1. A `COMMENT`-verdict self-review is accepted; `REQUEST_CHANGES` on one's own PR is refused (422)

**FRESH** — #412, verbatim 422 (`Review Can not request changes on your own pull
request`). The single-account assumption holds.

### B2. Inline comments open resolvable threads; severity-as-first-word is plain text

**PROBED HERE — CONFIRMED** (fresh record: #412). Four threads on PR #414, each
first comment opening with `Blocking:` or `Suggestion:` as ordinary text, all
resolvable — no platform involvement in the severity convention.

### B3. File-level findings ride a standalone `subject_type=file` comment beside the cycle's review

**PROBED HERE — CONFIRMED** (fresh record: #412 deviation 1 — the create-review
`comments[]` array rejects `subject_type` with HTTP 422). PR #414 carries a live
`"subjectType":"FILE"` thread on `prototype-412/beta.md`, resolvable and
replyable like any LINE thread.

### B4. Thread resolution via GraphQL `resolveReviewThread` (REST has no resolve)

**PROBED HERE — CONFIRMED** (fresh record: #412). All four threads read back
`isResolved: true`, across both LINE and FILE subject types.

### B5. The soft merge gate is one GraphQL unresolved-thread read

**PROBED HERE — CONFIRMED.** The query above *is* that read, run from an agent's
Bash with the repo's own credentials: `totalCount: 4`, unresolved `0`. The gate
#409 §2 specifies is executable in one call and returns a countable answer.

### B6. A verified fix outdates its thread — `isOutdated: true`, `line: null`, `originalLine` survives

**PROBED HERE — CONFIRMED independently.** #412 deviation 2 named this as the
accommodation delta re-review must key on. Re-observed above on a PR untouched
since: two threads `isOutdated: true` with `line: null` and `originalLine` 13 and
15 intact; one thread that merely drifted below an insertion kept a live
`line: 16` against `originalLine: 15` and did **not** go outdated. #409's rule —
the verifying reviewer keys on `path` + `originalLine` + comment text, never on
live `line` — is measured-correct on a second, independent observation.

### B7. After a rebase the REST compare endpoint is misleading; local git is truthful

**FRESH** — #412 deviation 3 (compare reported `diverged` listing all files while
the true content delta was empty). Not re-run: it needs another rebase/force-push
on a throwaway PR, which would mutate #412's preserved artifact. #409 §2's "full
re-read only after a rebase" stands on it.

### B8. The four-section PR body survives a `gh pr edit` whole-body read-modify-write

**FRESH** — #412, including `## Suggestion dispositions` carrying
`Declined (no-consequence)` lines with thread links.

### B9. A body-only `COMMENT` review (no inline comments) is valid

**FRESH** — #412 (cycle 3's converging review was one). Needed by #409 §2's
converging cycle and by `## Unanchored findings`.

### B10. Builder replies ride REST `…/comments/{first-comment-databaseId}/replies`

**FRESH** — #412. Backs #409 §2's "the builder never resolves a thread — it
replies `Fixed in <sha>`".

### B11. `gh pr diff --name-only` yields the PR's changed-file list

**PROBED HERE — CONFIRMED.** #409 §4's fourth disposition dimension ("Touches new
files") is defined as comparing the fix's file list against
`gh pr diff --name-only`, a command #412 never exercised.

```
$ gh pr diff 414 --repo GeoffNordling/dev-playbook --name-only
index.md
prototype-412/alpha.md
prototype-412/beta.md
prototype-412/index.md
prototype-412/procedure.md
```

A plain path list, one per line, from an agent's Bash — mechanically comparable,
no parsing beyond splitting lines. The dimension is checkable exactly as written.

### B12. Resolved threads render collapsed at the merge read

**NOT MEASURABLE FROM HERE.** #409 §6 justifies the `## Suggestion dispositions`
section with "what keeps dispositions visible at the merge read despite resolved
threads rendering collapsed". That is a **web-UI rendering** claim; the API
exposes `isResolved`, not how GitHub paints it. #412 deliberately left PR #414
open "so the threads render in review tooling" — the user settles it in one
look. Low stakes: the section is cheap and the claim only motivates it.

### B13. The `origin:deferral` label does not exist yet — the labels ripple is real work

**PROBED HERE — CONFIRMED.** #409 §7 requires adding an `origin` dimension to
`label_scheme.json` and re-running `bootstrap-labels` in consumer repos.

`src/dev_playbook/label_scheme.json` today carries exactly five dimensions:
`category` (maintenance, extension), `mode` (direct, spike), `tests` (yes, no),
`phase` (intake, design, spike, build, pr-review), `wayfinder` (map, research,
prototype, grilling, task). No `origin`.

`gh label list --repo GeoffNordling/dev-playbook` returns 16 labels — the
cross-product of those dimensions — and no `origin:*`.

**CONFIRMED**: the deferral stubs' label does not exist, `phase:intake` (the
stub's phase) does, and the ripple is genuine un-done work with a located file.

### B14. The brief-shape lint and `issue-authoring.md` must gain `Prohibited surfaces`

**PROBED HERE — CONFIRMED, with one wording delta.** The lint id is real —
`src/dev_playbook/workspace_lint.py:75`,
`ISSUE_BRIEF_SHAPE = "tracking.issue-brief-shape"` — and its build-brief heading
tuple is:

```python
BUILD_HEADINGS = (
    "Summary", "User intent", "Current behavior", "Desired behavior",
    "Key interfaces", "Acceptance criteria", "Out of scope",
)
```

with the comment above it stating the contract: "standards/tracking/issue-authoring.md
states them — the doc and this rule read one contract and cannot disagree."

**CONFIRMED**: adding `Prohibited surfaces` is a located, mechanical change
(seven headings → eight, plus the standard's text).

**Delta worth fixing in #409's text**: §1 lists the brief's binding sections as
`Acceptance criteria`, `Desired behavior`, `Out of scope`, `Prohibited surfaces`,
`Artifacts` — but `Artifacts` is **not** one of the seven required build
headings; it appears in the lint only as an optional approved-artifact section.
Citing a breach of `Artifacts` as Blocking would cite a section a brief is not
required to have. Either the lint gains it too, or #409's binding list drops it.

### B15. Today's deviation contract is single-lane: halt, commit, escalate, three limiters

**PROBED HERE — CONFIRMED.** `software-factory/deviation-contract.md`, verbatim:
the three limiters ("Does the fix change an acceptance criterion of the issue?",
"Does the fix touch a surface the brief declared out of scope?", "Does the fix
contradict a decision recorded on the issue, PR, an epic's standing rulings, or a
map?"), then "Three no's — make the fix and log it in the deviation ledger. Any
yes — escalate. **An answer the agent cannot give cleanly counts as yes**", then
"On any yes: stop work, commit what is done so the branch holds it, and post one
structured comment … to the PR if one exists, otherwise to the issue".

**CONFIRMED**: #409 §5's "today's deviation contract byte-for-byte" for the
builder's lane is accurate, and the file is single-lane as the ticket says — the
PR-callout lane is genuinely new text, and the manager's routing test genuinely
mirrors the limiters' three-question shape.

### B16. A halting agent's commit and push land through red gates with `--no-verify`

**PROBED HERE — CONFIRMED.** #409 §5's "the halt's commit always lands" depends
on `--no-verify` actually bypassing a refusing gate. dev-playbook installs both
hook types (`.git/hooks/pre-commit`, `.git/hooks/pre-push`, from
`.pre-commit-config.yaml`'s `default_install_hook_types: [pre-commit, pre-push]`),
so the case is live.

Setup: throwaway repo pair in the session scratchpad (working clone + bare
origin), each hook a two-line script printing to stderr and exiting 1.

```
$ git … commit -m "probe commit"
PRE-COMMIT GATE RED (probe 410)
rc=1

$ git … commit --no-verify -m "probe commit no-verify"
[master (root-commit) 12dc5e7] probe commit no-verify
 1 file changed, 1 insertion(+)
rc=0

$ git … push origin master
PRE-PUSH GATE RED (probe 410)
error: failed to push some refs to '…/origin.git'
rc=1

$ git … push --no-verify origin master
To …/origin.git
 * [new branch]      master -> master
rc=0
```

**CONFIRMED at both gates.** Scope caveat that matters to the design:
`--no-verify` bypasses **local** hooks only. A server-side refusal — branch
protection, or the PAT permission of A19 — is untouched by it. Consistent with
#409, which escalates on any push refusal regardless; and it is why the escape
hatch cannot be assumed to always work.

### B17. Every artifact #409 §7 lists as changing exists today

**PROBED HERE — CONFIRMED.** `software-factory/` holds `review-contract.md`,
`deviation-contract.md`, `factory-operations.md`, `user-checkpoints.md`,
`pr-feedback.md`, `node-skill-authoring.md` (plus `index.md`, `README.md`,
`refactor-catalogue.md`, `software-factory.md`); `standards/tracking/issue-authoring.md`
and `src/dev_playbook/label_scheme.json` exist; the skills `bug-pr-review`,
`code-pr-review`, `doc-pr-review`, `build`, `open-pr` and the retiring
`issue-overwatch` all exist under `dotfiles/dot-claude/skills/`. No row of §7's
table names a file that is not there.

### B18. The phase label is a usable program counter

**PROBED HERE — CONFIRMED.** The live repo carries `phase:intake`,
`phase:design`, `phase:spike`, `phase:build`, `phase:pr-review` — exactly the
phases #408's relaunch-fresh recovery re-derives from — alongside the
`mode:`/`tests:`/`category:` dimensions of the state tuple. Reading and writing
them is ordinary `gh issue` work this session exercised throughout.

### B19. The measured burden — 39 review-agent runs across 7 PRs, ~40 findings distilled to 6 ruled items

**NOT RE-MEASURED.** Calibration context in #409's question, not a fact its
rulings turn on; no ruling changes if the numbers move. The store to re-derive it
from exists (A20) should anyone want it audited.

---

## Part 3 — #419-scope facts

[#419](https://github.com/GeoffNordling/dev-playbook/issues/419) is measuring the
workspace-root arrangements in parallel. Each fact below records what this
repo-rooted session could see and what it could not. Nothing here is guessed.

### W1. Workspace-root settings resolution — where the factory's permission config lives

**DEFERRED to #419** — and **NOT MEASURABLE FROM HERE for a second reason worth
flagging**: under this session's sandbox the whole `~/workspace/.claude/` tree
reads back as masked device nodes, not files:

```
$ ls -la /home/geoff/workspace/.claude
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 agents
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 commands
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 hooks
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 settings.json
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 skills
crw-rw-rw-. 1 nobody nobody 1, 3 Aug 12 09:48 workflows
-rw-r--r--. 1 geoff  geoff  3401 Aug  3 10:32 settings.local.json
```

Those are the sandbox's write-deny masks (`/dev/null`, major 1 minor 3), so their
real contents are unreadable from inside the jail — an agent under this sandbox
profile reading workspace-scope config would read *nothing*, not the real file.
If the factory's config is to live at `~/workspace/.claude/settings.json`, #419
should check whether the factory's own agents can read it under the live sandbox
profile, not only whether the harness resolves it.

### W2. `gh` repo inference away from a clone

**DEFERRED to #419.** Not measurable from here: this session's Bash cwd is pinned
to the repo root and a `cd` does not survive to the next call (A11), so a
no-clone cwd is unreachable without chaining `cd` into every command — not the
arrangement #419 needs. Overlapping observation: **every** `gh` call in this
session passed an explicit `--repo GeoffNordling/dev-playbook` or an explicit
`repos/{owner}/{repo}` API path, and all succeeded — so the mitigation the
factory would use is exercised, from a cwd that would have inferred correctly
anyway.

### W3. User-scope agent definitions (`~/.claude/agents`)

**DEFERRED to #419**, with one free observation confirming #418's note:

```
$ ls /home/geoff/.claude/agents
ls: cannot access '/home/geoff/.claude/agents': No such file or directory
```

The directory does not exist today, so the dotfiles route for definitions is
un-exercised; whether a user-scope definition resolves from a workspace-rooted
session is #419's to measure.

### W4. Node placement from the workspace root

**DEFERRED to #419** — but A11's refutation applies at *any* root and sharpens
what #419 must probe: the question is not "does a node's `cd` reach the
worktree", it is "does the node re-assert the path on every call". Recommend
#419's node-shaped probes assert placement across at least two Bash calls.

### W5. Repo-guidance non-injection at the workspace root

**DEFERRED to #419.** Not measurable from here: this session is repo-rooted, so
dev-playbook's `CLAUDE.md` and project settings *are* injected; measuring an
absence needs a session rooted elsewhere, and launching one is exactly the
headless probe the user ruled out.

### W6. A misplaced node's file writes and git acts from the workspace root

**DEFERRED to #419** for the write half; the git half is **re-confirmed here at
2.1.229**, since it is #418's fail-faster rationale and #408 §1 quotes it:

```
$ git -C /home/geoff/workspace status
fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).
rc=128
```

Loud, immediate, non-zero. Not measured here: the write half — a misplaced node's
`Write` to a relative path from the workspace root, which A10 shows is fenced
nowhere and would simply land. That is #419's.

---

## Part 4 — disposition

**Back to [#408](https://github.com/GeoffNordling/dev-playbook/issues/408)'s
grilling ticket:**

1. **A11** — "placement by instruction: first act is `cd` plus a placement
   self-check" is refuted as *persistent* placement. The ruling (unfenced nodes,
   placed by instruction) survives; its instruction shape must become per-call
   path assertion, and §3's sentence needs rewriting before the epic quotes it.
2. **A21** — §6's "`agent_type`/`agent_id` on hook events give the accounting
   join its keys" is refuted for `agent_type` on `SubagentStop`; the join keys on
   `agent_id`, type resolved from `SubagentStart`. Affects
   [#411](https://github.com/GeoffNordling/dev-playbook/issues/411) and
   [#417](https://github.com/GeoffNordling/dev-playbook/issues/417).
3. **A24** — a stalled issue manager cannot be reaped by the factory manager
   (`TaskStop` refuses across the ownership boundary) and may wake hours later
   and finish. Relaunch-fresh needs a double-dispatch answer and a
   superseded-run check; feeds
   [#416](https://github.com/GeoffNordling/dev-playbook/issues/416).
4. **A2 / A3** — pin `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` rather than ride a
   remotely-served default; size the parallel fast-follow against
   `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` *and* the newly-surfaced
   `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`.
5. **A14** — an `Agent`-less definition disables spawning for its whole subtree,
   not only itself; the tools-list requirement is per-tier.
6. **A19** — soften the PAT claim to "may be refused by the PAT's Workflows
   permission"; and note the credential expires 2026-08-23.
7. **A23** — "reviewer definitions carry `disallowed-tools`" is unverified for
   agent definitions; verify when the first one is written.

**Back to [#409](https://github.com/GeoffNordling/dev-playbook/issues/409):**
nothing refuted. One text fix — **B14**: §1's binding-section list names
`Artifacts`, which the brief-shape lint does not require; drop it from the
Blocking-citeable list, or add it to the lint.

**Still open, honestly:** A9 (the path form's subagent-eligibility refusal —
this session's probe hit an existence check instead; #415's record stands), A5 (workflow nesting — unreachable from a subagent,
immaterial to the ruled design), A18 (worktree sweep eligibility — needs a
multi-day observation), A19 (PAT workflow push — needs a mutating push), B7
(post-rebase compare — needs another rebase), B12 (collapsed-thread rendering —
needs the user's eye on PR #414), and the six #419 arrangements.
