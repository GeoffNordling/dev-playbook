---
type: General-Sheet
title: CLOA Abstractions
description: The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
---

# CLOA Abstractions

The **CLOA primitives ontology**: the abstractions the user and the AI
share at the CLOA — each a noun with a small fixed verb set — and, as a
detail of method, the loop that generates them. An offshoot of [NO-MORE-SLOP.md](/NO-MORE-SLOP.md),
deleted when its results merge back into that plan or the branch of ideas
terminates. The same speculative voice applies: a guess is written as a
guess, and a sentence is settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
whole software factory — without reading all of it.

## Premise

Documentation does things, because agents make things happen and an agent
is a collection of documentation plus a permission set. So a documentation
unit has an operational meaning — what reads it, when it fires, what
changes as a result — and an abstraction names that meaning at the CLOA.

## Documentation as code

The vision: think of documentation the way code is thought of — modules,
typing, signatures, rules. Everything here is just wrapping deterministic
structure around written documentation. Keep the structure simple,
enforceable, and deterministic, and account for what it cannot carry in
the residuals ruled important.

The working heuristic: documentation is a fuzzy, stochastic version of
code — treat it as a special case of code, and unify the two theories
wherever the parallel is real, never by force. When the documentation
form of a problem is stuck, translate it to the code form, solve it
there, and port the analogy back.
Ports so far: change cost (below), the definition-site rule, and the
import-linter parallel (both under the reference chain).

**Change cost.** An adopted abstraction changes the
way a codebase does — renaming or replacing one is a refactor, a
significant investment, never a whim two weeks later. The CLOA change
discipline from the branch plan guards everyday operations against that
jitter; the bootstrap run, before anything is adopted, stays freeform.

## Abstraction shape

One noun carrying a small fixed verb set — an interface. Nouns describe;
verbs predict. Tentatively accepted rule: the operations are always verbs,
which is deterministic structure at the level of ideas.

The exemplar is the **Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from four verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts. The
loop owes an answer at both levels.

## The loop

In code, the programming language comes first and the functionality second.
Thus, functionality may be expressed as code, constrained by the primitives
that were defined by the language in advance.

When we seek to express existing documentation as code, we have a problem: documentation
has free-form, infinite possibilities. No constrained programming language
exists apriori: indeed the language we have is the English Language!

We solve this with a backwards operation combining AI proposals with user intuition.
This generates programmable primitives from the documentation in a way that aligns
with both user intuition and AI evaluation. The user vibes, the AI validates.

An expectation-maximization shape over a chosen target artifact:

- **E-step.** An agent re-expresses the target entirely in the current
  abstractions. Whatever forces a drop to file-level detail is the
  residual.
- **M-step.** Propose abstraction changes — add, merge, rename, delete —
  that shrink the residual. The user filters candidates on intuition; the
  model's job is to challenge the filter.
- **Convergence** is the pandas test: the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal. Good abstractions are a codebook the corpus gets short in.

Residuals are tracked, not zeroed. The loop's job is awareness of what
the abstractions fail to carry; the primitive set is refactored only when
the reduction is worth the change cost.

The first move on a repo is the **registry pass**: enumerate every
document type from its two registries — OKF concept types and
harness-owned kinds — and rule each one important or not to the CLOA
primitives ontology. Unimportant types are declared so and ignored;
targets come from the important ones.

The bootstrap run is freeform — a discussion, with several branching
possibilities live in the same context window. Rigidity applies later, to
adopted abstractions: see the change-cost note under the code heuristic.

Candidate generation settled during the close-out: parallel reader
agents extract each unit's chain against a shared brief, outside this
context window; rulings happen inline, between batches, and the brief
is re-synced to the ontology before each launch.

Before looping on a target, interview the user on what they want to
understand about it. The CLOA is relative to the repository's purpose and
the user's wants, so without the interview the loop optimizes explanation
in the abstract.

## Constraints

- **Deterministic backpressure where it reaches.** A claim stated in an
  abstraction's terms is worth more when a lint can check it — "skill X
  references skills Y and Z" is grepable; "skill X is elegant" is not — so
  prefer lintable claims wherever a lint can reach, and accept that much
  of what the abstractions say will never be lintable.
- **User eyes.** The artifacts the loop produces must be easy for the
  user to read — everything before this point optimized for agent
  readers. An application of constrain to optimize understanding.
- **Verbatim dependencies cannot participate.** The goal is to
  generate every reference chain with deterministic code, after
  structuring each unit to make that generation possible. A verbatim
  third-party file carries none of that structure, so it cannot
  participate. Two dispositions, undecided until the lint plan: own
  and restructure every vendored file (zero verbatim dependencies), or
  keep some verbatim and accept that their chains stay model-generated,
  outside the deterministic system. Related open note: overrides is
  grounded today in "a unit that cannot be edited"; if vendored files
  become owned, it likely re-grounds as superseding an instruction in
  effect at runtime, self-owned units included.
- **Types respected.** The loop keeps the stochastic/deterministic
  distinction and the document-type distinctions explicit.
- **General and hierarchical across repos.** The abstractions and the loop run on any
  workspace repo, anchored on that repo's registries — document types
  (upstream ∪ local) for concept docs, harness files for executors.
  Nothing here may depend on this repo's internals. Primitives will also
  cascade hierarchically across designated repositories the same way the Standards object does today.
- **The procedure generalizes; the nouns cascade.** The procedure —
  registry pass, EM loop, change discipline — runs on any repo. The
  nouns generated here are not repo-local output: dev-playbook is the
  root of the hierarchy, and every repo runs skills, so its primitives —
  Reference chain included — cascade to consumer repos the way
  Standards do today. A consumer repo's loop adds special-case nouns on
  top of the inherited set; it never re-derives the root.

## Abstractions so far

| Noun            | Verbs                         | Is                                                |
| --------------- | ------------------------------ | ------------------------------------------------- |
| Standard        | define, audit, enforce, adopt | A rule the workspace runs under                   |
| Agent           | do                            | Documentation that runs in a fresh context, on its own permission set |
| Skill           | do                            | Documentation that runs in the calling context, on its permissions |
| Workflow        | do                            | Deterministic orchestration code in its own runtime — not an LLM |
| Script          | do                            | Deterministic code run via the shell — not a direct LLM call, not the Workflow runtime |
| Reference chain | edges: does, reads, overrides, writes, args, returns | The declared tree of a unit's behavior and its call signature — args in, returns out |

- **Standard** is established and live. Its open problem: the top level is
  elegant and simple; the bottom level is a messy collection of
  non-user-readable documents and scripts.
- **Agent and Skill** get one verb, **do**, and no more, ever. Specificity
  comes from the behavior being done, which documentation defines — a
  Standard's verb where one exists (the deslopper does slop-tics.enforce),
  the whole unit where the doc is the definition (grill-with-docs does
  grilling). The two differ in context binding: an agent runs in a fresh
  context window, a skill in the calling one — an in-process call versus a
  subprocess. A fresh context starts from configuration (the preset
  preload, whose contents are not modeled, the way a call graph does not
  model env vars); a skill starts from here. Permissions ride on the node:
  an agent carries its own set, a skill the calling context's, minus any
  clamp its frontmatter declares. Declared permissions are assumed to take
  effect; harness enforcement fidelity is out of scope. The steps inside a
  skill are that skill's program, file-level detail below the CLOA, never
  an interface.
- **Workflow and Script** are deliberately two nouns for the same
  function — deterministic code, done with the one verb **do** — split
  by runtime: a Workflow runs in Claude Code's dynamic-workflow runtime
  (ralph-loop), a Script runs via the shell (usage-report's bundled
  `report.sh`, the repro loop diagnosing-bugs copies from its template).
  Different words in the same spot; the node name says which runtime
  executes. Running a script is a does-edge to a Script node — marked
  in-bundle when it ships inside the skill's directory — and the
  script's own reads and writes hang under that node. The zoom rule
  collapses in-bundle documents, never an executed script.

### Reference chain

A **unit** is one documentation file, or an abstract object that functions
like one, the way a skill functions like its SKILL.md. Every chain node is
a unit; the nouns in the table are its types.

Notation: `[x]` self-owned, `{x}` vendored. The edges:

- **does** — run a behavior some documentation defines: a Standard's verb
  where one exists, the whole unit where the doc is the definition.
- **reads** — consulted, not run.
- **overrides … with …** — substitute a clause in a unit that cannot be
  edited.
- **writes** — produce or mutate state outside the chain. Write targets
  are typed `bucket(refinement)`: a fixed coarse bucket — git, GitHub,
  local file, local cache, scratch — plus an optional free refinement,
  as in `git(branch)` or `local cache(SQLite)`. The bucket list stays
  fixed and lintable; the refinement is a memory aid, never a new type.
  Targets may re-enter the graph as read sources: design writes the
  brief that build later reads. Scratch writes carry no filenames.
  The refinement stays machine-readable: a comma-separated sequence of
  operations — `git(commit, push)` — never prose and never `+`. A
  target in another repo carries that repo's name as the refinement's
  head — `git(mission-control: commit, push)` — and the same repo
  prefix marks a cross-repo read target (`mission-control/friction
  log`); crossing a repo boundary is always visible.
- **args** — the value the caller hands in at invocation, carried by
  the harness's `$ARGUMENTS` substitution. Declared in Python
  type-hint form, `arg_name: arg_type` — log-friction declares
  `friction: str`. Never lands in state, dies with the call.
- **returns** — hand a value back to the caller, user and agent alike:
  ralph-setup returns a launch command to the user, bump-pins returns
  its status enum to update-standards-pin. Unlike a write, a return never
  lands in state — it dies with the call. Returns mirror args: named
  and typed as `return_name: return_type` — commit returns
  `outcome: str` — and an enumerable status is preferred, its values
  listed as a small enum. A returning unit will declare its return in
  its own file, so the primitive view renders the declaration instead
  of a model regenerating it; the declaration format is designed
  later, with the lint plan.

Any edge may carry a **guard** — the condition under which it fires.
A guarded edge is drawn dashed with the dashes spaced out so the break
is visible on screen (`├ ╌ does ╌ ╌ ►`), and its trailing text is the
condition; a solid edge (`├─does──►`) is unconditional, and its
trailing text is mere annotation. A call inside an `if` is still a call edge; the
condition never changes the edge's type.

Its rules:

- **Nodes are typed** by kind (Standard, Agent, Skill, Workflow, Script) and by
  ownership — self-owned or vendored. Ownership is a color, not an edge.
  A node may also carry its permission expression and model pin as node
  data, quoted verbatim in the harness's own syntax —
  `allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
  paraphrased into prose.
- **Edges live at the definition site.** An edge belongs to the document
  whose text contains the instruction — greppable, so the assignment is
  lintable. A root's effects are the union of edges reachable along its
  does-path — the same rule as code, where a write belongs to the frame
  whose source contains the statement.
- **Tree, then graph.** Each unit declares its own tree; the union across
  roots is the repo graph, where in-degree, hubs, and orphans appear. The
  code parallel is import-linter: a declared dependency contract that
  fails when reality disagrees. A lint-design candidate to evaluate when
  the checker is built: the ontology-guardrails idea
  (`~/workspace/mission-control/ideas/ontology-guardrails.md`) — declared
  rules enforced by a solver.

The chain absorbs skills as signatures, OKF traces, and the OKF graph —
one object seen from three angles.

Remembered, not primitives:

- **Zoom.** A unit collapses its internal files (containment is derivable
  from paths — `design/references/` sits under `design/`); zoomed in, they
  appear as nodes inside the unit boundary with ordinary edges.
- **Doc type.** A read target's frontmatter type (Guide, General-Sheet)
  is noted informally; a type earns a noun only when it demonstrates a
  verb interface, the way Standard did.

### Accepted residuals

The ledger of residuals ruled on and accepted as-is, one line each, so
no run raises the same question twice. A construct listed here is real
but deliberately outside the ontology until a ruling is reversed.

- **Reality probes** — direct shell contact with repo state ("run the
  gate", "confirm the git tree is clean"). A real operation; ruled not
  accounted.
- **Attestation checkpoints** — "report `READ: x`, proceed only after."
  A prompt device that raises the probability the read happens; ruled
  not accounted.
- **Agent-held ephemeral state** — counts and set-aside lists a unit
  tracks only in its own working memory, persisted nowhere
  (judgments-sweep's fix-attempt cap and skip list); ruled not
  accounted.
- **User interview loops** — a mid-run, multi-round dialogue with the
  user (skill-creator's "iterate until the user is satisfied";
  grilling's whole body). Conversing is what running in the calling
  context means; ruled not accounted.
- **Behavior-mode setting** — a unit whose body installs standing
  behavior in the session's ephemeral context and fires no edge at
  invocation (orchestrate: "everything below you is a subagent").
  Ruled residual; admitting it later requires a lintable,
  deterministic form.
- **Vendored platform manifests** — the `agents/openai.yaml` display
  card every vendored bundle ships for another agent platform; bundle
  furniture, referenced by nothing, never an edge.
- **Presentation gestures** — opening an already-written artifact for
  the user (improve-codebase-architecture's `xdg-open` on its report);
  part of returning the value, never an edge; ruled not accounted.
- **Phase gates** — a step-scoped prohibition inside a unit's own
  program, lifted by a later step (improve-codebase-architecture's "Do
  NOT propose interfaces yet"); internal sequencing below the CLOA,
  already covered by the steps-are-the-program rule; ruled not
  accounted.
- **Written-artifact semantics** — the schema and state rules of a
  document a unit writes and later re-reads: wayfinder's map-body
  sections, fog lifecycle, HITL/AFK axis, claim-by-assignment, ticket
  sizing. The artifact's contract lives in the artifact; the chain
  records only the writes and reads that touch it.

## Targets

The population a repo's loop must account for is enumerated by its two
registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/claude-code/files.md) for harness
files — so "every unit accounted for" is a checkable claim, and each
registered type gets a disposition into the ontology. The boundary
between the two is encoded as `classify()` in `src/dev_playbook/md.py`.
This repo's census, taken at the registry pass, per `classify()`:
107 concept docs, 48 harness `.md` files, 16 indexes, 47 excluded (the
vendored `dotfiles/.agents` tree and scratch). Orient and pymc-modeling
were deleted after the count.

The registry pass ruled on every registered type:

| Type | Pop. | Important? | Ruling |
|---|---|---|---|
| Standard | 37 | **Yes** | The Standard noun — define, audit, enforce, adopt |
| Standard-Card | 15 | **Yes** | Same object as Standard — its catalog surface |
| Guide | 9 | **Yes** | All `software-factory/` — deferred to the factory phase |
| Vocabulary | 1 | Separate | The vocabulary API, not a primitive |
| Decision-Record | 25 | No | Takes no actions; greppable history |
| README | 7 | No | Navigation |
| General-Sheet | 7 | No | Parking lot for unsettled types |
| Recipe-Description | 3 | No | Describes backing code |
| Instrument-Spec | 2 | No — actively excluded | Instruments face possible deletion |
| Candidate-List | 1 | No | Tracker state |
| Reference | 1 | No | Vendored mirror |
| Survey / Log / Spec-Item | 0 | No | No population here |

The bootstrap targets, run in order and all recorded in the ledger:
`document-deslop` (minimal, known cold — the calibration run),
`grill-with-docs` (mid-size — five skills and a standard), `design`
(the hub — the chain least likely to fit in the user's head).

The software factory is next — the graduation exercise. It brings the
Guide type (9 docs, all `software-factory/`) and the 13 parked units,
and may leave large residuals: a Guide describes how a fleet of units
operates together — protocol, not one unit's behavior — which no
current noun carries. Per the remembered rule, Guide earns a noun only
if it demonstrates a verb interface, the way Standard did; otherwise
its content lands in chains, written-artifact semantics, and the
ledger.

### The chains ledger

Every finalized chain is recorded in [CLOA Chains](/CLOA-CHAINS.md) as it
is ruled — the three bootstrap runs and each close-out unit — so the
close-out ends in a written ledger, not in compacted memory. This file
keeps the ontology and the rulings; that file keeps the chains.

The empirical close-out ended by ruling with 23 chains recorded: batches had
stopped producing ontology changes, and the thirteen units still
unread were ruled expressible with the existing primitives. The
recorded chains are proof of concept, not final artifacts — the final
traces will be generated deterministically by scripts operating on
structure embedded in the unit files, designed with the lint plan.
