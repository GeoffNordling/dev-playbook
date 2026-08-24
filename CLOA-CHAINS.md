---
type: General-Sheet
title: CLOA Chains
description: The ledger of finalized reference chains — one recorded entry per unit, written down as it is ruled
---

# CLOA Chains

Every finalized Reference chain, recorded at ruling time in the notation
[CLOA Abstractions](/CLOA-ABSTRACTIONS.md) defines, so the close-out ends
in a written ledger rather than compacted memory. An entry is the chain
plus its one-sentence carrier; the rulings that shaped it live in the
abstractions file.

Excluded units record no chain: `datasheet` (Instruments exclusion) and
`judgments-sweep` (Judgments exclusion).

## Bootstrap runs

### Run 1: document-deslop — zero residual

The chain, declared:

    [document-deslop] Skill
      └─does──► [deslopper] Agent (Read, Write)
                  ├─does──►  [slop-tics] Standard — .enforce
                  ├─reads──► [conventions] Standard
                  └ ╌ reads ╌ ╌ ► [writing-for-agents] Skill  agent-facing targets only

One sentence carries the target: document-deslop is the enforce arm of the
Slop Tics Standard — a Skill that resolves a hint to files and dispatches
the deslopper Agent once per file. Everything else in the two files — the
one-pass write rule, the DONE protocol, the rewrite rules — is internals
below the CLOA, the pandas method body, and is not residual.

What the run bought: the **do**-only verb rule for Agent and Skill, and the
first two edge labels. The enforce/consult distinction that first appeared
as residual dissolved into them — enforce is *does* the Standard's verb,
consult is merely *reads*.

### Run 2: grill-with-docs — the wrapped interview

The chain, declared:

    [grill-with-docs] Skill
      ├─does──► {grilling} Skill                the interview
      ├─does──► {domain-modeling} Skill         active throughout
      │           ├─reads──►  {CONTEXT-FORMAT} {ADR-FORMAT}
      │           └─writes──► CONTEXT.md, docs/decisions/*
      └─overrides {domain-modeling}'s ADR clause
          with──► [records] Standard

One sentence carries the target: grill-with-docs does grilling with
domain-modeling active throughout, overriding its decision-record clause
with the workspace's Decision Record Standard.

What the run bought: the generalized **does** edge, the **overrides**
edge, the ownership node type — the wrapper exists only because its
dependencies are vendored — and the definition-site rule for edge
assignment. Open: the **writes** edge (adopted in run 3).

### Run 3: design — the hub

The chain, declared (grill-with-docs's subtree is run 2's, reused by
reference):

    [design] Skill
      ├─reads──► [software-factory] [user-checkpoints]        Guides
      ├─reads──► [issue-authoring] [tracker-operations]       Standards
      ├─does──► {codebase-design} Skill              the lens, invoked first
      ├─does──► [grill-with-docs] Skill              subtree per run 2
      ├ ╌ does ╌ ╌ ► {prototype} Skill                    reading can't settle it
      ├ ╌ does ╌ ╌ ► [user-intent-mini-interview] Skill   a single-leaf write lands
      ├─does──► [issue-review-claims] Skill (no Write)      fresh-context subagent
      ├─does──► [issue-review-simulation] Skill (no Write)  fresh-context subagent
      └─writes─► issue brief, phase labels, probe-record comment, prototype/<issue> branch

One sentence carries the target: design turns an issue's rough brief into
a factory-ready one — or an epic with children — by grilling the approach
through the codebase-design lens, prototyping only what reading can't
settle, and writing the brief back audited by the two issue-review
lenses.

The chain absorbed two things cleanly. `references/design-it-twice.md`
and `references/decompose.md` are inside the unit — the skill is its
directory, so they are private functions, not chain nodes. And the old
mention-grep survey said design references eight skills; the declared
chain has six does edges — `intake` appears only in when-to-use prose,
and "research" is a word, not the skill. The gap between grep and
declaration is exactly what the import-linter parallel exists to close.

What the run bought: **writes** adopted, with targets typed as state; the
**guard** annotation blessed; permission expressions as node data; and
the context-binding correction to Agent and Skill — fresh context versus
calling context, not permission set alone.

Residuals tracked, unmodeled: the user as **soft guardian** — design
waits for "approved" before anything lands on GitHub, a wait, not a
permission boundary; and doc types held informal (see "Remembered, not
primitives").

## Empirical close-out

### ralph-setup

    [ralph-setup] Skill
      ├─reads───► [ralph-loop] Recipe-Description     mandatory first read
      ├─does────► [grill-with-docs] Skill             subtree per run 2
      ├ ╌ writes ╌ ╌ ► local file(PLAN.md, PROGRESS.md)    the user approved twice
      │                                                     and the gate is green
      └─returns─► launch_command: str    the ralph-loop Workflow launch — never runs it

One sentence carries the target: ralph-setup grills the plan into shape,
writes PLAN.md and PROGRESS.md from its bundled skeletons once approved
and the gate is green, then returns the Workflow launch command without
starting the loop.

### commit

    [commit] Skill · allowed-tools: Bash(git *), model: sonnet, effort: low
      ├─writes──► git(commit, push)
      └─returns─► outcome: str    enum: clean / files remain / push landed

One sentence carries the target: commit is a leaf — it stages this
conversation's work, commits, pushes, and returns a status.

### grilling

    {grilling} Skill
      ├ ╌ does ╌ ╌ ► sub-agent (unnamed, fresh context)   a question needs a
      │                                                    fact from the environment
      └─returns─► questions: str    each with a recommendation —
                   loops until the frontier is empty

One sentence carries the target: grilling is a pure conversation loop —
no reads, no writes; its only state is the question frontier it holds in
working memory (ledgered ephemeral state).

### orchestrate

    [orchestrate] Skill · model: inherit, effort: xhigh
      └─returns─► confirmation: str    orchestration mode is on

One sentence carries the target: orchestrate fires no other edge at
invocation — its whole body installs standing behavior ("everything
below you is a subagent") in the session's ephemeral context, the
ledgered behavior-mode residual.

### log-friction

    [log-friction] Skill · model: sonnet, effort: xhigh
      ├─args────► friction: str    the description, via $ARGUMENTS
      ├─reads───► mission-control/friction log          the entry format and
      │                                                  its repeat-bites rule
      ├ ╌ writes ╌ ╌ ► git(mission-control: commit, push)    something to record
      └─returns─► outcome: str    entry name + push landed | "nothing to record"

One sentence carries the target: log-friction appends one entry to
mission-control's friction log — the read and the write are the same
cross-repo document — and reports that the push landed.

### wizard

    {wizard} Skill
      ├ ╌ reads ╌ ╌ ► env/config/CI files            a setup
      ├ ╌ reads ╌ ╌ ► current-vs-target state        a migration
      ├─writes──► scratch                            the generated wizard script (default)
      ├ ╌ writes ╌ ╌ ► local file(script, README)    the user wants it repeatable
      ├ ╌ writes ╌ ╌ ► git(commit)                   the user wants it repeatable
      ├─returns─► stage_plan: str          for confirmation before authoring
      └─returns─► run_instructions: str    at handoff

One sentence carries the target: wizard authors a Workflow — deterministic
bash the user runs later; the script's own future writes (.env, GitHub
secrets) belong to that Workflow's chain, and this skill never runs it.

### skill-creator

    [skill-creator] Skill · model: opus, effort: xhigh
      ├─reads───► [skill-conventions] Standard    plus its checklist before done
      ├─does────► [writing-for-agents] Skill      in-context
      ├ ╌ overrides [writing-for-agents]'s craft guidance
      │    with ╌ ╌ ► [skill-conventions] Standard   they collide
      └─writes──► local file(new skill bundle)    project-local or cross-project home

One sentence carries the target: skill-creator writes a new node of this
very graph — a skill bundle authored against the conventions Standard,
with writing-for-agents active and overridden where the Standard
collides. No returns.
