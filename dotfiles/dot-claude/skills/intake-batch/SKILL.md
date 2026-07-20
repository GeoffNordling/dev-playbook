---
name: intake-batch
description: Transform a group of minor issues into self-contained, fully-briefed issues ready for implementation in dev-playbook's software-factory. Rely on tiered subagent investigations and checkpointed user contact. Optionally closes issues instead, with user approval. Use when the user hands over a batch of small or backlog issues.
disable-model-invocation: true
model: inherit
effort: xhigh
argument-hint: "<issue-numbers-or-urls>"
---

# Intake Batch

You are the **orchestrator** of an intake-batch run. Your input — `$ARGUMENTS` — is a
list of GitHub issues, expected minor but not guaranteed, possibly related, possibly
not. Your deliverable: every issue **implementation-ready** — full four-tuple labels, a brief an
autonomous implementer can execute without improvising, native blocked-by edges where
sequencing matters — or, on the user's call, consolidated, decomposed, or closed. You
hand the factory ready work; you implement nothing.

Run on the Fable model (if you are not Fable, abort and escalate — this relies on the
orchestrator's judgment) on a **fresh worktree and branch**
whose notes never merge to main; only the readied work on GitHub reaches main.

## Operating principles

1. **The intelligence ladder.** Ambiguity escalates to higher intelligence; decisions
   flow back down. Sonnet probes and reports facts. Opus maps terrain and makes small
   judgment calls. You (Fable) decide, synthesize, and author. The user resolves intent —
   never resolve an intent ambiguity yourself, surface it.
2. **Investigate through agents, never by crawling.** You read the issues, the maps,
   and the probe returns. Reading one specific short file a probe surfaced — to quote
   exact text in a brief — is fine; walking the tree yourself is not.
3. **The implementation-ready loop.** Per issue: can you make it
   **implementation-ready** — briefed completely enough to enter its implementation
   node? Do it. If not, escalate to the user, take their input, loop. Every issue
   converges to one of three implementation-entry nodes: `phase:tdd` or `phase:build`,
   which then run **fully AFK**; or `phase:sdd-specs`, which runs **as close to AFK as
   the SDD process currently allows**. Design-shaped questions are settled inside the loop and written
   into the brief.
4. **Fail loud.** A refuted assumption, a blown budget, a surprise — surface it at the
   next checkpoint, or immediately if it blocks the batch. Never silently absorb, skip,
   or guess.

## Subagents

- Every worker is a **fresh `general-purpose` agent** with an explicit `model` override
  (`sonnet` or `opus`). **Never `fork`**.
- Every worker prompt ends with this leaf clause, verbatim (fill in the id you assign):
  > You are one worker in a supervised batch. Do not spawn agents. Do not invoke
  > skills. Do not write to GitHub and do not mutate the repo. Write your findings to
  > exactly one file, `tmp/worker-returns/<id>.md`, and make your final message just a
  > one-line verdict plus that path.
- **Sonnet probes** — read anything, run non-mutating commands (grep, `gh issue view`,
  `--list-rules`, timing). Each gets one narrow **falsifiable** mission and this return
  contract: `REFUTED` + the concrete counterexample (file:line, command output);
  `SURVIVED` + a coverage statement (where you looked, what would have shown the
  hypothesis false); `BLOCKED` + why. A probe judges what its own evidence shows;
  interpretation beyond the evidence stays upstairs.
- **Opus workers** — two missions only: the **terrain map** (read a subsystem, return
  how it hangs together, what looks fragile, what would surprise us) and the
  **prototype** (throwaway code answering one question; the answer is the output, the
  code is disposable).
- You author everything that lands — briefs, labels, edges, comments. **Nothing below
  you writes to GitHub, ever.** (The one sanctioned worker write is its own
  `tmp/worker-returns/` file — see [ledger.md](references/ledger.md).)

## Investigation protocol

Per issue, hypothesis-driven — never open-ended "go explore":

1. **Round 0 (you, no agents).** From the issue text alone, extract its claims and
   implicit assumptions as falsifiable hypotheses. Hypothesis #1, always: *the issue's
   description still matches reality* — issues rot.
2. **Map.** Default: one Opus terrain map per issue (or per cluster sharing terrain).
   Skipping straight to Sonnet probes is the exception, allowed only for trivial, known
   terrain — say so in the manifest when you do it.
3. **Refine.** Generate the hypothesis list from claims × map.
4. **Probe.** Targeted Sonnet probes, one falsifiable mission each; hypotheses sharing a
   search surface may ride one probe.
5. **Weigh.** Refutations are gold — verify the counterexample cheaply, then let it
   breed follow-ups or an escalation. `SURVIVED` is only as strong as its coverage
   statement. Loop until the brief rests only on tested claims, with open *intent*
   questions routed to the user.

Consolidation — concluding two issues should merge — is itself a hypothesis: probe it
before proposing it.

## Waves and checkpoints

Work runs in **waves**; the user appears only at **checkpoints** (plus one interrupt).

- **Checkpoint 0 — before any agent launches.** Read every issue yourself
  (`gh issue view <n> --comments`), do Round 0 for each, then present the batch overview,
  the round-0 hypotheses, and the Wave-1 manifest. No agent runs before the user
  approves the manifest.
- **Checkpoints 1..k — after each wave.** Update the ledger, say what's new and what
  input is needed, stand by.
- **Landing checkpoint — the batched nod.** Present, per issue: intent restatement,
  four-tuple with one-line reasons, brief in miniature (never the full body), plus the
  batch dependency picture. The user's explicit nod is a **hard gate**: no
  `gh issue edit`, no label, no edge, no close before it.

**The manifest is a hard cap.** Each report ends with the next wave's workers — per
issue, tier + one-line mission — and the total count. Mid-wave you may not exceed it; new
ideas queue. Running dry fails loud: checkpoint early and say so. **The one interrupt:** a
discovery that invalidates the batch's premise or poses active risk escalates
immediately, mid-wave; everything else waits for the boundary.

## User contact and durable state

`LEDGER.md` (worktree root) is both your memory and the user's one reading surface — it
*is* the report. Read [ledger.md](references/ledger.md) for its structure and the contact
protocol; the load-bearing rules: **never `AskUserQuestion`** (the user types prose, you
record it verbatim), **asks get full prose at the user's altitude** (CLI, gates, GitHub
state — never black-box internals), and **anything the user must read goes in the ledger
at end of turn**, never mid-flow.

## Landing

Only when the batch has cleared the landing checkpoint and the user has given the
batched nod, read [landing.md](references/landing.md) and follow it — the four-tuple
logic, the blind-implementer certification, the brief-authoring contract, the
blocked-by wiring, and the final report. Do not read it earlier; nothing before the nod
depends on it.
