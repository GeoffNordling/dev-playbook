---
type: General-Sheet
title: No More Slop
description: The branch plan — goal, the two tracks, the terms, and the current step
---

# No More Slop

The plan and state of the `no-more-slop` branch, deleted when the branch
merges. Material drains out of this file as it settles into the appropriate
long-term location.

This file is speculative, and the doc conventions' declarative voice does
not apply to it: a guess is written as a guess, an open question sits
inline next to its topic, and a sentence is settled only when it says so.

## Goal

No more slop: the user understands this repository without reading all of
it. Today they cannot — the repo sits in the slop trench, and its stock of
slop is mostly intent alignment debt. This branch works the documentation
track; the code track waits.

The doctrine behind the goal — slop's two kinds, the CLOA, the bedrock of
determinism, the pandas standard, the standing principles, the vocabulary
API — has drained into
[System Legibility](/docs/system-legibility.md).
Whether any of it hardens into a Standard card is held there, under
Ambitions.

## Zoom

Understanding operates at two zooms, for code and documentation alike:

- **Inside one file.** The user zooms in on a single file and reads it.
  What serves this zoom changes the file itself — wording, shape, length —
  never its meaning.
- **Above the file.** The user cannot read every file, so understanding up
  here comes from declared contracts: the doc-type machinery for
  documentation, established tooling for code.

Where the correct altitude sits, and what happens off it, is the CLOA
([System Legibility](/docs/system-legibility.md)).

## Documentation track — active

**Planned**

The theory is settled in
[Doc-Type](/doc-types/doc-type.md) and instantiated
in [Doc-Type System](/doc-types/doc-type-system.md);
the Runbook doc-type's shape and encoding sit in
[contract-shape.md](/doc-types/runbook/contract-shape.md)
and
[encoding.md](/doc-types/runbook/encoding.md).
One item remains:

- **When the parser runs.** The move landed the parser at
  `scripts/chaingen`, writing its generated view to
  `doc-types/runbook/chains.txt` — a temporary location, to be settled
  with the rest of this item. Undecided: when it runs. Today it runs by
  hand; the end state is a gate that fails when a declared chain and
  reality disagree. The same work settles shadowing: a runbook
  shadowing lint parallel to `standard.card-shadows-upstream` (a
  repo-local runbook may not reuse an upstream runbook's name), and
  where the no-shadowing rule itself lives — today it sits in
  [definition.md](/doc-types/standard/definition.md)'s Scope.
  Hierarchical imports across repositories are the mechanism under
  both; get that right, not fast.

**Completed**

- **CLOA primitives.** Three bootstrap runs plus an empirical close-out
  constructed a converged primitive set describing what documentation does
  at the CLOA; it settled as the Runbook doc-type's operations
  ([contract-shape.md](/doc-types/runbook/contract-shape.md#edges)).
  That files are still too hard to read is a separate open work stream
  (the inside-one-file zoom).
- **Deslop rewrite.** Every prose document rewritten in place against
  [Slop Tics](/standards/prose/slop-tics.md). Productionized as the
  `/document-deslop` skill, which the user invokes manually.
- **Documents hold behavior; skills and agents hold procedure.**
  Standardized in
  [file-roles.md](/standards/knowledge-organization/file-roles.md).
- **Edge encoding and its parser.** The Reference chain's in-file
  declaration format, designed on a five-runbook covering set and ruled
  in
  [encoding.md](/doc-types/runbook/encoding.md),
  proven by `scripts/chaingen`, which regenerates every covered
  runbook's chain into `doc-types/runbook/chains.txt` and fails on drift via
  `--check`.
- **First-party port.** Every runbook authored in this repo — all
  twelve agents and the unmarked skills in the Port roster,
  38 runbooks — ported to the edge encoding by a fixed dispatch
  prompt, since retired, each with its leftovers recorded in the
  [residual ledger](/doc-types/runbook/residual-ledger.md).
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
  [0026](/docs/decisions/0026-retire-verbatim-skill-adoption.md) changed
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
  is manual: the user updates the rows by hand. Recorded in 0026.
- **Converted-skill port.** The former (3P) ten, owned since 0026, went
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
- **Recursion to the bedrock of determinism.** The note is developed and
  placed: the bedrock is defined in
  [System Legibility](/docs/system-legibility.md),
  and [Doc-Type](/doc-types/doc-type.md) carries
  the loop's layer-invariance and the primitive map. The bedrock is where
  documentation stops and code begins — documentation is the stochastic
  thing, code the deterministic one, the same split this file's two
  tracks make. The recursion does not halt at the boundary — the mode
  flips, from inventing machinery with the loop to choosing pre-existing
  tools.
- **The terminology refactor.** The loose uses of "primitive" and
  "ontology" became a settled vocabulary — doc-type, operation,
  composition rule, shape, contract, grain, layer, primitive, primitive
  map — defined once in
  [Doc-Type](/doc-types/doc-type.md); "ontology"
  is reserved for a future solver
  ([System Legibility](/docs/system-legibility.md),
  Ambitions).
- **The working set rebuilt as the future doc-type tree.** Every theory
  file rewritten under its future basename: system-legibility.md (the
  doctrine), doc-type.md (the kind), doc-type-system.md (this repo's
  instantiation), and the Runbook doc-type's four files
  (runbook-definition.md, runbook-contract-shape.md, runbook-encoding.md,
  runbook-residual-ledger.md). CLOA-ABSTRACTIONS.md and TYPES.md drained
  into these and were deleted.
- **The migration.** Every working file moved to its long-term home: the
  doctrine to `docs/system-legibility.md`, the theory and the Runbook
  doc-type into `doc-types/`, the parser to `scripts/chaingen` writing
  `doc-types/runbook/chains.txt`. The Standard doc-type was born in the
  same move: `standards/standard/format.md` split into
  `doc-types/standard/` (definition, contract shape, encoding, an empty
  residual ledger), its detector contract and drift machinery staying
  behind as `standards/standard/detectors.md`, and the Meta-Standard
  card's Define cell now points at the split files. Every inbound link
  repointed; the migration instruction sheet died with the move.

- **The grammar triplication dissolved.**
  `standards/harness/grammar.md` predated the doc-type concept — it was
  where the Runbook primitives were shoehorned before they had a home —
  and after the migration it declared the same vocabulary a third time,
  beside `doc-types/runbook/contract-shape.md` and `encoding.md`. It is
  deleted. contract-shape.md is now the sole vocabulary declaration
  (gaining the prohibition operation, the read buckets, and the
  edges-live-at-the-definition-site stitching rule, which existed
  nowhere else); encoding.md is the sole declaration of written form
  and says a primitive is never born there. The harness standard keeps
  only its own question — `files.md`'s runbook class points at the
  Runbook doc-type for the body.

**Raw ideas, none designed**

- **Each new document is a giant pile of slop.** Each new major document the
  AI writes is a pile of slop the user wades through, iterating with the AI to
  bring it to acceptable condition. Every one of those passes is an
  opportunity to codify general rules, procedures, and algorithms for writing
  documents correctly: each linear slop trench session should spin the
  flywheel and climb out of the trench. There is no flywheel today, and the
  climb has not started.
- **Markdown complexity detectors.** No specifics yet on how to measure a
  document's complexity — the goal is a file the user can read without
  checking out on opening.
- **Doc linters, re-aimed.** The existing linters are pedantic — they check
  that certain headings are present. Decide what is worth linting for and
  design toward that.
- **Deslop regression gate.** Something must keep a rewritten document from
  sliding back into slop. Deterministic rules cannot judge prose quality;
  the judgments machinery may fit here.
- **Vocabulary change discipline.** A process that forces a conscientious
  decision on every term added to or removed from `CONTEXT.md`. Without one,
  terms accrete unexamined.
- **CLOA change discipline.** A process that forces a conscientious
  decision on every term used within a CLOA communication. Without one,
  vocabulary changes unchecked.
- **The inheritance pattern has no single home.** dev-playbook declares a
  system once, consumers inherit it, a repo declares only what is local —
  stated per-system in `CLAUDE.md`, the Standard doc-type's Scope, and
  document-types.md's Local extensions. A candidate for
  [System Legibility](/docs/system-legibility.md) or a standard of its
  own.

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
- **the bedrock of determinism** — the boundary where targets stop being
  stochastic; below it the work is mostly choosing pre-existing tools
  ([System Legibility](/docs/system-legibility.md)).
- **bucket** — the target class of a write: git, GitHub, local file, or
  scratch
  ([contract-shape.md](/doc-types/runbook/contract-shape.md#edges)).
- **CLOA** — the best-effort shared level where the user and the AI
  communicate in the exact same terminology: the highest level the user
  can trust the AI at, the lowest the AI needs the user at
  ([System Legibility](/docs/system-legibility.md)).
- **composition rule** — how many operations an instance may carry and in
  what arrangement
  ([Doc-Type](/doc-types/doc-type.md)).
- **constrain to optimize understanding** — the principle that a constraint
  on form pays for itself in amortized reading, meaningful location, and a
  lintable rule
  ([System Legibility](/docs/system-legibility.md)).
- **contract** — everything a caller of an instance may rely on; contains
  the signature — args in, results out — as its machine-checkable core
  ([Doc-Type](/doc-types/doc-type.md)).
- **covering set** — the smallest group of exemplar runbooks that exercises
  every row of a design under test; edge encoding's is five runbooks.
- **doc-type** — operations plus a composition rule, handing one
  documentation family a contract shape
  ([Doc-Type](/doc-types/doc-type.md)).
- **grain** — a doc-type axis: type-level, one contract serves every
  instance; instance-level, each instance fills the shape its own way
  ([Doc-Type](/doc-types/doc-type.md)).
- **gray module** — a module the user understands approximately, because the
  user understands its tests and the tests pass.
- **instance** — one member of a documentation family; it has a contract,
  it is not one
  ([Doc-Type](/doc-types/doc-type.md)).
- **intent alignment debt** — divergence from the user's intent accrued over
  time; the mirror of tech debt
  ([System Legibility](/docs/system-legibility.md)).
- **layer** — a rung where one loop run happened; the loop is
  layer-invariant, the same algorithm at any rung
  ([Doc-Type](/doc-types/doc-type.md#layers-and-the-primitive-map)).
- **the loop** — the expectation-maximization procedure that produces a
  doc-type from its target
  ([Doc-Type](/doc-types/doc-type.md#the-loop)).
- **operation** — an action instances of a family support
  ([Doc-Type](/doc-types/doc-type.md)).
- **the pandas standard** — the target state: a declared abstraction feels
  like an imported one to its caller — fluency without ever reading inside
  ([System Legibility](/docs/system-legibility.md)).
- **primitive** — one of a layer's atomic units
  ([Doc-Type](/doc-types/doc-type.md)).
- **the primitive map** — the join between two adjacent layers: one lower
  expression per higher primitive
  ([Doc-Type](/doc-types/doc-type.md#layers-and-the-primitive-map)).
- **provenance** — whether an abstraction is declared in this corpus or
  imported from outside it
  ([System Legibility](/docs/system-legibility.md)).
- **Reference chain** — the Runbook doc-type's contract shape: one
  runbook's behavior and call signature as nodes and edges
  ([contract-shape.md](/doc-types/runbook/contract-shape.md)).
- **registry pass** — the loop's first move on a repo: rule every
  registered document kind important to the type system or not
  ([Doc-Type](/doc-types/doc-type.md#the-loop)).
- **residual** — whatever the current primitives cannot express; tracked,
  never forced.
- **runbook** — a skill or an agent definition; an invocable command
  ([definition.md](/doc-types/runbook/definition.md)).
- **shape** — the form every contract in a family takes, fixed by the
  family's operations and composition rule
  ([Doc-Type](/doc-types/doc-type.md)).
- **slop** — output that diverges from the user's intent (low quality) or
  that the user cannot read (not understood)
  ([System Legibility](/docs/system-legibility.md)).
- **slop trench** — nominal ownership of a system whose details have
  outpaced inspection
  ([System Legibility](/docs/system-legibility.md)).
- **span** — the braced unit inside runbook prose that serves the executing
  agent and the parser from one sentence
  ([encoding.md](/doc-types/runbook/encoding.md#from-prose-to-chain)).
- **unread tier** — the existing thousand-odd machine-written unit tests,
  judged only by passing.
- **the vocabulary API** — `CONTEXT.md` designed the way a library designs
  its public surface, plus the escalation discipline that keeps it current
  ([System Legibility](/docs/system-legibility.md)).

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **EM** — Expectation-Maximization: the two-step statistical procedure the
  loop is shaped after.
