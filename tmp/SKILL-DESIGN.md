# SKILL-DESIGN: Backlog-Grooming Orchestrator

Status: DRAFT — under active grilling. Resolved decisions accumulate below;
unresolved questions remain at the bottom.

## Resolved decisions

### D1 — Position in the factory: a batch front door

The skill is a **batch variant of intake, subsuming it for issue groups** — not
a pre-intake research pass. For each issue in the batch it investigates, then
writes the four-tuple and brief itself, landing the issue at its first work
node. `/intake` remains the door for single fresh ideas. Precedent: design's
decompose exit already mints ready leaves in place without a round-trip
through intake.

Additional deliverable beyond per-issue readiness: a **cross-batch dependency
analysis** for parallelization. Dependencies are wired as native GitHub
blocked-by relationships (never labels — per the tracking standard). If the
batch is fully parallel, no edges are wired; the absence is itself a finding
the report states.

Cost accepted: the skill must honor intake's full contract — four-tuple
correctness, brief format per issue conventions, and a human nod before any
`gh issue edit` — with the consolidated cadence report playing the role of
intake's per-issue confirmation gate.

### D2 — Convergence model: the AFK-ready loop

Per issue, grooming is one loop:

1. Can the orchestrator make the issue AFK-ready? If yes — do it.
2. If not — escalate to the human, receive input, go back to 1.

Every issue converges to AFK-ready; there is no separate exit taxonomy.
The richer outcomes are expressions of the loop, not extra exits:

- **Epic** — the "tiny issue was actually big" discovery is escalated; the
  human's input authorizes decomposition; the children then run the same loop.
- **Spike as tool** — the orchestrator is always authorized to run spike-style
  investigations itself as part of making an issue AFK-ready.
- **Spike as issue** — minting a `mode:spike` issue requires human approval
  (initial policy; may loosen as trust builds).
- **Close** — an issue dissolved by investigation is an escalation with a
  recommend-close; the human's input closes it.

`phase:design` is not a normal grooming exit: design-shaped decisions are
resolved through the escalation loop (human intent in, orchestrator encodes it
into the brief), not deferred to a downstream HITL node.

### D3 — Checkpoint structure: wave boundaries + one narrow interrupt

Waves are the spine. The orchestrator runs a whole wave autonomously —
learning, deciding, preparing — then stops at a planned checkpoint with one
consolidated report: per-issue verdicts, all escalation questions batched,
recommendation-first. The human answers everything in one sitting; answers
cross-pollinate across issues. Issues whose answers spawn new questions cycle
back and ride the next checkpoint.

The one exception: an **unexpected blocking discovery** — something that
invalidates the batch's premise or poses active risk — is escalated
immediately, mid-wave. Everything else waits for the boundary.

The batched nod at the landing checkpoint replaces intake's per-issue hard
gate: one message covering every issue (intent + four-tuple + brief in
miniature), one explicit "land them" from the human before any GitHub write.

### D4 — The intelligence ladder, and who reads what

Guiding principle: **ambiguity escalates to higher intelligence; decisions
flow back down.** The ladder is Sonnet → Opus → Fable → human. The Fable
orchestrator — like the human — does not look directly at the whole system; it
probes through the tools and agents available to it, then decides.

Operational consequences:

- The orchestrator **personally reads every issue in the batch first**, so it
  holds the total scope before delegating anything.
- Sonnet agents probe the system — codebase investigation, scope reading,
  cross-reference chasing — and return findings, never decisions.
- **Consolidation authority**: holding the whole batch, the orchestrator may
  decide overlapping issues should merge. That decision is itself
  evidence-driven — it may dispatch a further Sonnet investigation to test
  whether consolidation is actually sound before committing to it.
- The `/intake` skill is **not invoked** — it was designed for high-effort
  HITL sessions. The orchestrator authors the batch's issues itself, honoring
  intake's output contract (D1) without its interview process.

### D5 — Tier rules, operationalized

The original "Opus writes code" framing was an example of a tier —
small-decision intelligence — not a task list. For grooming:

1. **Sonnet = probes.** May read anything and execute non-mutating commands
   (greps, `gh issue view`, `--list-rules`, timing runs). "Read-only" means
   no repo mutation and no GitHub write — not "no execution." Returns
   structured findings; never decides.
2. **Opus = the spike hands.** Activates only when an investigation must
   write throwaway code — a prototype, a benchmark harness. The code is
   disposable; the answer is the output. A batch where Opus never appears is
   fine, not a gap. Grooming *should* use spikes and prototypes where they
   settle questions — dispatching one is Fable's decision.
3. **Fable = decisions + all authorship.** Briefs, four-tuples, consolidation
   calls, dependency analysis, every GitHub write (post-nod). Nothing below
   Fable writes to GitHub — preserving workflow.md's single-label-writer
   principle: the batch session is the writing session.
4. **Subagent mechanics (#199 scar tissue).** Every worker is a fresh
   zero-context `general-purpose` agent with an explicit `model` override —
   never `fork`. Every worker prompt carries a leaf clause: "You are one
   worker in a batch; do not spawn agents, do not invoke skills; return
   findings as your final message."

### D6 — Durable state: the batch ledger

One markdown ledger file (`BATCH.md`, worktree root) the orchestrator
maintains continuously: per-issue stage
(`queued → investigating → blocked-on-human → ready-to-land → landed`),
findings digest, open questions, and human-ratified decisions **verbatim**.
The checkpoint report is a view of the ledger; recovery after `/clear` or
compaction is "read the ledger, resume." (Ralph-loop pattern: disk is the
memory.)

The ledger is **committed** as the batch progresses — the batch runs on its
own worktree and branch, so commits are cheap and give the experiment a
history — but the branch's ledger commits **never merge to main**; the ledger
is deleted when the batch closes.

An explicit decision-graph notation was considered and **parked**: ceremony
ahead of knowledge. If attempt 1's ledger keeps wanting to be a graph,
v2 gets one.

### D7 — Investigation protocol: falsifiable hypotheses

Investigation is organized around **falsifiable hypotheses**, not open-ended
exploration. The asymmetry that makes the intelligence ladder trustworthy:
**a refutation travels upward as checkable evidence** (a concrete
counterexample Fable can confirm in seconds), while understanding is
expensive to generate. Probes are verification-shaped because that is what
cheap models are good at.

Per issue:

1. **Fable, round 0** — from issue text alone, extract the issue's claims and
   implicit assumptions as hypotheses. Hypothesis #1, always: *the issue's
   description still matches reality* (issues rot).
2. **Opus map — the default intermediary.** For most issues, at least one
   Opus agent produces a medium-level opinionated map of the terrain (how the
   subsystem hangs together, what looks fragile, what would surprise us).
   Mapping-with-salience is small-decision intelligence — Opus-tier by
   definition. Skipping straight from issue text to Sonnet probes is the
   exception, permitted only for genuinely trivial, known terrain.
3. **Fable** — generate/refine hypotheses from claims × map.
4. **Targeted Sonnet probes** — narrow falsifiable missions with a
   three-valued return contract: `REFUTED` + counterexample;
   `SURVIVED` + coverage statement (where I looked — Fable judges adequacy);
   `BLOCKED` + why. Hypotheses sharing a search surface may ride one probe.
5. **Fable** — weigh; refutations breed follow-up hypotheses or escalations;
   loop until the brief rests only on tested claims and open *intent*
   ambiguities go to the human.

**Fable investigates through agents, never by crawling.** The orchestrator
does not read the repo at large; it reads issues, maps, and probe returns.
Reading a specific short file a probe surfaced (to quote exact text in a
brief) is using a tool; crawling the tree is the anti-pattern. The salience
caution is accepted and managed by tier choice: any mapper's judgment gates
the hypothesis space above it, so unfamiliar or treacherous terrain gets the
smarter mapper.

### D8 — Compute guard: the wave manifest

Hypothesis rounds compound; the fan-out could quietly explode. The guard is
HITL budget approval at each checkpoint:

- Every checkpoint report ends with the **next wave's manifest**: per-issue
  planned probes (tier + one-line mission), and the total agent count.
  The human approves or trims before launch.
- Mid-wave, the approved manifest is a **hard cap**. Discoveries that warrant
  more probes queue for the next manifest; only a batch-blocking discovery
  uses the immediate-escalation channel (D3).
- Running dry mid-wave fails loud: checkpoint early with partial results,
  never silently exceed.
- Consequence: **Checkpoint 0 precedes any agent launch** — the session's
  first act is reading the batch, round-0 hypotheses, and a Wave-1 manifest
  for approval. The human's "I expected 3 agents, not 12" moment happens
  before the spend, not after (#199, prevention item 3, made structural).

### D9 — Checkpoint report format

A view of the ledger, in four parts:

1. **Per-issue block** — verdict (`AFK-ready` / `needs your call` /
   `recommend close` / `recommend merge into #X` / `bigger than it looks`);
   the **hypothesis table** (claim · status · one-line evidence); the ask,
   recommendation-first; and a **"decided without you"** line per autonomous
   call, so silent decisions stay cheaply vetoable.
2. **Batch-level** — proposed blocked-by edges (or "fully parallel");
   consolidation proposals with evidence; cross-cutting discoveries.
3. **Next wave's manifest** (D8), closing with the approval ask.
4. **Answer mechanics** — crisp decisions as `AskUserQuestion` batches,
   recommendation as first option; answers land in the ledger verbatim
   before work resumes.

### D10 — Cycle discipline: no retro layer

At the end of the design session the skill is written, then executed clean.
No in-run retrospective instrumentation — the run's results and the human's
experience of it are the feedback; revision happens after, from those.

### D11 — Name and artifact form

The skill is named **`intake-batch`** — the batch entrance of the factory's
existing front door, self-documenting against `intake`. (Considered:
`groom`/`batch-groom` — rejected, backlog implication too narrow;
`batch-refine` — industry term but reads as code-refining; `fledge` —
metaphor tax.)

For attempt 1 it is a self-contained procedure doc, `INTAKE-BATCH.md`, at the
batch worktree root — not a registry skill. The clean run is a **fresh
session** (top model, this worktree) whose launch prompt is "Read
INTAKE-BATCH.md and execute it on issues …" — zero inherited context, the
honest test of the doc's completeness. Registry promotion
(`dotfiles/dot-claude/skills/intake-batch/`) only after the design survives
contact.

## The problem

Little groups of minor tasks accumulate (e.g. GitHub issues #208, #207, #199,
#184, #183, #171, #169). As a rule they are *expected* to be minor in scope and
effort — but software engineering surprises you, and a tiny issue can become a
big one once you start poking around. The only time we truly understand how
difficult an issue was is when we've finished it.

Two constraints rule out the reliable-but-expensive baseline (top model +
human-in-the-loop on every issue):

1. **Not enough compute** to run the top model (Fable) on everything.
2. **Not enough human time** to hold any model's hand through every issue.

## The experiment

Trust a top-model **orchestrator** (Fable, today) to work through a batch of
minor issues with the *minimum* human contact needed to preserve intent and
steering. Two — and only two — check-in channels:

1. **Planned cadence** — the orchestrator presents organized, planned reports
   designed to extract the human's feedback and steer intent.
2. **Escalation** — on encountering something unexpected, the orchestrator
   pauses that thread of work and escalates to the human.

## Model tiering (delegation policy)

The orchestrator delegates downward by decision weight:

| Tier | Model | Work |
|------|-------|------|
| Read-only, no decisions | Sonnet 5 | research, codebase exploration |
| Small decisions | Opus | writing code, reviewing code |
| Large decisions | Fable (orchestrator itself) | synthesis, judgment calls — or escalate/present to the human |

## Scope of THIS prototype session

Not implementation. The deliverable of this session's workflow is
**transformed issues**: each nascent minor backlog issue becomes a fully
fleshed out, fully specified GitHub issue ready to hand off to the software
factory (workflow.md). The orchestrator (this session) uses Opus and Sonnet
subagents to spike, explore, and investigate — then writes the specification
back into the issue.

One chat = the grooming pass over the batch. Implementation happens later,
per-issue, in the factory.

## Open design questions (for the grilling session)

- What artifacts define the skill? A single SKILL.md? Supporting markdown
  files? An explicit graph structure of decision-making and agent management?
- What does the planned-cadence report look like — format, frequency, content?
- What triggers escalation vs. orchestrator judgment? Where is the line
  between "small" and "large" decision making, operationally?
- How does a subagent signal "this issue is bigger than it looks" upward?
- What is the per-issue output contract — what does "fully specified, ready
  for the factory" mean, concretely? (Relation to the existing intake /
  fill-issue-gaps skills?)
- Batch mechanics: issues processed serially, in parallel waves, or
  opportunistically?
- Cycle plan: attempt → retrospect → revise skill. What do we capture during
  the attempt to make the retrospective useful?
