---
type: General-Sheet
title: CLOA Chains
description: The ledger of finalized reference chains — one recorded entry per unit, written down as it is ruled
---

# CLOA Chains

Every finalized Reference chain, recorded at ruling time in the notation
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md) defines, so the close-out ends
in a written ledger rather than compacted memory. An entry is the chain
plus its one-sentence carrier; the rulings that shaped it live in the
abstractions file.

These chains exist as proof of concept — each one written to test
that the primitive set could express that unit's operations, and the
set held. The final traces are generated instead, from structure
embedded in the unit files themselves: that structure is ruled in
[Edge Encoding](/no-more-slop-branch-working-files/EDGE-ENCODING.md), and
`parser/chaingen.py` emits `parser/chains.txt` — the five covering-set
units so far, log-friction's entry below among them. The
close-out ended by ruling with 22 chains recorded: batches had
stopped producing ontology changes, and the thirteen units still
unread were ruled expressible with the existing primitives.

Excluded units record no chain: `datasheet` (Instruments exclusion) and
`judgments-sweep` (Judgments exclusion). Deleted units record no chain:
`orient` and `pymc-modeling`, removed from the workspace during the
close-out.

## Bootstrap runs

Bootstrap entries keep the notation of their era — written before
write typing and args/reports existed. Guard dashes were retrofitted;
the rest was not. The close-out entries onward use the final notation.

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
      │           └─writes──► CONTEXT.md, docs/adr/*
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
      └─reports─► launch_command: str    the ralph-loop Workflow launch — never runs it

One sentence carries the target: ralph-setup grills the plan into shape,
writes PLAN.md and PROGRESS.md from its bundled skeletons once approved
and the gate is green, then reports the Workflow launch command without
starting the loop.

### commit

    [commit] Skill · allowed-tools: Bash(git *), model: sonnet, effort: low
      ├─writes──► git(commit, push)
      └─reports─► outcome: str    enum: clean / files remain / push landed

One sentence carries the target: commit is a leaf — it stages this
conversation's work, commits, pushes, and reports a status.

### grilling

    {grilling} Skill
      ├ ╌ does ╌ ╌ ► sub-agent (unnamed, fresh context)   a question needs a
      │                                                    fact from the environment
      └─reports─► questions: str    each with a recommendation —
                   loops until the frontier is empty

One sentence carries the target: grilling is a pure conversation loop —
no reads, no writes; its only state is the question frontier it holds in
working memory (ledgered ephemeral state).

### orchestrate

    [orchestrate] Skill · model: inherit, effort: xhigh
      └─reports─► confirmation: str    orchestration mode is on

One sentence carries the target: orchestrate fires no other edge at
invocation — its whole body installs standing behavior ("everything
below you is a subagent") in the session's ephemeral context, the
ledgered behavior-mode residual.

### log-friction

    [log-friction] Skill · model: sonnet, effort: xhigh
      ├─args────► friction
      ├ ╌ reports ╌ ► outcome: str    that there is nothing to record    if there is genuinely nothing to record
      ├─reads───► friction/log.md
      ├ ╌ writes ╌ ► git(mission-control: add, commit, push)    and push    if there is something to record
      └─reports─► outcome: str    one line with the entry's short name, and that the push landed

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
      ├─reports─► stage_plan: str          for confirmation before authoring
      └─reports─► run_instructions: str    at handoff

One sentence carries the target: wizard authors a Script — deterministic
bash the user runs later; the script's own future writes (.env, GitHub
secrets) belong to that Script's chain, and this skill never runs it.

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
collides. No reports.

### candidate-promote

    [candidate-promote] Skill · model: inherit, effort: xhigh
      ├─args────► candidate    the entry name, via $ARGUMENTS —
      │                              asks if absent or ambiguous
      ├─reads───► CANDIDATES.md                   the parking lot, repo root
      ├─reads───► [candidates] Standard           the conventions contract
      ├─does────► [intake] Skill    in-context    the located entry as the
      │                                            free-form idea
      ├ ╌ writes ╌ ╌ ► local file(CANDIDATES.md)    intake reports the issue
      │                                              number — the entry is
      │                                              deleted, never before
      └─reports─► issue_number: int, removed_entries: list[str]

One sentence carries the target: candidate-promote owns the lookup and
the delete — authoring the issue is intake's job, and the entry leaves
CANDIDATES.md only after intake lands the issue. First recorded edge
into a parked factory unit; intake's own chain waits for the factory
phase.

### usage-report

    [usage-report] Skill · allowed-tools: Bash(bash *usage-report/scripts/report.sh), model: sonnet, effort: low
      └─does────► [report.sh] Script    in-bundle
                    └ ╌ reads ╌ ╌ ► ~/.cache/claude-code/usage.json    exits with a
                                                                        diagnosis rather
                                                                        than a guess

One sentence carries the target: usage-report is a thin shim around a
deterministic Script — the allowed-tools clamp permits exactly one
command, and the Script reads the usage cache and exits with a
diagnosis rather than a number it cannot stand behind. No writes
anywhere.

### research

    [research] Skill
      └─does────► research agent (unnamed, fresh context)
                    ├ ╌ reads ╌ ╌ ► primary sources — docs, source code,
                    │                specs    as needed
                    └─writes──► local file(findings .md)    where the repo
                                                             already keeps
                                                             such notes

One sentence carries the target: research spins one background agent
whose entire spec is this document — it reads primary sources, writes
one findings file into the repo, and hands nothing back to the caller.

### domain-modeling

    {domain-modeling} Skill
      ├ ╌ reads ╌ ╌ ► CONTEXT.md          challenging a term against the glossary
      ├ ╌ reads ╌ ╌ ► CONTEXT-MAP.md      it exists at repo root
      ├ ╌ reads ╌ ╌ ► source code         the user states how something works
      ├ ╌ reads ╌ ╌ ► {CONTEXT-FORMAT}    a term resolves
      ├ ╌ reads ╌ ╌ ► {ADR-FORMAT}        an ADR is offered
      ├ ╌ writes ╌ ╌ ► local file(CONTEXT.md)              a term is resolved
      └ ╌ writes ╌ ╌ ► local file(docs/adr/NNNN-slug.md)   all three ADR
                                                            criteria hold

One sentence carries the target: vanilla domain-modeling is fully
conditional — every edge guarded, no does-edges, its two writes the
glossary and an ADR; grill-with-docs vendors it and overrides the ADR
clause.

### diagnosing-bugs

    [diagnosing-bugs] Skill
      ├ ╌ reads ╌ ╌ ► CONTEXT.md                          it exists
      ├ ╌ reads ╌ ╌ ► docs/adr/*                          touching that area
      ├ ╌ writes ╌ ╌ ► local file(hitl loop script)       a user-run repro
      │                                                    step is the last
      │                                                    resort
      ├ ╌ does ╌ ╌ ► [hitl loop script] Script            same condition — the
      │                                                    user runs it, output
      │                                                    feeds the loop
      ├ ╌ writes ╌ ╌ ► local file(DEBUG instrumentation)  Phase 4 — reverted
      │                                                    in cleanup
      ├ ╌ writes ╌ ╌ ► local file(regression test)        a correct test seam
      │                                                    exists
      ├ ╌ writes ╌ ╌ ► scratch                            throwaway harnesses —
      │                                                    deleted in cleanup
      ├ ╌ writes ╌ ╌ ► git(commit)                        the confirmed
      │                                                    hypothesis lands in
      │                                                    the message
      └ ╌ does ╌ ╌ ► [improve-codebase-architecture] Skill   the root cause was
                                                             architectural — only
                                                             after the fix lands

One sentence carries the target: diagnosing-bugs is all guards — its
lasting writes are one regression test and one commit carrying the
confirmed hypothesis; everything else it writes, it reverts. Its
secret-redaction rule is a ledgered behavior-mode setting, not an edge.

### writing-for-agents

    [writing-for-agents] Skill
      (no edges)

One sentence carries the target: writing-for-agents is pure craft
guidance — its whole behavior is being active in the calling context;
its only read is its own bundled reference, collapsed by the zoom rule,
and other units do it (skill-creator) and override it where a Standard
collides.

### codebase-design

    {codebase-design} Skill
      ├ ╌ reads ╌ ╌ ► CONTEXT.md                          composing the sub-agent
      │                                                    briefs
      ├ ╌ does ╌ ╌ ► design agents ×3–4                   design-it-twice — parallel,
      │               (unnamed, fresh context)             one design constraint each
      ├ ╌ reports ╌ ╌ ► problem_space_explanation: str    before the fan-out
      └ ╌ reports ╌ ╌ ► comparison_and_recommendation: str    after the compare

One sentence carries the target: codebase-design is mostly vocabulary —
its one active move is the design-it-twice fan-out, three to four fresh
agents each pinned to a different design constraint, compared and
reported; the exact-term discipline it installs is a ledgered
behavior-mode setting.

### prototype

    {prototype} Skill
      ├─writes──► local file(demo)                logic HTML, or UI variants
      │                                            with a ?variant= switcher
      ├ ╌ writes ╌ ╌ ► scratch                    persistence is in question —
      │                                            named "PROTOTYPE — wipe me"
      ├ ╌ writes ╌ ╌ ► local file(real module)    the validated decision folds
      │                                            in; losing variants deleted
      ├─writes──► git(branch, commit)             the prototype lives out of main
      ├─writes──► GitHub(issue)                   context pointer to the branch,
      │                                            plus the settled verdict —
      │                                            there or in a commit
      └─reports─► demo: str    the file path or the variant URL

One sentence carries the target: prototype builds a throwaway demo,
hands the user its path or URL, and once the question is answered folds
the decision into real code — the demo itself always exits main on a
throwaway branch, pointered from the issue.

### improve-codebase-architecture

    [improve-codebase-architecture] Skill
      ├─reads───► CONTEXT.md                  the domain glossary
      ├─reads───► docs/adr/*                  decisions not to re-litigate
      ├─does────► {codebase-design} Skill     in-context — the vocabulary lens,
      │                                        loaded first
      ├─does────► exploration agent           walks the codebase for shallow
      │            (unnamed, fresh context)    modules and friction
      ├─writes──► scratch                     the HTML architecture report
      ├─reports─► report_path: str            told to the user and opened
      ├ ╌ does ╌ ╌ ► {grilling} Skill             the user picks a candidate
      └ ╌ does ╌ ╌ ► {domain-modeling} Skill      a new term needs the glossary,
                                                   or a rejection deserves an ADR

One sentence carries the target: improve-codebase-architecture is a
hub — the vocabulary lens loads first, a fresh explorer walks the code,
findings land as a scratch HTML report whose path is the reported
value, and every downstream edge waits on the user picking something up.

### handoff

    [handoff] Skill · model: opus, effort: medium
      ├─args────► focus    optional — the next session's focus,
      │                          via $ARGUMENTS
      ├─writes──► scratch                    the handoff document in OS temp —
      │                                       secrets redacted before writing
      ├─reports─► absolute_path: str
      └─reports─► resume_line: str    "Read /tmp/handoff-<name>.md and continue."

One sentence carries the target: handoff writes one scratch document
carrying the session's state and reports its path with a paste-ready
resume line; everything it cites is already in context, so it reads
nothing.

### update-standards-pin

    [update-standards-pin] Skill · model: opus, effort: xhigh
      ├─reads───► [distribution] Standard            the bump is the release
      ├─reads───► workspace_lint.py                  the GOVERNED roster
      ├─does────► [bump-pins] Script                 dry-run first, then
      │             │                                 mutating — shared
      │             │                                 scripts/, not in-bundle
      │             ├─reads───► consumer/.pre-commit-config.yaml    the pinned rev
      │             ├─writes──► local file(consumer: .pre-commit-config.yaml)
      │             └─reports─► status: str    enum: green / needs work /
      │                          already current / would bump /
      │                          skipped (four reasons)
      ├ ╌ does ╌ ╌ ► [enable-repo-governance] Skill    a repo has no pin
      ├ ╌ writes ╌ ╌ ► git(commit, push)               the finding is a defect
      │                                                 in the release itself
      ├ ╌ writes ╌ ╌ ► local file(consumer: edits, deletions)    adaptations
      │                                                           and retired
      │                                                           content
      ├─writes──► git(consumer: commit, push)          one commit per consumer —
      │                                                 pin move plus adaptation
      └─reports─► per_repo_report: str    plus escalation, skip, and
                   fault reports

One sentence carries the target: update-standards-pin walks the
GOVERNED roster doing the bump-pins Script per consumer and landing
one commit per repo — the first unit whose writes are mostly
consumer-prefixed, `consumer:` standing for whichever roster member is
in hand.

### wayfinder

    {wayfinder} Skill
      ├─args────► idea      charting a new map, via $ARGUMENTS
      ├─args────► map       working a map — URL or issue number
      ├─args────► ticket    optional — else wayfinder picks from
      │                           the frontier
      ├─reads───► [tracker-operations] Standard    the Wayfinding
      │                                             operations section
      ├─reads───► the map issue and its frontier   the open, unblocked,
      │                                             unclaimed children;
      │                                             ticket bodies on zoom
      ├ ╌ does ╌ ╌ ► setup-matt-pocock-skills      no tracker provided —
      │                                             dead reference; stays,
      │                                             the unit is verbatim
      ├ ╌ does ╌ ╌ ► {grilling} Skill              naming the destination,
      │                                             mapping the frontier,
      │                                             whenever in doubt
      ├ ╌ does ╌ ╌ ► {domain-modeling} Skill       alongside grilling,
      │                                             throughout
      ├ ╌ does ╌ ╌ ► [research] Skill              one per research ticket —
      │                                             fresh context, in parallel
      ├ ╌ does ╌ ╌ ► {prototype} Skill             a prototype ticket calls
      │                                             for code
      ├ ╌ does ╌ ╌ ► skills the map's Notes name   resolved at runtime from
      │                                             the map body
      ├─writes──► GitHub(issue, label, sub-issue, dependency,
      │            assignee, comment, close)        the map and its tickets —
      │                                              created, claimed,
      │                                              resolved, closed, the
      │                                              body sections kept current
      ├ ╌ writes ╌ ╌ ► git(branch)                 research findings on
      │                                             research/<name>
      ├ ╌ writes ╌ ╌ ► local file(markdown tracker)    no tracker provided
      └ ╌ reports ╌ ╌ ► no_map_needed: str         the grill surfaces no fog

One sentence carries the target: wayfinder is a GitHub-state machine —
the map, tickets, claims, fog, and decision log are all issue state
under one writes edge, its callees are the interview pair plus
research and prototype, and its "plan, don't do" default with the
map-Notes escape is a ledgered behavior-mode. The map body's own
contract — fog lifecycle, HITL/AFK axis, claim-by-assignment — is
ledgered written-artifact semantics.
