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
document type from its two registries — the
[document-type registry](/standards/knowledge-organization/document-types.md)
for concept docs and the
[Claude Code file registry](/standards/harness/files.md) for harness
files — and rule each one important or not to the CLOA primitives
ontology. Unimportant types are declared so and ignored; targets come
from the important ones. The registries make "every runbook accounted
for" a checkable claim. Throughout, the loop keeps the
stochastic/deterministic distinction and the document-type distinctions
explicit.

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

## Scope

An abstraction's reach runs along two axes: documentation families and
repos.

Every documentation family is its own beast. The Reference chain is the
runbook-family solution: skills and agent definitions are commands, so a
command-shaped abstraction fits. Each family earns its own abstractions
and its own deterministic parsing.

Across repos, the procedure generalizes and the nouns cascade. The
procedure — registry pass, EM loop, change discipline — runs on any
workspace repo, anchored on that repo's registries: document types
(upstream ∪ local) for concept docs, harness files for executors. The
nouns generated here are not repo-local output: dev-playbook is the
root of the hierarchy, and every repo has runbooks, so its primitives —
Reference chain included — cascade to consumer repos the way Standards
do today. A consumer repo can add its own special cases but
automatically inherits systems from its higher levels.

## Registry dispositions

The general registry for dev-playbook: every registered type from both
registries — concept docs and harness files — and its ruling:

| Type | Important? | Ruling |
|---|---|---|
| Skill | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md) construction |
| Agent definition | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md) construction |
| Standard | **Yes** | The Standard noun — define, audit, enforce, adopt |
| Standard-Card | **Yes** | Same object as Standard — its catalog surface |
| Guide | **Yes** | No construction built yet |
| Vocabulary | Separate | The vocabulary API, not a primitive |
| Decision-Record | No | Takes no actions; greppable history |
| README | No | Navigation |
| General-Sheet | No | Parking lot for unsettled types |
| Recipe-Description | No | Describes backing code |
| Instrument-Spec | No — actively excluded | Instruments face possible deletion |
| Candidate-List | No | Tracker state |
| Reference | No | Vendored mirror |
| Survey / Log / Spec-Item | No | No population here |
| `CLAUDE.md` | No | Context, injected prose — read, never invoked |
| Rule (`rules/*.md`) | No | Context, injected prose — read, never invoked |
| Settings | No | Configuration the harness reads |
| Hook | No | Deterministic code the harness runs |
| Workflow (`workflows/*.js`) | No | Deterministic code the harness runs |
