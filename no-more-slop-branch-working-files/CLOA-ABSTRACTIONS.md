---
type: General-Sheet
title: CLOA Abstractions
description: The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
---

# CLOA Abstractions

The **CLOA primitives ontology**: the abstractions the user and the AI
share at the CLOA — each a noun with a small fixed verb set — and, as a
detail of method, the loop that generates them. An offshoot of [NO-MORE-SLOP.md](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).
The same speculative voice applies: a guess is written as a
guess, and a sentence is settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
entire repository — without having to read all of it.

## Documentation is code

Documentation is code: it does things because agents do things, and an agent
is just documentation, a harnesss, and permissions.

Unfortunately, documentation is also stochastic and extremely high-dimensional.
We add parsimonious structure that constructs
high-level abstractions capturing the important parts the user cares about.
Keep the structure simple, lintable, deterministic, and high leverage.

Treat documentation as a special case
of code; pre-existing methods for code may work for documentation also,
with minimal modifications. When facing a difficult problem in documentation,
translate to the code form, solve it there, and port the analogy back. For
example, each document should probably have a typed signature.

Documentation abstractions change the
way codebases do — refactors are possible but costly.

## A noun with one or more verbs

One noun carrying a small fixed verb set. Nouns describe;
verbs act. Naming nouns and giving them verbs is deterministic
structure at the level of ideas.

Implemented exemplars so far:

**Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from those verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts.

**Runbook Reference chain**: the noun is the
chain, the verbs are its six edge labels (does, reads, overrides, writes,
args, reports), and its node types — Agent, Skill, Script — ride along as
one-verb nouns. It allows the user to understand a runbook's behavior without opening
the body.

## An EM loop for primitive construction

In code, the programming language comes first and the functionality second.
Thus, functionality may be expressed as code, constrained by the primitives
that were defined by the language in advance.

Expressing existing documentation as code hits a problem: documentation
has free-form, infinite possibilities. No constrained programming language
exists apriori: the language is English itself.

We solve with a backwards operation combining AI proposals with user
intuition: generate programmable primitives from the documentation.

An expectation-maximization shape over a chosen target artifact:

- **E-step.** An agent re-expresses the target entirely in the current
  abstractions. Whatever forces a drop to file-level detail is the
  residual.
- **M-step.** Propose abstraction changes — add, merge, rename, delete —
  that shrink the residual. The user filters candidates on intuition; the
  model's job is to challenge the filter. The burden of proof sits with
  the model: the user's accept or reject needs no justification, and the
  model validates every accepted candidate against the corpus.
- **Convergence** is the pandas standard: the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal — good abstractions are a codebook the corpus gets short in,
  so functionality per character runs high.

Track residuals. The loop's job is awareness of what
the abstractions fail to carry; the primitive set is refactored only if
the reduction is worth the change cost.

The first move on a repo is the **registry pass**: enumerate every
document type from its two registries — OKF concept types and
harness-owned kinds — and rule each one important or not to the CLOA
primitives ontology. Unimportant types are declared so and ignored;
targets come from the important ones.

Before looping on a target, interview the user on what they want to
understand about it. The CLOA is relative to the repository's purpose
and the user's preferences.

This algorithm can also apply to greenfield repositories. But instead of
looking at existing documentation and pulling out useful constructions,
the AI and the user can talk about theoretical functionality for the
future repository in the user's imagination.

### Layer invariance

The loop is layer-invariant. It ran once at the ontology level — target:
the documentation corpus; output: the primitives table below — and again
one level down in
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md),
where the target is skill prose and the output is a grammar. Two adjacent
runs connect through a map between the lower level's generated primitives
and the higher level's existing ones, written to a stateful location
(Edge Encoding's primitive map). One-to-one is the ideal — each higher
primitive with exactly one lower expression — but may not always be
possible; the map is what matters, because it lets the next run start
from structure instead of from conversation. The alternative is the
linear mode — correcting one instance per turn, no primitive ever
extracted — which is how a session lands back in the slop trench.

The shape, abstractly:

```
layer N:    target artifact ──loop──► primitives
                                          ▲
                                          │ the map, written statefully:
                                          │ one lower expression per higher primitive
layer N−1:  target artifact ──loop──► primitives
```

And the two runs this branch executed:

```
ontology:   documentation corpus ──loop──► nouns + verbs
                                           (Reference chain: reads, writes, reports, …)
                                               ▲
                                               │ the primitive map in REFERENCE-CHAIN.md:
                                               │ reads ↔ {Read …}, writes ↔ {Write …}, …
encoding:   runbook prose ──loop──► grammar
                                    (braced spans: {Read …}, {If …, {…}}, …)
```

## Constraints

- **Deterministic backpressure where it reaches.** A claim stated in an
  abstraction's terms is worth more when a lint can check it — "skill X
  references skills Y and Z" is grepable; "skill X is elegant" is not — so
  prefer lintable claims wherever a lint can reach, and accept that much
  of what the abstractions say will never be lintable.
- **User eyes.** The artifacts the loop produces must be easy for the
  user to read — documentation up to this point has generally optimized
  for agent readers. This applies the branch principle
  [Constrain to optimize understanding](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).
- **Verbatim dependencies cannot participate.** The goal is to
  generate every reference chain with deterministic code, after
  structuring each runbook to make that generation possible. A verbatim
  third-party file carries none of that structure, so it cannot
  participate. Settled at Decision Record 0025: verbatim adoption is
  retired and every runbook is owned — zero verbatim dependencies.
  Consequence: overrides, grounded until then in "a runbook that cannot
  be edited", re-grounds as superseding an instruction in effect at
  runtime, self-owned runbooks included.
- **Types respected.** The loop keeps the stochastic/deterministic
  distinction and the document-type distinctions explicit.
- **Every documentation family is its own beast.** The Reference chain
  is the skills-family solution — skills are commands, so a
  command-shaped abstraction fits — not the universal one. Each family
  earns its own abstractions and its own deterministic parsing: a
  freedom and a burden both. The registry pass's per-type dispositions
  and the rule that a type earns a noun only by demonstrating a verb
  interface are this constraint applied.
- **General and hierarchical across repos.** The abstractions and the loop run on any
  workspace repo, anchored on that repo's registries — document types
  (upstream ∪ local) for concept docs, harness files for executors.
  Nothing here may depend on this repo's internals.
- **The procedure generalizes; the nouns cascade.** The procedure —
  registry pass, EM loop, change discipline — runs on any repo. The
  nouns generated here are not repo-local output: dev-playbook is the
  root of the hierarchy, and every repo runs skills, so its primitives —
  Reference chain included — cascade to consumer repos the way
  Standards do today. A consumer repo's loop adds special-case nouns on
  top of the inherited set; it never re-derives the root.

## Targets

The population a repo's loop must account for is enumerated by its two
registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/harness/files.md) for harness
files — so "every runbook accounted for" is a checkable claim, and each
registered type gets a disposition into the ontology. The boundary
between the two is encoded as `classify()` in `src/dev_playbook/md.py`.
This repo's census, taken at the registry pass, per `classify()`:
107 concept docs, 48 harness `.md` files, 16 indexes, 47 excluded (the
vendored `dotfiles/.agents` tree and scratch).

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

The software factory is the graduation exercise, parked for now. It
brings the Guide type (9 docs, all `software-factory/`) and the 13 parked
runbooks,
and may leave large residuals: a Guide describes how a fleet of runbooks
operates together — a protocol above single-runbook behavior — which no
current noun carries. Per the remembered rule, Guide earns a noun only
if it demonstrates a verb interface, the way Standard did; otherwise
its content lands in chains, written-artifact semantics, and the
ledger.

### The chains ledger

Every chain is generated into `parser/chains.txt` from in-file structure;
that structure is
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md), this
file's lower level.
