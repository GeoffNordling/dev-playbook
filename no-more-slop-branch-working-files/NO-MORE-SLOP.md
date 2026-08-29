---
type: General-Sheet
title: No More Slop
description: The branch plan — goal, principles, the two tracks, and the current step
---

# No More Slop

The plan and state of the `no-more-slop` branch, deleted when the branch
merges. Material drains out of this file as it settles into the appropriate
long-term location.

This file is speculative, and the doc conventions' declarative voice does
not apply to it: a guess is written as a guess, an open question sits
inline next to its topic, and a sentence is settled only when it says so.

## Goal

The user can understand this repository without reading all of it. Today
they cannot: the repo sits in the slop trench — nominal ownership of a
system whose details have outpaced inspection. This branch works the
documentation track; the code track waits.

Open question: no standard states this goal. A System Legibility card used
to, pointing at the datasheet and file-graph instruments, but both went
stale and the card was deleted. Whether the goal earns a card of its own is
a question for the end of this branch, once the work has shown what would
actually be governed.

"Slop" splits into:

- **Low quality** — divergence from the user's latent intent for action and
  preference for style. For the AI this operationalizes as divergence from
  the stated standards, which are themselves ill-defined in places.
- **Not understood** — the user cannot or will not read critical information,
  whatever its quality, because it is encoded only as illegible walls of text
  and code, greppable by AI, but not the user.

Today's stock of slop is mostly **intent alignment debt** — divergence
from the user's intent accrued over time: the mirror of tech debt. Going
forward, we use appropriate structure and abstractions in order to maintain
user understanding and prevent new debt from accruing.

## Levels

Understanding happens at multiple levels, for code and documentation alike:

- **One file, opened.** The user zooms in on a single file and looks at it.
  What serves this level changes the file itself — wording, shape, length —
  never its meaning.
- **Above the file.** The user cannot read all files at once, so understanding at
  the higher levels has to come some other way. Code has established tools
  at this level; we will construct similar abstractions for documentation.

Across the levels runs an abstraction/detail axis with a latent optimal
point neither party knows a priori. Too low — too much detail — and the
user wastes stops paying attention, rubber stamps, and intent alignment debt
accumulates; too high and the user is
fooled into thinking they understand temporarily; both ends produce slop. Pre-AI
interfaces were forcing functions: pandas and git impose their
abstractions, and a wrong mental model did not survive contact with them.
Natural language imposes such constraints. We must deliberately engineer interfaces
at the appropriate level of abstraction. 

## Principles

These apply to both tracks.

- **The CLOA** — the level of abstraction
  where the AI and the user communicate in the exact same terminology.
  Its shared definitions are the primitives in
  [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md) — each a noun with a small
  fixed verb set — from which the user predicts behavior without reading
  bodies. The bets per track: the primitives carry the CLOA for
  documentation, and the acceptance tier (code track) carries it for
  code.
- **The vocabulary API** — `CONTEXT.md` holds the canonical terms for
  communication: the user understands it 100%, the AI uses its terms, and
  a missing term is added on the spot and approved by the user. Zero vibe
  coding in that file. It is designed the way a library designs its
  public surface, with the internals below it AI-owned. Escalation
  discipline is its behavioral half: the AI raises questions in
  vocabulary terms, proposing a new term when one is missing. A default,
  toggleable — some modes of talk need to leave the vocabulary.
- **Deterministic backpressure preferred over stochastic functions.**
  Stochastic functions — prompts, models, agents — are powerful but
  expensive. Deterministic backpressure — detectors, linters, gates, and
  plain contact with reality — is inviolable and efficient. Prefer it
  wherever it can reach, but it can't do everything. Prefer claims a lint
  can check — "skill X references skills Y and Z" is grepable; "skill X
  is elegant" is not. Keep agentic
  backpressure tools simple and loop friendly: simple status codes can be
  better than detailed reports.
- **Move slowly in decision space.** Past failures were planning too much
  and leaping too far. Small iterative steps, with backpressure from
  reality at each one; what stays small is how much is committed before
  reality answers back.
- **Constrain to optimize understanding.** Apply constraints that funnel
  the same declarations through reduced forms designed to help the user
  understand. This amortizes reading (learn the shape once,
  read every instance fast), makes location and absence meaningful, and
  it enables linting. The constrained artifacts are for user eyes —
  documentation up to now has generally optimized for agent readers.

## The pandas standard

The target state, named for where the user lived it: years of pandas
fluency — which objects exist, which methods fit which task, how they
compose — without ever reading inside a pandas method. The internals
belonged to the pandas maintainers; here they belong to the AI. The
fluency came from being the caller: the user learned pandas, git, and the
software factory by operating them daily.

The [Standard](/standards/standard/format.md) card system is the in-repo
exemplar, worked as the abstraction shape in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs).

## Documentation track — active

**Now**

The ontology is settled in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md);
the encoding design and its parser sit in Encoding, beneath Reference
Chain. Two items remain:

- **Recursion to the bedrock of determinism.** Develop the note: the
  EM loop applies all the way down until the target stops being
  stochastic; maps recurse one rung further — grammar ↔ parser, the
  certified transform, pinned by `--check`.
- **Primitive and ontology terminology sweep.** "Primitive" and
  "ontology" are used loosely across these files; tighten every use.

**Completed**

- **CLOA primitives.** Three bootstrap runs plus an empirical
  close-out in
  [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
  constructed a converged primitive set — that file's table is the
  roster — describing what documentation does at the CLOA: the user
  understands the whole surface and keeps enough control to guide the
  system, the implementation below the CLOA is delegated to the agent,
  and deep dives stay auditable by opening actual files. That
  files are still too hard to read is a separate open work stream (the
  Levels section's first level).
- **Deslop rewrite.** Every prose document rewritten in place against
  [Slop Tics](/standards/prose/slop-tics.md). Productionized as the
  `/document-deslop` skill, which the user invokes manually.
- **Documents hold behavior; skills and agents hold procedure.**
  Standardized in
  [file-roles.md](/standards/knowledge-organization/file-roles.md).
- **Edge encoding and its parser.** The Reference chain's in-file
  declaration format — braced spans over a fixed keyword lexicon,
  sliced at fixed cut points but never interpreted — designed on a
  five-runbook covering set in Encoding
  and proven by `parser/chaingen.py`, which deterministically
  regenerates every covered runbook's chain into `parser/chains.txt` and
  fails on drift via `--check`.
- **First-party port.** Every runbook we author ourselves — all twelve
  agents and the unmarked skills in the Port roster,
  38 runbooks — ported to the edge encoding by a fixed dispatch
  prompt, since retired, each with its leftovers recorded in the
  Residual Ledger.
- **The runbook standard, and the gate green.**
  [Runbook Conventions](/standards/harness/runbook-conventions.md)
  replaced what the old docs taught: `skill-management.md` deleted, the
  `## Name: $ARGUMENTS` heading and `argument-hint` retired, `arguments`
  declared. `scripts/harness-files-lint` audits agents as well as skills
  against per-kind closed vocabularies and enforces the new keys
  (`harness.arguments-format`, `harness.tools-format`);
  `harness.banned-field` is gone. `skill-creator` became
  `runbook-creator`, a procedure that states no rules and defers to the
  standard. Every commit from 8d5a80f on carries no `SKIP` — the gate is
  green unaided, which was this step's bar. A tangent off it produced
  [the writing-improvement process](/docs/writing-improvement-process.md).
- **Verbatim adoption retired.**
  [0025](/docs/decisions/0025-retire-verbatim-skill-adoption.md) changed
  the policy: adoption is by copy into the owned tree. Ten (3P) skills
  converted to owned copies; `wizard`, `marimo-batch`, and
  `marimo-notebook` were deleted instead. The install machinery (CLI,
  lock file, `.agents` tree, mirror symlinks, gate exemptions) retired,
  and every document that evaluates or adopts other people's skills —
  `pocock-sweep`, the verdicts ledger, the standards that named the
  vendored exemption — now states the new stance.
- **Sweep machinery deleted.** The `pocock-sweep` skill is deleted and the
  ledger reduced to skill / verdict / date / reason per source — no release
  pin, no tag or commit hashes, no per-ruling Decision Record. Re-evaluation
  is manual: the user updates the rows by hand. Recorded in 0025.
- **Converted-skill port.** The former (3P) ten, owned since 0025, went
  through the same port as the first-party runbooks — the Port roster
  is fully ticked.
- **Rules moved out of skills.** Under the relaxed file-roles standard
  (rules live in documents, procedures live in runbooks), `codebase-design`
  became `standards/modules/design.md` and `writing-for-agents` became
  `standards/harness/writing-for-agents.md`; both skills are deleted and
  every caller repointed. `domain-modeling` slimmed to the active
  discipline: its `CONTEXT-MAP.md` layout (conflicting with
  context-content.md) and its `adr-format.md` (conflicting with
  decisions/records.md) were cut, the CONTEXT.md format folded into
  context-content.md, and `grill-with-docs` — reduced to a one-line
  wrapper once its override retired — was deleted, its callers running
  `/grilling` + `/domain-modeling` directly.
- **Working-file reorganization.** The branch's working files rebuilt
  as a tree with one job per file: Reference Chain declares the
  object, Encoding beneath it is the writer's spec, the Residual
  Ledger is the one system-wide record, and Port Prompt retired.

**Raw ideas, none designed**

- **Each new document is a giant pile of slop.** Each new major document Claude
  writes is a pile of slop that I have to wade through and iterate with Claude
  to brint to acceptable condition. Every time I do this is an opportunity to
  codify general rules, procedures, and algorithms for writing documents
  correctly. I need to use each linear slop trench session to spin the flywheel
  and climb out of the trench. Right now there is no flywheel and I haven't
  even started climbing out.
- **Markdown complexity detectors.** No specifics yet on how to measure a
  document's complexity — the goal is a file the user can read without
  checking out on opening.
- **Doc linters, re-aimed.** The existing linters are pedantic — they check
  that certain headings are present. Decide what is worth linting for and
  design toward that.
- **Reference chains, the lint.** The primitive was constructed in
  [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md) and its declaration format
  and deterministic generation are now Completed above. Still raw:
  the lint that fails when the declared chain and reality disagree.
- **Deslop regression gate.** Something must keep a rewritten document from
  sliding back into slop. Deterministic rules cannot judge prose quality;
  the judgments machinery may fit here.
- **Vocabulary change discipline.** A process that forces a conscientious
  decision on every term added to or removed from `CONTEXT.md`. Without one,
  terms accrete unexamined.
- **CLOA change discipline.** A process that forces a conscientious
  decision on every term used within a CLOA communication. Without one,
  vocabulary changes unchecked.

The core problem of this track: documentation needs far more reading by the
user than code does. Code is deterministic and can be pinned down by tools;
documentation can only be taken so far by them, so something has to keep it
a pleasure to read.

## Code track — parked

**Adopt**

- **ruff `C901`** — over-complex functions fail lint; no new dependency.
- **mypy, tightened** — exact flags undecided, not necessarily full
  `--strict`.
- **import-linter** — a declared contract over module dependencies
  ("`config` must not import `cli`"), failing CI when an import crosses a
  forbidden line.
- **Rendered API surface** — public signatures plus docstrings, the
  read-a-module-at-a-glance view. `griffe-outline` exists; evaluate it
  before reaching for mkdocstrings or pdoc.
- **`tests/acceptance/`** — see the tiers below.

**Undecided**

- **Hypothesis** — one readable property can replace fifty example tests.
- **Gherkin / BDD** — the most readable acceptance tests; worth
  remembering, not worth shoehorning in.
- **Mermaid sequence diagrams** — cheap to generate when tracing one
  operation.
- **coverage.py** — as a detector, not a percentage: uncovered code is
  code nothing forces to be correct.

**Rejected**

- **radon / xenon** — `C901` covers this in a running tool.
- **vulture** — dead code is not a priority.
- **pyright** — one type checker is enough.

**Notes**

- **Two testing tiers.** The unread tier: the existing thousand-odd unit
  tests, machine-written, judged by passing. The acceptance tier:
  `tests/acceptance/`, small and capped, written in `CONTEXT.md`
  terminology, one test per behavior the user could state in a sentence,
  read 100%. The deterministic gate that keeps the acceptance tier from
  bloating is undesigned — a size cap, naming rules, or a rule that every
  public module has at least one.
- **Gray modules.** If the user understands a module's tests and the tests
  pass, the user has an approximate understanding of the code beneath.
- **Import graph and call graph.** The import graph (modules, dozens of
  nodes) sits at the CLOA and import-linter can enforce rules on it; the
  call graph (functions, hundreds of nodes) sits below it, for tracing one
  operation. They disagree at type-only imports, callbacks and plugins, and
  `__init__.py` re-export hubs.
- **Docstrings.** The ruff `D` gate is live (pep257, `D401` off, `tests/`
  exempt) in pre-commit and `make check`. `D` checks presence and format
  only; docstring quality stays stochastic with the review agents, which is
  the right assignment.

## Terms

The terms this branch coined. Each line is the definition; the file that
works the term holds the detail. Every one is a tentative promotion to
`CONTEXT.md`: none is promoted until the user approves it.

- **acceptance tier** — the small, capped, fully read test suite in
  `tests/acceptance/`, one test per behavior the user could state in a
  sentence. Its opposite is the unread tier.
- **CLOA** — the level of abstraction where
  the AI and the user communicate in the exact same terminology.
- **constrain to optimize understanding** — the principle that a constraint
  on form pays for itself in amortized reading, meaningful location, and a
  lintable rule.
- **covering set** — the smallest group of exemplar runbooks that exercises
  every row of a design under test; edge encoding's is five runbooks.
- **gray module** — a module the user understands approximately, because the
  user understands its tests and the tests pass.
- **intent alignment debt** — divergence from the user's intent accrued over
  time; the mirror of tech debt.
- **layer invariance** — the loop is the same algorithm at any level, with
  adjacent runs joined by a map
  ([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#layer-invariance)).
- **the loop** — the expectation-maximization procedure that generates
  primitives from a target artifact
  ([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#an-em-loop-for-primitive-construction)).
- **the pandas standard** — the target state: fluency with an interface —
  which objects exist, which methods fit which task — without ever reading
  inside it.
- **Reference chain** — the declared tree of one runbook's behavior and its
  call signature (Reference Chain, under CLOA Abstractions).
- **registry pass** — the loop's first move on a repo: rule every registered
  document type important to the primitives ontology or not.
- **residual** — whatever the current abstractions cannot express; tracked,
  never forced.
- **runbook** — a skill or an agent definition; an invocable command that
  owns a Reference chain.
- **slop** — output that diverges from the user's intent (low quality) or
  that the user cannot read (not understood); the Goal section splits the
  two.
- **slop trench** — nominal ownership of a system whose details have
  outpaced inspection.
- **unread tier** — the existing thousand-odd machine-written unit tests,
  judged only by passing.
- **the vocabulary API** — `CONTEXT.md` designed the way a library designs
  its public surface, plus the escalation discipline that keeps it current.

## Acronyms

- **CLOA** — Correct Level of Abstraction.