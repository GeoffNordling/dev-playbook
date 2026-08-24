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

Candidate generation may run outside this context window — an agent reads
the target and returns candidates for filtering here — or inline; which
fits is not yet known.

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
- **Types respected.** The loop keeps the stochastic/deterministic
  distinction and the document-type distinctions explicit.
- **General and hierarchical across repos.** The abstractions and the loop run on any
  workspace repo, anchored on that repo's registries — document types
  (upstream ∪ local) for concept docs, harness files for executors.
  Nothing here may depend on this repo's internals. Primitives will also
  cascade hierarchically across designated repositories the same way the Standards object does today.

## Heuristic: pivot to code

Documentation is a fuzzy, stochastic version of code — treat it as a
special case of code, and unify the two theories wherever the parallel is
real, never by force. When the documentation form of a problem is stuck,
translate it to the code form, solve it there, and port the analogy back.
Ports so far: change cost (below), the definition-site rule, and the
import-linter parallel (both under the reference chain).

**Change cost.** An adopted abstraction changes the
way a codebase does — renaming or replacing one is a refactor, a
significant investment, never a whim two weeks later. The CLOA change
discipline from the branch plan guards everyday operations against that
jitter; the bootstrap run, before anything is adopted, stays freeform.

## Abstractions so far

| Noun            | Verbs                         | Is                                                |
| --------------- | ------------------------------ | ------------------------------------------------- |
| Standard        | define, audit, enforce, adopt | A rule the workspace runs under                   |
| Agent           | do                            | Documentation that runs in a fresh context, on its own permission set |
| Skill           | do                            | Documentation that runs in the calling context, on its permissions |
| Reference chain | edges: does, reads, overrides, writes | The declared tree of everything a unit does, reads, overrides, and writes |

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
  are typed as state — a GitHub issue, a local markdown file, a git
  branch — and may re-enter the graph as read sources: design writes the
  brief that build later reads.

Any edge may carry a **guard** — the condition under which it fires — as
a prose annotation on the edge ("only agent-facing targets", "only when
reading can't settle it"). A call inside an `if` is still a call edge;
the condition never changes the edge's type.

Its rules:

- **Nodes are typed** by kind (Standard, Agent, Skill) and by ownership —
  self-owned or vendored. Ownership is a color, not an edge. A node may
  also carry its permission expression — an agent's set, a skill's
  clamp — as node data.
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

## Targets

The population a repo's loop must account for is enumerated by its two
registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/claude-code/files.md) for harness
files — so "every unit accounted for" is a checkable claim, and each
registered type gets a disposition into the ontology. The boundary
between the two is encoded as `classify()` in `src/dev_playbook/md.py`.
This repo's census, per `classify()`: 107 concept docs, 48 harness `.md`
files, 16 indexes, 47 excluded (the vendored `dotfiles/.agents` tree and
scratch).

The registry pass ruled on every registered type. Two matter to the
ontology: **Standard** — with Standard-Card as its catalog surface, the
same object — and **Guide**, the software factory's documentation, unmet
by the loop so far. **Vocabulary** is important but separate: the
vocabulary API, not a primitive. Everything else is declared unimportant
and ignored — Decision-Records included, which take no actions and exist
as greppable history.

Chosen, in order: `document-deslop` (minimal, known cold — the
calibration run), `grill-with-docs` (mid-size — five skills and a
standard), `design` (the hub — eight skills and four docs, the chain least
likely to fit in the user's head).

The software factory is the graduation exercise, not a target yet: the
abandoned attempt to understand it whole failed because the factory is
only a collection of abstractions, and none of them had been constructed
yet.

### Run 1: document-deslop — zero residual

The chain, declared:

    [document-deslop] Skill
      └─does──► [deslopper] Agent (Read, Write)
                  ├─does──►  [slop-tics] Standard — .enforce
                  ├─reads──► [conventions] Standard
                  └─reads──► [writing-for-agents] Skill  (only agent-facing targets)

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
      ├─does──► {prototype} Skill                    only when reading can't settle it
      ├─does──► [user-intent-mini-interview] Skill   every single-leaf write
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
