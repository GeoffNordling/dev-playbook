# Session: dev\_playbook

<session id="164eb714-6a1c-48af-a8bc-e1fa1dec76de" project="dev_playbook" agent="Claude" started_at="2026-08-30T13:59:26.676Z" ended_at="2026-08-30T15:37:55.665Z" message_count="75">
<message role="user" ordinal="0" timestamp="2026-08-30T13:59:26.676Z">
/clear
</message>
<message role="user" ordinal="1" timestamp="2026-08-30T13:59:40.522Z">
Load no-more-slop-branch-working-files/NO-MORE-SLOP.md
</message>
<message role="assistant" ordinal="2" timestamp="2026-08-30T13:59:43.106Z" has_tool_use="true">
<tool_call id="toolu_01KHDZXKYcqdyQ2ijvB11jpJ" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md","description":"Read NO-MORE-SLOP.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md
]]></tool_body>
<tool_result><![CDATA[
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
forward, appropriate structure and abstractions maintain user
understanding and prevent new debt from accruing.

## Levels

Understanding happens at multiple levels, for code and documentation alike:

- **Inside one file.** The user zooms in on a single file and looks at it.
  What serves this level changes the file itself — wording, shape, length —
  never its meaning.
- **Above the file.** The user cannot read all files at once, so understanding
  at the higher levels has to come some other way. Code has established tools
  at this level; documentation gets similar abstractions constructed for it.

Across the levels runs an abstraction/detail axis with a latent optimal
point neither party knows a priori. Too low — too much detail — and the
user stops paying attention, rubber stamps, and intent alignment debt
accumulates; too high and the user is temporarily fooled into thinking they
understand. Both ends produce slop. Pre-AI interfaces were forcing
functions: pandas and git impose their abstractions, and a wrong mental
model did not survive contact with them. Natural language imposes no such
constraints, so interfaces at the appropriate level of abstraction are
engineered deliberately.

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

**Planned**

The ontology is settled in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md);
the encoding design and its parser sit in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
beneath
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
Two items remain:

- **Recursion to the bedrock of determinism.** Develop the note: the
  [EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#an-em-loop-for-primitive-construction)
  applies all the way down until the target stops being stochastic; maps
  recurse one rung further — grammar ↔ parser, the certified transform,
  pinned by `--check`.
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
  declaration format, designed on a five-runbook covering set and ruled
  in
  [Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
  proven by `parser/chaingen.py`, which regenerates every covered
  runbook's chain into `parser/chains.txt` and fails on drift via
  `--check`.
- **First-party port.** Every runbook authored in this repo — all
  twelve agents and the unmarked skills in the Port roster,
  38 runbooks — ported to the edge encoding by a fixed dispatch
  prompt, since retired, each with its leftovers recorded in the
  [Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).
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
- **Working-file reorganization.** The branch's working files rebuilt
  as a tree with one job per file: Reference Chain Declaration holds
  the object, Reference Chain Encoding beneath it is the writer's
  spec, the Residual Ledger is the one system-wide record, and Port
  Prompt retired.

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
- **bucket** — the target class of a write: git, GitHub, local file, or
  scratch
  ([Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md#edges)).
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
- **the primitive map** — the join between two adjacent loop layers: one
  lower expression per higher primitive
  ([Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#the-primitive-map)).
- **provenance** — whether an abstraction is declared in this corpus or
  imported from outside it
  ([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs)).
- **Reference chain** — the declared tree of one runbook's behavior and its
  call signature
  ([Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)).
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
- **span** — the braced unit inside runbook prose that serves the executing
  agent and the parser from one sentence
  ([Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#from-prose-to-chain)).
- **unread tier** — the existing thousand-odd machine-written unit tests,
  judged only by passing.
- **the vocabulary API** — `CONTEXT.md` designed the way a library designs
  its public surface, plus the escalation discipline that keeps it current.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **EM** — Expectation-Maximization: the two-step statistical procedure the
  loop is shaped after.
]]></tool_result>
</message>
<message role="assistant" ordinal="4" timestamp="2026-08-30T13:59:45.491Z">
Loaded. The branch plan is in context: goal (understand the repo without reading all of it), the CLOA/vocabulary-API/backpressure principles, doc track active with two items remaining (recursion-to-bedrock note, primitive/ontology terminology sweep), code track parked.

What next?
</message>
<message role="user" ordinal="5" timestamp="2026-08-30T13:59:47.079Z">
/working-doc-set-diagram that is the root
</message>
<message role="assistant" ordinal="6" timestamp="2026-08-30T13:59:51.454Z" has_tool_use="true">
<tool_call id="toolu_01AwZjEtPFx7Mo6hiXxgRmnN" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cd /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files \u0026\u0026 ls -R \u0026\u0026 echo \"=====\" \u0026\u0026 for f in *.md; do echo \"--- $f\"; grep -n '^## ' \"$f\"; done","description":"List working files and headings"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cd /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files && ls -R && echo "=====" && for f in *.md; do echo "--- $f"; grep -n '^## ' "$f"; done
]]></tool_body>
<tool_result><![CDATA[
This session is isolated in the worktree /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2, but this command is too complex to verify that it stays inside the worktree. Refusing to run it — a worktree-isolated session's git operations must target its own worktree. Split it into plain, separate commands and run them from /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2.
]]></tool_result>
</message>
<message role="assistant" ordinal="8" timestamp="2026-08-30T13:59:54.882Z" has_tool_use="true">
<tool_call id="toolu_01Ms8YadgFJ1dN7qQkcwEUbt" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"ls -R /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files","description":"List working files"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ ls -R /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files
]]></tool_body>
<tool_result><![CDATA[
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files:
CLOA-ABSTRACTIONS.md
index.md
NO-MORE-SLOP.md
parser
REFERENCE-CHAIN-DECLARATION.md
REFERENCE-CHAIN-ENCODING.md
RESIDUAL-LEDGER.md

/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser:
chaingen.py
chains.txt
]]></tool_result>
</message>
<message role="assistant" ordinal="10" timestamp="2026-08-30T13:59:56.831Z" has_tool_use="true">
<tool_call id="toolu_01MYdarKzFc3umpSPYdtXLeN" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"grep -n '^## ' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/*.md","description":"Get section headings"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ grep -n '^## ' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/*.md
]]></tool_body>
<tool_result><![CDATA[
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:27:## From prose to chain
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:64:## The primitive map
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:98:## Writing the spans
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:170:## Acronyms
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:16:## Goal
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:22:## Documentation is code
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:41:## Three readers
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:52:## A noun with one or more verbs
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:78:## An EM loop for primitive construction
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:173:## Scope
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:193:## Registry dispositions
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:220:## Acronyms
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:15:## Runbooks
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:355:## Acronyms
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:18:## The chain
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:30:## Nodes
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:53:## Edges
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:84:## Acronyms
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:17:## Goal
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:44:## Levels
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:65:## Principles
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:105:## The pandas standard
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:118:## Documentation track — active
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:247:## Code track — parked
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:299:## Terms
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:359:## Acronyms
]]></tool_result>
</message>
<message role="assistant" ordinal="12" timestamp="2026-08-30T14:00:02.777Z" has_tool_use="true">
<tool_call id="toolu_018tgCrECcgF8haKHm3BJ51K" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"grep -no '(/no-more-slop-branch-working-files/[^)]*)' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md","description":"Find cross-references"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ grep -no '(/no-more-slop-branch-working-files/[^)]*)' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md
]]></tool_body>
<tool_result><![CDATA[
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:10:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:152:(/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:11:(/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:18:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:21:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:10:(/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:15:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:33:(/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:42:(/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:72:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#the-primitive-map)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:74:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:82:(/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:12:(/no-more-slop-branch-working-files/NO-MORE-SLOP.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:74:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:102:(/no-more-slop-branch-working-files/NO-MORE-SLOP.md#the-pandas-standard)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:109:(/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:140:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:200:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:201:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:11:(/no-more-slop-branch-working-files/NO-MORE-SLOP.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:16:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:19:(/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:20:(/no-more-slop-branch-working-files/NO-MORE-SLOP.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:21:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:22:(/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:23:(/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md)
]]></tool_result>
</message>
<message role="assistant" ordinal="14" timestamp="2026-08-30T14:00:11.682Z">
<code_block><![CDATA[
index.md
   │
   ▼
NO-MORE-SLOP.md ···················· branch plan: Goal · Levels ·
   │                                 Principles · The pandas standard ·
   │                                 Documentation track · Code track ·
   │                                 Terms · Acronyms
   ▼
CLOA-ABSTRACTIONS.md ··············· ontology: Goal · Documentation is
   │        │                        code · Three readers · A noun with
   │        │                        one or more verbs · An EM loop for
   │        │                        primitive construction · Scope ·
   │        │                        Registry dispositions · Acronyms
   │        └───────────────────────┐
   ▼                                ▼
REFERENCE-CHAIN-           RESIDUAL-LEDGER.md
DECLARATION.md             system-wide residual record:
   │      the object:      Runbooks · Acronyms
   │      The chain ·
   │      Nodes · Edges ·
   │      Acronyms
   ▼
REFERENCE-CHAIN-ENCODING.md ········ writer's spec: From prose to chain ·
   │                                 The primitive map · Writing the
   │                                 spans · Acronyms
   ▼
parser/ ···························· chaingen.py · chains.txt
]]></code_block>
</message>
<message role="user" ordinal="15" timestamp="2026-08-30T14:30:53.112Z">
/model
</message>
<message role="user" ordinal="16" timestamp="2026-08-30T14:31:11.184Z">
Have you read all the files in full? yes or no
</message>
<message role="assistant" ordinal="17" timestamp="2026-08-30T14:31:14.007Z">
No — only NO-MORE-SLOP.md in full. For the other five I grepped headings and cross-references to draw the diagram.
</message>
<message role="user" ordinal="18" timestamp="2026-08-30T14:31:50.223Z">
We&#39;re going to work on this part now:

## Documentation track — active

**Planned**

The ontology is settled in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md);
the encoding design and its parser sit in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
beneath
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
Two items remain:

- **Recursion to the bedrock of determinism.** Develop the note: the
  [EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#an-em-loop-for-primitive-construction)
  applies all the way down until the target stops being stochastic; maps
  recurse one rung further — grammar ↔ parser, the certified transform,
  pinned by `--check`.
- **Primitive and ontology terminology sweep.** &#34;Primitive&#34; and
  &#34;ontology&#34; are used loosely across these files; tighten every use.

Read all the files in full, and then your only job is to report which ones you should have read. then we will back up the conversation, and you will read only the relevant files to these objectives.
</message>
<message role="assistant" ordinal="19" timestamp="2026-08-30T14:31:52.421Z" has_tool_use="true">
<tool_call id="toolu_017V2zq1onAujFvmcGUK2Qo9" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md","description":"Read index.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md
]]></tool_body>
<tool_result><![CDATA[
---
okf_version: "0.1"
---

# no-more-slop-branch-working-files — Bundle Index

Temporary tracking files for the `no-more-slop` branch. The whole folder is
deleted when the branch merges; material drains out of it into long-term
locations as it settles.

Start at [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md):
it is the branch plan, and it holds the goal, the principles, the terms, and
the next steps for the work as a whole. The other files hang beneath it.

One subdirectory carries no index of its own, and
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
owns what it holds: `parser/`, holding `chaingen.py` and `chains.txt`.

- [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md) — The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
- [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md) — The branch plan — goal, principles, the two tracks, and the current step
- [Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) — The Reference chain declared — a runbook's behavior and call signature as nodes and edges
- [Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md) — The layer below the declaration — the spec a writer follows to encode chain edges in runbook prose
- [Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md) — The system-wide record of what the current abstractions cannot express — one section per registry type ruled important
]]></tool_result>
</message>
<message role="assistant" ordinal="21" timestamp="2026-08-30T14:31:53.827Z" has_tool_use="true">
<tool_call id="toolu_01X2dXRaa7V3ih4EvJhCy89m" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md","description":"Read CLOA-ABSTRACTIONS.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: CLOA Abstractions
description: The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
---

# CLOA Abstractions

The **CLOA primitives ontology**: the abstractions the user and the AI
share at the CLOA — each a noun with a small fixed verb set — and, as a
detail of method, the loop that generates them. An offshoot of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md). The
same speculative voice applies: a guess is written as a guess, and a
sentence is settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
entire repository — without having to read all of it.

## Documentation is code

Documentation is code: it does things because agents do things, and an agent
is just documentation, a harness, and permissions.

Unfortunately, documentation is also stochastic and extremely high-dimensional.
Parsimonious structure added on top constructs
high-level abstractions capturing the important parts the user cares about.
Keep the structure simple, lintable, deterministic, and high leverage.

Treat documentation as a special case
of code; pre-existing methods for code may work for documentation also,
with minimal modifications. When facing a difficult problem in documentation,
translate to the code form, solve it there, and port the analogy back. For
example, each document should probably have a typed signature.

Documentation abstractions change the
way codebases do — refactors are possible but costly.

## Three readers

Every structure decision must serve the readers below, in priority order:

1. **The executing agent** — the primary customer. Runbook prose commands
   the agent in natural imperative English; nothing may clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parsers that generate views and the lints
   that enforce grammars. Served by subtle helpers, never by machine
   notation embedded in prose.

## A noun with one or more verbs

One noun carrying a small fixed verb set. Nouns describe;
verbs act. Naming nouns and giving them verbs is deterministic
structure at the level of ideas.

Every abstraction carries a **provenance**: declared or imported. A
declared abstraction is invented here and declared in this corpus —
Standard, the Reference chain. An imported abstraction is someone
else's, taken as a dependency — GitHub, git, `str` — its contract as
given.

Implemented exemplars so far:

**Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from those verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts.

**Runbook Reference chain**: the noun is the
chain, the verbs are its edge labels, and its node types ride along as
one-verb nouns — both rosters declared in
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
It allows the user to understand a runbook's behavior without opening
the body.

## An EM loop for primitive construction

In code, the programming language comes first and the functionality second.
Thus, functionality may be expressed as code, constrained by the primitives
that were defined by the language in advance.

Expressing existing documentation as code hits a problem: documentation
has free-form, infinite possibilities. No constrained programming language
exists a priori: the language is English itself.

The solution is a backwards operation combining AI proposals with user
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
- **Convergence** is
  [the pandas standard](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#the-pandas-standard):
  the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal — good abstractions are a codebook the corpus gets short in,
  so functionality per character runs high.

Track residuals in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).
The loop's job is awareness of what
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
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
where the target is skill prose and the output is a grammar. Two adjacent
runs connect through a map between the lower level's generated primitives
and the higher level's existing ones, written to a stateful location.
One-to-one is the ideal — each higher
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
                                               │ the primitive map:
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
| Skill | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
| Agent definition | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
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

## Acronyms

None.
]]></tool_result>
</message>
<message role="assistant" ordinal="23" timestamp="2026-08-30T14:31:55.176Z" has_tool_use="true">
<tool_call id="toolu_01VXMK4AM2oRrpSVLNWmUJaH" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md","description":"Read REFERENCE-CHAIN-DECLARATION.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Declaration
description: The Reference chain declared — a runbook's behavior and call signature as nodes and edges
---

# Reference Chain Declaration

The **Reference chain** is one CLOA abstraction: the construction
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
rules for the runbook family. This file declares the object itself — its
nodes and its edges. The mechanics that construct a
chain from runbook prose — the primitive map and the rules for
writing spans — sit one layer down in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md). Same
working-file conventions as the branch plan sets out.

## The chain

A Reference chain is abstractions and the actions that connect them:
**nodes** joined by labeled **edges**, rooted at one runbook.

The chain's origin: a runbook is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
contract. The Reference chain is that contract written down: the
signature (args in, reports out) plus the effects, in the coarse order
they fire. Not full fidelity — the chain is a collapse of the runbook's
program, and the fine-grained sequencing it drops stays below the CLOA.

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub, a
file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | reads                  | —           | Its own noun and verbs, in [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs) |
| Agent    | does                   | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | does                   | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | does                   | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under its
node.

## Edges

An edge is an action. The six labels:

| Label | The action | Detail |
| ----- | ---------- | ------ |
| does | run a runbook or a script | — |
| reads | consult | — |
| overrides … with … | substitute a previous clause | — |
| writes | change state | target is one of four buckets — `git(commit, push)` |
| args | take the caller's input | by name — `friction` |
| reports | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type.

How each edge is written in runbook prose is ruled in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#the-primitive-map),
and how it draws in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md).

Any edge may carry a **condition** — what must hold for it to fire. A
conditional edge draws dashed; an unconditional edge draws solid. The
condition never changes the edge's type.

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Acronyms

None.
]]></tool_result>
</message>
<message role="assistant" ordinal="25" timestamp="2026-08-30T14:31:55.884Z" has_tool_use="true">
<tool_call id="toolu_01Cmvi4zCoANAT51dhZbKoeL" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md","description":"Read REFERENCE-CHAIN-ENCODING.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Encoding
description: The layer below the declaration — the spec a writer follows to encode chain edges in runbook prose
---

# Reference Chain Encoding

The layer below
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
how chain edges are written inside runbook prose, so deterministic
code can generate every chain. This file is the spec for the writer of
that prose. The primitive map below is the join between the two
layers — one lower expression per higher primitive. The parser is
`parser/chaingen.py`, which writes every chain to `parser/chains.txt`
and fails on drift via `--check`; everything the writer does not
need — how an edge draws, how a name resolves — lives in that code and
nowhere else. Same working-file conventions as the branch plan sets
out.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What binds 100% is
the small grammar below, to be specified as a standard card and enforced
by a lint.

## From prose to chain

A chain edge must come out of the same sentence that commands the
executing agent — no writer maintains two copies. The **span** is how
one sentence serves both readers: braces mark the one machine-readable
unit inside otherwise plain prose. The parser slices a span at fixed
cut points — the keyword, the links, the splitters — and every word
between cuts is an opaque string it carries but never reads, so the
payload stays natural language for the agent. The two mix freely in
one sentence, and the boundary cuts both ways: unmarked prose is never
an edge — unbraced `if` is the deliberate way to keep a condition out
of the chain — and prose never restates a span; a sentence that
shadows a primitive becomes the span or is reworded away.

Two live uses. In each, the span is the prose as it stands in the
runbook file, and the edge below it is what the deterministic parser
generates from that span. A simple read, from intake:

```
{Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md);
the brief formats, brief principles, and the readiness bar}

  ├─reads───► [issue-authoring] Standard
```

A condition nesting a read, from design:

```
{If §2 settled that the public surface is load-bearing,
{Read [design-it-twice.md](references/design-it-twice.md)} and work through it}

  ├ ╌ reads ╌ ► design-it-twice.md    if §2 settled that the public surface is load-bearing
```

The rest of this file builds that trip up piece by piece: which
primitives come from where, and the rules for writing each span.

## The primitive map

Every higher primitive is either **derived** from the runbook's file or
**declared** in its body as a span.

The derived primitives:

| Primitive | Source | Detail |
| --------- | ------ | ------ |
| node type | the file path | `agents/` is an Agent, `SKILL.md` a Skill, `scripts/` or a script extension a Script |
| node data | frontmatter, verbatim | — |
| runbook summary | frontmatter `description` | — |
| args | frontmatter `arguments` list | names only — the name carries the meaning; no placeholder in the body |

The declared primitives:

| Primitive | Span |
| --------- | ---- |
| reads | `{Read <one link>}` |
| reads — GitHub | `{Read from GitHub …}` |
| writes — local file | `{Write …}` |
| writes — GitHub | `{Write to GitHub …}` |
| writes — scratch | `{Write to scratch …}` |
| writes — git | `{Commit …}` + fenced command |
| does — Agent | `{Launch <one link>}` |
| does — Skill or Script | `{Run <one link>}` |
| overrides … with … | `{Override <link> … with <link> …}` |
| reports | `{Report …}` |
| condition | `{If <condition>, {…}}` |
| prohibition | `{Never {…}}` |

Keywords are imperative — commands to the executing agent; the chain's
edge labels are their third-person translation.

## Writing the spans

A span is `{keyword payload}`: flat by default, nested at most two
deep — `If` and `Never` spend the cap. The keyword matches
case-insensitively, a span may wrap across source lines, and spans
count only outside code spans and fenced blocks. The rules for each
declared form, refining the table above:

**Targets.** Where the table says `<one link>`, exactly one markdown
link in the payload names the target; every other word is annotation —
instruction to the executing agent, never read by the parser. One
target per span: two reads are two spans. A does-link points at the
live harness path (`~/.claude/skills/…`, `~/.claude/agents/…`). A
`#fragment` on any link must match a heading in the target file. A
linkless `{Read}` may instead carry one inline-code target
(`` {Read `CONTEXT.md` …} ``), taken verbatim.

```
{Run [/grilling](~/.claude/skills/grilling/SKILL.md) once to sharpen the raw idea}
```

The link is the target; "once to sharpen the raw idea" is annotation.

**Buckets.** The keyword picks the write bucket — `Commit` is git,
`Write` is local file — unless the payload opens with `to GitHub` or
`to scratch`; `from GitHub` does the same for `Read`. A `{Commit …}`
span requires a fenced git command block in the same step, and span
and block must agree.

```
{Write to scratch a self-ignoring `.datasheet/` directory}
```

The `to scratch` prefix picks the bucket; bare `{Write …}` would be
the local-file bucket.

**Splitters.** In `{If <condition>, {…}}`, the text before the first
nested span is the condition, lifted verbatim; every nested span fires
under it. In `{Override … with …}`, the word `with` splits the
payload — one link on each side, the overridden clause before, the
replacement after. In every payload, the first `;` ends what travels
to the chain: front the kernel, elaborate after the semicolon.

```
{Write the target document in place; it must say the same things
without committing any of the named tics}
```

"the target document in place" travels to the chain; everything after
the semicolon stays in the file.

**Prohibition.** `{Never {…}}` wraps exactly one span — inner keyword
`Write`, `Commit`, or `Merge` — and flips it from action to ban. A ban
the vocabulary cannot carry stays plain prose, recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

```
{Never {Commit}} — leave the changes in the working tree for review.
```

The span is the braces alone; the prose after the dash stays outside
it.

**Reports.** `{Report …}` reports the constant `outcome: str` — a
runbook's report is prose — with the payload as annotation.

```
{Report one line: worktree and branch removed, main at that commit}
```

The edge is `outcome: str`; the whole payload rides as annotation.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
]]></tool_result>
</message>
<message role="assistant" ordinal="27" timestamp="2026-08-30T14:31:57.293Z" has_tool_use="true">
<tool_call id="toolu_014GhCX7zc98vMqrfyUVWAWc" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md","description":"Read RESIDUAL-LEDGER.md"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Residual Ledger
description: The system-wide record of what the current abstractions cannot express — one section per registry type ruled important
---

# Residual Ledger

The system-wide record of residuals: what the current abstractions
cannot express. One section per registry type ruled important in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)'s
registry dispositions — only Runbooks today. That is all an entry is —
a record.

## Runbooks

Per runbook ported to the
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
what the full rewrite could not express, recognized and written down at
the moment of porting. Entries name spans and keywords in the vocabulary
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
declares.

An entry is a couple of sentences, hard limit: name each specific
action the file could not express and why the map cannot say it —
nothing else. No inventories of what fit, no family taxonomies, no
cross-references to other entries, no history, no restating the map's
rules.

### Accepted classes

Residual classes ruled on and accepted as-is, one line each, so no run
raises the same question twice. A construct listed here is real but
deliberately outside the ontology until a ruling is reversed.

- **Reality probes** — direct shell contact with repo state ("run the
  gate", "confirm the git tree is clean"). A real operation; ruled not
  accounted.
- **Attestation checkpoints** — "report `READ: x`, proceed only after."
  A prompt device that raises the probability the read happens; ruled
  not accounted.
- **Agent-held ephemeral state** — counts and set-aside lists a runbook
  tracks only in its own working memory, persisted nowhere
  (judgments-sweep's fix-attempt cap and skip list); ruled not
  accounted.
- **User interview loops** — a mid-run, multi-round dialogue with the
  user (runbook-creator's "iterate until the user is satisfied";
  grilling's whole body). Conversing is what running in the calling
  context means; ruled not accounted.
- **Behavior-mode setting** — a runbook whose body installs standing
  behavior in the session's ephemeral context and fires no edge at
  invocation (orchestrate: "everything below you is a subagent").
  Ruled residual; admitting it later requires a lintable,
  deterministic form.
- **Presentation gestures** — opening an already-written artifact for
  the user (improve-codebase-architecture's `xdg-open` on its report);
  part of reporting the value, never an edge; ruled not accounted.
- **Phase gates** — a step-scoped prohibition inside a runbook's own
  program, lifted by a later step (improve-codebase-architecture's "Do
  NOT propose interfaces yet"); internal sequencing below the CLOA,
  already covered by the steps-are-the-program rule; ruled not
  accounted.
- **Written-artifact semantics** — the schema and state rules of a
  document a runbook writes and later re-reads: wayfinder's map-body
  sections, fog lifecycle, HITL/AFK axis, claim-by-assignment, ticket
  sizing. The artifact's contract lives in the artifact; the chain
  records only the writes and reads that touch it.

### log-friction

Could not express the fire-and-forget behavior mode, the early exit
("and stop"), or the why-text calibrating judgment — no primitive for
any of the three.

### document-deslop

Partially ported; the Review section still waits. Could not express a
report that one branch deliberately withholds.

### usage-report

Could not express the script's own read of `usage.json` — a script has
no frontmatter or spans, so the does edge ends at the file.

### deslopper

Could not express being a Standard's enforce arm (flattened to a plain
read) or an agent's inputs — agents have no `arguments` frontmatter.

### handoff

Could not express telling the two reports apart — both render
`outcome: str`.

### ralph-setup

Could not express the report's name (`launch_command` rides only in
annotation) or the mid-run `READ:` acknowledgment, which targets the
conversation, not the invoker.

### commit

Could not express committing the ambient repo — `git_detail()` demands
a `-C <repo>` no honest same-repo command carries — or the
skip-the-amend decision itself; only its report has a primitive.

### clean-up-branch-worktree

Could not express the ambient-repo `git fetch`/`git merge`, the
`ExitWorktree` tool call (does covers only file-linked runbooks), or the
state-reading local `git` commands.

### idea

Could not express the delegation target's own behavior — the Run edge
resolves to mission-control's skill, outside the scanned corpus, so no
chain exists to stitch into — or the Overrides section, which binds
fixed values, not one linked runbook for another.

### rewind-compact

Could not express telling the two reports apart (both `outcome: str`).

### commit-off

Could not express the two exact-text mid-session acknowledgments —
they target the conversation, not the invoker, and no primitive covers
them.

### candidate-promote

Could not express reading the invoking repo's `CANDIDATES.md` —
`{Read}` needs one fixed on-disk link and the target changes per
invocation — or the typed report (`issue_number: int`) — reports
render only `outcome: str`.

### grilling

Could not express dispatching the fact-finding sub-agent — `{Launch}` needs
a link to one agent definition file, and this is an unnamed, ad hoc
dispatch with none. Could not express the round-by-round design-tree loop
itself (no primitive for an iterative Q&A frontier) or the closing
"do not act on it until the user confirms" prohibition — it is
conditional on the user's confirmation, and the Never vocabulary has no
verb for acting.

### orchestrate

Could not express launching runtime-chosen subagents — `{Launch}`
needs a link to one agent file and none exists — or the persistent
session posture, which no primitive covers.

### intake

Could not express the mode→phase routing table (a table has no
sentence for the grammar to span). `software-factory.md` renders as
bare link text: `classify()` has no type for docs outside
`standards/`.

### runbook-creator

Could not express the interview loop of steps 2 and 6 (no primitive
for a question-and-answer round), the `scripts/harness-files-lint` run (bare
command, no link for a does edge), or the step-completion gates (no
control-flow primitive).

### working-doc-set-deslop

Could not express the pre-flight `git status` check (no on-disk link, so
no `{Read}`) or the closing user verdict — accept-and-commit versus
reject-and-restore-to-`HEAD` — which no primitive covers.

### doc-pr-review

Could not express the audit act itself — no primitive for it — or the
diff-conditional standards table in § Read what the diff calls for — a
table has no sentence for the grammar to span. The escalation bullets in
§ 6 restate the condition rather than firing their own edges,
since the map has no primitive for enumerating alternative triggers
under one condition.

### adjudicator

Could not express the routing test and its dispositions
(§3–§4), the ordered-first-hit routing, or the callout distinction — no
control-flow or enumeration primitive for any of them. Could not express the
prompt's issue-number and verdict-word input — agents have no `arguments`
frontmatter — or the `READ:` acknowledgment, which targets the conversation,
not the invoker.

### build

Could not express the issue-number input (agents have no `arguments`
frontmatter), the open-ended "read the standard that governs the artifact"
instruction (an example-led rule, not an enumerable branch), telling the
escalation and completion reports apart (both render `outcome: str`), or
the gate runs (`make check`, §4 and §6) — a bare command in the ambient
repo, with no on-disk link for a does edge.

### design

Could not express the
`EnterWorktree`/`ExitWorktree` tool calls and worktree/branch git
commands (does covers only file-linked runbooks, and none carries a fenced
`-C` block for `{Commit}`), the approval gate spanning §6 into §7
(condition containment can't cross sections), the area-discovery and
probe-picking interviews (no primitive for a question-and-answer round
with the user), or the `READ:` acknowledgment (targets the
conversation, not the invoker).

### judgments-sweep

Could not express dispatching the judge fan-out — `Workflow({ name: "judgments", … })`
is neither an Agent nor a Skill/Script link, so does has no primitive for a
Workflow call.

### code-pr-review

Could not express the audit act itself — no primitive for it — or the
diff-conditional standards table
in § Read what the diff calls for, or the presence-check and
audit-dimension tables — a table has no sentence for the grammar to
span. The green-gate and PR/diff-missing
escalation bullets restate the condition rather than firing their
own edges, since the map has no primitive for enumerating alternative
triggers under one condition.

### compact-prep

Could not express step 2's "only if something stands out" condition —
the condition primitive gates a whole span, not a report's own contents.

### set-auditor

Could not express the set-member reads — the root and its linked working
files are runtime-bound (named in the launching prompt), so `{Read}`'s one
fixed on-disk link cannot cover them; they stay plain prose. Could not
express "ask no questions" — the Never vocabulary has no verb for it.

### agent-view-overwatch

Could not express the launch command handed to the user (no primitive for
an instruction the agent itself never runs), the teardown's
`git worktree remove`/`git branch -D` (writes—git bucket is scoped to
commits, not arbitrary git subcommands), or the board table (no
primitive for a rendered report's shape).

### bug-pr-review

The eight finder angles and their dedup/tag steps
are procedure, not edges, so the map has nothing to encode there.

### set-deslopper

Could not express reading every set member — `{Read}` needs one fixed
on-disk link, and set membership is runtime-determined.

### enable-repo-governance

Could not express the size-conditional
landing choice in § 5 (a decision, not a fixed condition) or the
GitHub-token permission preflight, which has no primitive.

### user-intent-mini-interview

Could not express the
ask/scrutinize/marry interview loop of steps 1–3 (no primitive for a
question-and-answer round).

### issue-overwatch

Could not express the
`EnterWorktree` calls and worktree-only git commands (does covers only
file-linked runbooks). The AFK/Inline/Review-stop engagement switch, including
the fixed `/open-pr` launch inside the Review-stop branch, has no primitive
for a multi-way enumeration — encoding just that one branch would misstate it
as unconditional. The runtime-chosen `Run /<skill> <N>` delegation has no
fixed link for `{Launch}` — tabled: the factory's node-delegation process is
in flux and likely to be overhauled, so no encoding is attempted for it now.

### open-pr

Could not express the local branch-diff read
(`git diff origin/main...issue-<issue>` — no on-disk link) or the
issue-number input (agents have no `arguments` frontmatter). The
alternate reports all collapse to `outcome: str`.

### update-standards-pin

Could not express the report-format table in § Read the report (a table
has no sentence for the grammar to span, so its `/enable-repo-governance`
mention stays unencoded too). Could not express the ambient dev-playbook
commit for a release-defect fix or the per-consumer commit/push — the
writes—git bucket needs a fenced command with a fixed `-C`, and neither the
ambient nor the runtime-chosen consumer repo carries an honest one — or the
`pre-commit gc` cleanup, a bare command with no on-disk link for a does
edge.

### issue-review-simulation

Could not express the read of whatever files the brief names —
`{Read}` needs one fixed on-disk link and they are runtime-bound.

### improve-codebase-architecture

Could not express spawning the
anonymous exploration sub-agent — `{Launch}` needs a link to one agent
definition file, and this is an ad hoc Task-tool call with none.

### diagnosing-bugs

Could not express the redact-every-secret discipline, a behavior-mode
setting with no primitive. Could not express Phase 3's ranked-list check-in
(targets the conversation mid-run, not a terminal report) or the
throwaway-harness and captured-trace writes — menu options among Phase 1's
ten ways, so an unconditional scratch edge would misstate them. Could
not express the commit that carries the confirmed hypothesis — writes—git
bucket needs a fixed `-C <repo>` a same-repo commit can't honestly carry.

### wayfinder-to-build

Could not express the mid-run `READ:` acknowledgment
(targets the conversation, not the invoker) or the per-step "Done when"
completion gates (no control-flow primitive).

### research

Could not express spawning the background research agent — `{Launch}` needs
a link to one agent definition file, and this is an ad hoc, unnamed dispatch
with none. Could not express reading primary sources — `{Read}` needs one
fixed on-disk link, and the sources vary with the question asked.

### domain-modeling

Could not express cross-referencing the code — the files consulted vary
with the claim under test, so there is no single target to name.

### wayfinder

Could not express the dead `/setup-matt-pocock-skills`
reference, since no such skill exists in this corpus — kept verbatim as
adopted. Could not express invoking whatever skill the map's Notes section
names, or an effort overriding the plan-don't-do default from that same
section — both are resolved from map content at runtime, not a link to one
fixed runbook. Could not express the research-branch write
(`research/<name>`) — writes—git bucket needs a fixed `-C` command block,
and the branch name is chosen per ticket.

### prototype

Could not express committing the prototype to a throwaway branch —
`git_detail()` requires a fixed `-C` fenced command, and here the repo
and branch are chosen at runtime, not fixed.

## Acronyms

- **AFK** — Away From Keyboard: a run that proceeds without the user present.
- **HITL** — the user in the loop: a run that stops for the user.
]]></tool_result>
</message>
<message role="assistant" ordinal="29" timestamp="2026-08-30T14:31:57.999Z" has_tool_use="true">
<tool_call id="toolu_0129bqwKveCzAXyyVjLkP2Zy" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py","description":"Read chaingen.py"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py
]]></tool_body>
<tool_result><![CDATA[
#!/usr/bin/env python3
"""chaingen — reconstruct a runbook's Reference chain from its encoded file.

Prototype implementing REFERENCE-CHAIN-ENCODING.md's certified transform: slice, never
interpret. Cut points are the keyword, the markdown
link(s), the `with` splitter, nested braces, and the first semicolon.
Everything between cut points is opaque verbatim text. A `#fragment` on a
read/launch/run link target splits off as a `§ fragment` annotation on the
edge, after failing loud unless it matches a heading slug in the target.
A `{Never {…}}` span wraps one primitive span and renders a prohibition
edge — `never <verb>`, the wrapped payload's kernel as target, possibly
empty. A bucket prefix opens a linkless payload and names the target
node: `{Write to GitHub …}` / `{Write to scratch …}` pick the write
bucket, `{Read from GitHub …}` the GitHub read.

Usage:
    chaingen.py            regenerate chains.txt — every runbook in the
                           corpus (dotfiles/dot-claude agents and
                           skills), blank-line separated
    chaingen.py --check    regenerate in memory and diff against
                           chains.txt; exit 1 on drift
"""

import difflib
import glob
import os
import re
import sys

LEXICON = {
    "read": "reads",
    "commit": "writes",
    "write": "writes",
    "report": "reports",
    "launch": "does",
    "run": "does",
    "override": "overrides",
    "if": "condition",
    "never": "never",
}

# A Never span wraps one primitive span and flips it from assertion to
# prohibition. Only these keywords can be prohibited; the label keeps each
# keyword's own verb — commit stays "commits", not the assertion fold to
# "writes", since no git block exists to disambiguate.
NEVER_LEXICON = {
    "write": "writes",
    "commit": "commits",
    "merge": "merges",
}

NODE_DATA_KEYS = ("tools", "model", "effort", "allowed-tools", "disallowed-tools")

# Bucket prefixes: a fixed literal opening a linkless payload picks the
# target node. Write buckets serve assertion and prohibition alike, so
# {Never {Write to GitHub}} draws the same GitHub node.
WRITE_BUCKETS = (("to GitHub", "GitHub"), ("to scratch", "scratch"))
READ_BUCKET = ("from GitHub", "GitHub")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

CODE_RE = re.compile(r"`([^`]+)`")

LABEL_FIELD = 8  # ─reads───► : label plus dashes fill 8 columns
SEP = "    "  # segment separator on an edge line


class LintError(Exception):
    """A grammar violation in an encoded file."""


# ── frontmatter ──────────────────────────────────────────────────────────


def split_frontmatter(text, path):
    """Split a runbook file into its frontmatter dict and body text."""
    lines = text.split("\n")
    if lines[0] != "---":
        raise LintError(f"{path}: no frontmatter")
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        raise LintError(f"{path}: unterminated frontmatter") from None
    meta = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, "\n".join(lines[end + 1 :])


def parse_arguments(meta):
    """Read the `arguments` frontmatter list — names only."""
    raw = meta.get("arguments", "")
    if not raw:
        return []
    if not (raw.startswith("[") and raw.endswith("]")):
        raise LintError(f"arguments not a list: {raw!r}")
    return [a.strip() for a in raw[1:-1].split(",") if a.strip()]


# ── span scanner ─────────────────────────────────────────────────────────
# Walks the body character by character. Backtick-delimited code (inline
# spans and fences alike) is inert: braces inside it never open or close
# a span, but its characters are captured verbatim into payloads.


class Span:
    """One braced span: payload text with nested spans elided."""

    def __init__(self, start):
        """Open a span at byte offset `start`."""
        self.start = start
        self.text = ""  # payload with nested spans elided
        self.children = []


def scan_spans(body):
    """Collect top-level spans, nesting capped at two deep."""
    spans, stack = [], []
    in_code = False
    i = 0
    while i < len(body):
        c = body[i]
        if c == "`":
            in_code = not in_code
        if not in_code:
            if c == "{":
                span = Span(i)
                if stack:
                    if len(stack) >= 2:
                        raise LintError(f"nesting deeper than two at offset {i}")
                    stack[-1].children.append(span)
                stack.append(span)
                i += 1
                continue
            if c == "}":
                if not stack:
                    raise LintError(f"unbalanced '}}' at offset {i}")
                span = stack.pop()
                span.end = i
                if not stack:
                    spans.append(span)
                i += 1
                continue
        if stack:
            stack[-1].text += c
        i += 1
    if stack:
        raise LintError(f"unclosed '{{' at offset {stack[-1].start}")
    if in_code:
        raise LintError("unbalanced backtick")
    return spans


def keyword_of(span):
    """Split a span into its lexicon keyword and payload."""
    stripped = span.text.lstrip()
    word = stripped.split(None, 1)[0] if stripped else ""
    key = word.lower()
    if key not in LEXICON:
        raise LintError(f"unknown keyword {word!r} in span at offset {span.start}")
    payload = stripped[len(word) :].strip()
    return key, payload


# ── slicing helpers ──────────────────────────────────────────────────────


def collapse(text):
    """Collapse whitespace runs — spans wrap across source lines."""
    return " ".join(text.split())


def kernel(text):
    """The first semicolon (outside inline code) ends the chain's view."""
    in_code = False
    for i, c in enumerate(text):
        if c == "`":
            in_code = not in_code
        elif c == ";" and not in_code:
            return text[:i]
    return text


def one_link(payload, where):
    """Extract the payload's single markdown link and the remainder."""
    links = LINK_RE.findall(payload)
    if len(links) != 1:
        raise LintError(f"{where}: expected exactly one link, found {len(links)}")
    text, target = links[0]
    remainder = collapse(LINK_RE.sub(" ", payload, count=1))
    return text, target, remainder


def split_bucket(payload, prefix):
    """The rest of a payload opening with the bucket prefix, or None."""
    pat = r"\s+".join(re.escape(w) for w in prefix.split())
    m = re.match(pat + r"\b", payload, re.IGNORECASE)
    if not m:
        return None
    return payload[m.end() :].strip()


def one_code(payload, where):
    """Extract a linkless payload's single inline-code target and the remainder."""
    codes = CODE_RE.findall(payload)
    if len(codes) != 1:
        raise LintError(
            f"{where}: a linkless Read needs exactly one inline-code target, "
            f"found {len(codes)}"
        )
    return codes[0], collapse(CODE_RE.sub(" ", payload, count=1))


# ── target classification ────────────────────────────────────────────────


def repo_root(start):
    """Walk up from `start` to the enclosing repository root."""
    d = os.path.abspath(start)
    while d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    raise LintError(f"no repo root above {start}")


def resolve(link_target, source_file):
    """Resolve a link target to an on-disk path; fail if it does not exist."""
    if link_target.startswith("~"):
        path = os.path.expanduser(link_target)
        # Same-repo resolution: a ~/workspace/<repo>/… path naming the repo
        # the source file lives in resolves inside that file's own checkout
        # (main or worktree), not the literal main checkout.
        m = re.match(r"~/workspace/([^/]+)/(.*)", link_target)
        if m:
            main = os.path.expanduser(f"~/workspace/{m.group(1)}")
            root = repo_root(os.path.dirname(source_file))
            if root == main or root.startswith(main + os.sep):
                path = os.path.join(root, m.group(2))
        # ~/.claude/ is this meta-repo's dotfiles/dot-claude tree, stowed;
        # from inside the repo it resolves to the checkout's own tree.
        m = re.match(r"~/\.claude/(.*)", link_target)
        if m:
            stowed = os.path.join(
                repo_root(os.path.dirname(source_file)), "dotfiles", "dot-claude"
            )
            if os.path.isdir(stowed):
                path = os.path.join(stowed, m.group(1))
    elif link_target.startswith("/"):
        path = os.path.join(
            repo_root(os.path.dirname(source_file)), link_target.lstrip("/")
        )
    else:
        path = os.path.join(os.path.dirname(source_file), link_target)
    if not os.path.exists(path):
        raise LintError(f"link target does not exist: {link_target} -> {path}")
    return path


def classify(link_text, link_target, source_file):
    """Render a link target as a node, or as the link text for a non-runbook."""
    real = os.path.realpath(resolve(link_target, source_file))
    base = os.path.basename(real)
    if base == "SKILL.md":
        name, ntype = os.path.basename(os.path.dirname(real)), "Skill"
    elif "/agents/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Agent"
    elif "/standards/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Standard"
    elif "/scripts/" in real or re.search(r"\.(sh|py|bash)$", base):
        # the path segment types extensionless scripts (repo-lint,
        # judgments-run), the same rule agents/ uses
        name, ntype = base, "Script"
    else:
        return link_text  # not a runbook: the link text travels verbatim
    return f"[{name}] {ntype}"


# ── fragment anchors ─────────────────────────────────────────────────────
# Mirrors dev_playbook.md's github_slug/heading_slugs — the package is not
# importable from this standalone prototype, so the regexes are copied.

SLUG_BACKTICK = re.compile(r"`([^`]*)`")
SLUG_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SLUG_STAR = re.compile(r"(\*{1,2})(.+?)\1")
SLUG_UNDERSCORE = re.compile(r"(?<!\w)(_{1,2})(?=\S)(.+?)(?<=\S)\1(?!\w)")
SLUG_DROP = re.compile(r"[^\w\s\-]")
SLUG_WHITESPACE = re.compile(r"\s")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(.*)$")


def github_slug(heading):
    """GitHub's anchor slug for a heading."""
    text = SLUG_BACKTICK.sub(r"\1", heading)
    text = SLUG_LINK.sub(r"\1", text)
    text = SLUG_STAR.sub(r"\2", text)
    text = SLUG_UNDERSCORE.sub(r"\2", text)
    text = SLUG_DROP.sub("", text.lower())
    return SLUG_WHITESPACE.sub("-", text)


def heading_slugs(path):
    """Slugs of every heading in the file at `path`, fenced code skipped."""
    slugs, fence = set(), None
    with open(path) as f:
        for line in f:
            m = FENCE_RE.match(line)
            if m:
                run, info = m.group(1), m.group(2)
                if fence is None:
                    fence = run
                    continue
                if run[0] == fence[0] and len(run) >= len(fence) and not info:
                    fence = None
                    continue
            if fence is None and (h := HEADING_RE.match(line)):
                slugs.add(github_slug(h.group(1)))
    return slugs


def split_anchor(link_target, source_file, where):
    """Split a #fragment off a link target; the fragment must name a heading."""
    target, _, fragment = link_target.partition("#")
    if not fragment:
        return link_target, ""
    if not target.endswith(".md"):
        raise LintError(f"{where}: #fragment on a non-markdown target: {link_target}")
    if fragment not in heading_slugs(resolve(target, source_file)):
        raise LintError(f"{where}: no heading slugs to '#{fragment}' in {target}")
    return target, fragment


# ── git bucket ───────────────────────────────────────────────────────────


def git_detail(body, after):
    """Read the git command after a Commit span: -C repo, subcommands in order."""
    for line in body[after:].split("\n"):
        stripped = line.strip()
        if stripped.startswith("git "):
            repo_m = re.search(r"-C\s+(\S+)", stripped)
            if not repo_m:
                raise LintError("git command block without -C")
            subs, seen = [], set()
            for m in re.finditer(r"git\s+(?:-C\s+\S+\s+)?([a-z-]+)", stripped):
                if m.group(1) not in seen:
                    seen.add(m.group(1))
                    subs.append(m.group(1))
            return f"git({repo_m.group(1)}: {', '.join(subs)})"
    raise LintError("Commit span with no git command block after it")


# ── edge construction ────────────────────────────────────────────────────


class Edge:
    """One chain edge: label, target, annotation, condition."""

    def __init__(self, label, target, annotation="", condition=""):
        """Build an edge; annotation and condition default empty."""
        self.label = label
        self.target = target
        self.annotation = annotation
        self.condition = condition


def edge_from_span(key, payload, span, body, source_file):
    """Slice one edge span into an Edge per its keyword's rule."""
    label = LEXICON[key]
    where = f"span at offset {span.start}"
    if key in ("read", "launch", "run"):
        if (
            key == "read"
            and (rest := split_bucket(payload, READ_BUCKET[0])) is not None
        ):
            # GitHub state read: no on-disk target exists, the prefix is
            # the whole address.
            if LINK_RE.search(payload):
                raise LintError(f"{where}: a from-GitHub Read carries a link")
            return Edge(label, READ_BUCKET[1], collapse(kernel(rest)))
        if key == "read" and not LINK_RE.search(payload):
            # Runtime-bound target: a file in the invoking repo, named as
            # inline code per the cross-reference standard's varied-location
            # row. No on-disk resolution — the node is the token verbatim.
            token, rest = one_code(payload, where)
            return Edge(label, f"`{token}`", collapse(kernel(rest)))
        _text, target, rest = one_link(payload, where)
        target, anchor = split_anchor(target, source_file, where)
        node = classify(_text, target, source_file)
        annotation = SEP.join(
            s for s in (f"§ {anchor}" if anchor else "", collapse(kernel(rest))) if s
        )
        return Edge(label, node, annotation)
    if key == "write":
        for prefix, node in WRITE_BUCKETS:
            if (rest := split_bucket(payload, prefix)) is not None:
                return Edge(label, node, collapse(kernel(rest)))
        return Edge(label, "local file", collapse(kernel(payload)))
    if key == "commit":
        return Edge(label, git_detail(body, span.end), collapse(kernel(payload)))
    if key == "report":
        return Edge(label, "outcome: str", collapse(kernel(payload)))
    if key == "override":
        left, sep, right = payload.partition(" with ")
        if not sep:
            raise LintError(f"{where}: Override without 'with'")
        ltext, ltarget, lrest = one_link(left, where + " (left of with)")
        rtext, rtarget, rrest = one_link(right, where + " (right of with)")
        lnode = classify(ltext, ltarget, source_file)
        rnode = classify(rtext, rtarget, source_file)
        annotation = SEP.join(
            s
            for s in (collapse(kernel(lrest)), f"with {rnode}", collapse(kernel(rrest)))
            if s
        )
        return Edge(label, lnode, annotation)
    raise LintError(f"{where}: keyword {key!r} is not an edge")


def edges_of(body, source_file):
    """All edges of a body in document order, conditions stamped."""
    edges = []
    for span in scan_spans(body):
        key, payload = keyword_of(span)
        if key == "never":
            if len(span.children) != 1:
                raise LintError(
                    f"Never at offset {span.start} must wrap exactly one span"
                )
            if collapse(payload):
                raise LintError(
                    f"Never at offset {span.start} carries prose outside its span"
                )
            child = span.children[0]
            stripped = child.text.lstrip()
            # the keyword is the leading alpha run — a semicolon may follow
            # it directly ({Never {Write; …}})
            m = re.match(r"[A-Za-z]+", stripped)
            word = m.group(0) if m else ""
            if word.lower() not in NEVER_LEXICON:
                raise LintError(
                    f"Never cannot prohibit {word!r} at offset {child.start}"
                )
            inner = stripped[len(word) :].strip()
            target, annotation = collapse(kernel(inner)), ""
            if word.lower() == "write":
                for prefix, node in WRITE_BUCKETS:
                    if (rest := split_bucket(inner, prefix)) is not None:
                        target, annotation = node, collapse(kernel(rest))
                        break
            edges.append(
                Edge("never " + NEVER_LEXICON[word.lower()], target, annotation)
            )
            continue
        if key == "if":
            if not span.children:
                raise LintError(f"condition at offset {span.start} nests no span")
            # condition: raw text between the keyword and the first nested
            # span, trailing comma dropped
            condition = collapse(
                kernel(
                    body[span.start + 1 : span.children[0].start]
                    .lstrip()[len(key) :]
                    .strip()
                    .rstrip(",")
                )
            )
            for child in span.children:
                ckey, cpayload = keyword_of(child)
                if ckey == "if":
                    raise LintError(
                        f"condition nested in condition at offset {child.start}"
                    )
                if ckey == "never":
                    raise LintError(
                        f"Never nested in condition at offset {child.start}"
                        " is not supported"
                    )
                edge = edge_from_span(ckey, cpayload, child, body, source_file)
                edge.condition = "if " + condition
                edges.append(edge)
        else:
            edges.append(edge_from_span(key, payload, span, body, source_file))
    return edges


# ── rendering ────────────────────────────────────────────────────────────


def render_edge(edge, last):
    """Render one edge line — dashed when conditional, solid otherwise."""
    corner = "└" if last else "├"
    if edge.condition:
        arrow = f"{corner} ╌ {edge.label} ╌ ►"
    else:
        pad = "─" * max(1, LABEL_FIELD - len(edge.label))
        arrow = f"{corner}─{edge.label}{pad}►"
    segments = [s for s in (edge.target, edge.annotation, edge.condition) if s]
    if not segments:  # a total prohibition: bare arrow, empty node slot
        return f"  {arrow}"
    return f"  {arrow} " + SEP.join(segments)


def render_unit(path):
    """Render one runbook file as its full chain, header plus edges."""
    with open(path) as f:
        text = f.read()
    meta, body = split_frontmatter(text, path)
    real = os.path.realpath(path)
    ntype = "Agent" if "/agents/" in real else "Skill"
    braces = "{{{}}}" if "/.agents/" in real else "[{}]"
    data = ", ".join(f"{k}: {meta[k]}" for k in meta if k in NODE_DATA_KEYS)
    header = f"{braces.format(meta['name'])} {ntype}" + (f" · {data}" if data else "")
    edges = [Edge("args", a) for a in parse_arguments(meta)]
    edges += edges_of(body, os.path.abspath(path))
    lines = [header]
    for i, edge in enumerate(edges):
        lines.append(render_edge(edge, i == len(edges) - 1))
    return "\n".join(lines) + "\n"


# ── entry ────────────────────────────────────────────────────────────────


def all_runbooks(claude_dir):
    """Every runbook in the corpus: agents/*.md, then skills/*/SKILL.md."""
    runbooks = sorted(glob.glob(os.path.join(claude_dir, "agents", "*.md")))
    runbooks += sorted(glob.glob(os.path.join(claude_dir, "skills", "*", "SKILL.md")))
    return runbooks


def unit_name(path):
    """A runbook's display name: the skill's directory or the agent's basename."""
    base = os.path.basename(path)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(path))
    return base[: -len(".md")]


def main(argv):
    """Write chains.txt, or with --check diff against it."""
    here = os.path.dirname(os.path.abspath(__file__))
    chains_path = os.path.join(here, "chains.txt")
    runbooks = all_runbooks(os.path.join(here, "..", "..", "dotfiles", "dot-claude"))
    rendered = []
    for p in runbooks:
        try:
            rendered.append(render_unit(p))
        except LintError as e:
            raise LintError(f"{unit_name(p)}: {e}") from None
    text = "\n".join(rendered)
    if argv == ["--check"]:
        if not os.path.exists(chains_path):
            print("DRIFT: chains.txt does not exist")
            return 1
        with open(chains_path) as f:
            want = f.read()
        if text == want:
            print(f"OK: chains.txt matches all {len(runbooks)} runbooks")
            return 0
        print("DRIFT:")
        sys.stdout.writelines(
            difflib.unified_diff(
                want.splitlines(keepends=True),
                text.splitlines(keepends=True),
                "chains.txt",
                "regenerated",
            )
        )
        return 1
    if argv:
        print(__doc__)
        return 2
    with open(chains_path, "w") as f:
        f.write(text)
    print(f"wrote {len(runbooks)} chains to {chains_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except LintError as e:
        print(f"lint: {e}", file=sys.stderr)
        sys.exit(1)
]]></tool_result>
</message>
<message role="assistant" ordinal="31" timestamp="2026-08-30T14:31:58.755Z" has_tool_use="true">
<tool_call id="toolu_017wepsPbSFZqoL8LMT18fsC" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chains.txt","description":"Read chains.txt"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chains.txt
]]></tool_body>
<tool_result><![CDATA[
[adjudicator] Agent · tools: Read, Bash, model: opus, effort: xhigh
  ├─reads───► review contract
  ├─reads───► deviation contract
  ├─reads───► PR feedback
  ├─reads───► GitHub    the repository name and the pull request's number
  ├─reads───► GitHub    the record you are judging against
  ├─reads───► GitHub    every thread on the pull request
  ├─writes──► GitHub    one reply, then the resolve
  ├─writes──► GitHub    the stub issue first
  ├─writes──► GitHub    the reply `Deferred (<reason>) → #<stub>` and the resolve, in that order
  ├─reads───► GitHub    the current body
  ├─writes──► GitHub    the updated body
  ├─reads───► factory-operations.md's merge-message recipe    § the-merge-message-recipe
  ├─writes──► GitHub    a comment on the pull request
  ├─reports─► outcome: str    the settled envelope
  └ ╌ reports ╌ ► outcome: str    the escalation envelope    if you stopped instead

[bug-pr-review] Agent · tools: Read, Bash, model: sonnet, effort: xhigh
  ├─never writes─► to the code under review
  ├─reads───► review contract
  ├─reads───► GitHub    the repository name and the pull request's number and head sha
  ├─reads───► GitHub    the pull request's existing threads and comments
  ├─reads───► GitHub    the diff in scope
  ├─writes──► GitHub    one review with the findings as threads
  ├─writes──► GitHub    resolutions of your prior cycle's threads whose fixes you have verified
  ├─reports─► outcome: str    `outcome` `"done"`
  └ ╌ reports ╌ ► outcome: str    `outcome` `"escalated"` and the reason in `gist`    if you can't produce the review

[build] Agent · model: opus, effort: xhigh
  ├─reads───► GitHub    the issue
  ├─reads───► PR feedback
  ├─writes──► GitHub    a reply on each thread you fix
  ├─never writes─► GitHub    thread resolutions
  ├ ╌ reads ╌ ► tdd.md    and the testing conventions it opens with, end-to-end    if the issue carries `tests:yes`
  ├─does────► [commit] Skill
  ├─reads───► deviation contract
  ├─reports─► outcome: str    the escalation envelope
  ├─does────► [commit] Skill
  ├ ╌ writes ╌ ► GitHub    the ledger entries in the contract's shape    if any deviation was logged
  └─reports─► outcome: str    the completion envelope

[code-pr-review] Agent · tools: Read, Bash, model: sonnet, effort: xhigh
  ├─reads───► review contract
  ├─reads───► PR feedback
  ├─reads───► GitHub    the repository name and the pull request's number and head sha
  ├─reads───► GitHub    the brief
  ├─reads───► GitHub    the pull request's existing threads and comments
  ├─reads───► GitHub    the diff in scope
  ├─writes──► GitHub    one review with the findings as threads
  ├─writes──► GitHub    resolutions of your prior cycle's threads whose fixes you have verified
  ├─reports─► outcome: str    `outcome` `"done"`
  └ ╌ reports ╌ ► outcome: str    `outcome` `"escalated"` and the reason in `gist`    if you can't produce the review

[doc-pr-review] Agent · tools: Read, Bash, model: sonnet, effort: xhigh
  ├─reads───► review contract
  ├─reads───► PR feedback
  ├─reads───► [conventions] Standard
  ├─reads───► GitHub    the repository name and the pull request's number and head sha
  ├─reads───► GitHub    the brief
  ├─reads───► GitHub    the pull request's existing threads and comments
  ├─reads───► GitHub    the diff in scope
  ├─writes──► GitHub    one review with the findings as threads
  ├─writes──► GitHub    resolutions of your prior cycle's threads whose fixes you have verified
  ├─reports─► outcome: str    `outcome` `"done"`
  └ ╌ reports ╌ ► outcome: str    `outcome` `"escalated"` and the reason in `gist`    if you can't produce the review

[open-pr] Agent · model: sonnet, effort: low
  ├─reads───► GitHub    the PR list for the branch
  ├ ╌ reports ╌ ► outcome: str    that PR    if it lists one
  ├─reads───► factory-operations.md's merge-message recipe    § the-merge-message-recipe
  ├─reads───► GitHub    the issue brief and its comments
  ├─writes──► scratch    the PR body
  ├─writes──► GitHub    the pull request
  ├─reports─► outcome: str    the PR's number and whether you created it or found it already open
  └ ╌ reports ╌ ► outcome: str    the reason instead, as escalated    if the PR cannot be created at all

[set-auditor] Agent · tools: Read, Grep, Glob, model: opus, effort: xhigh
  ├─reads───► [working-documentation-sets] Standard
  ├─never writes─►
  ├─never commits─►
  └─reports─► outcome: str    findings ranked by how much each would mislead a fresh session reading the set cold, as the hand-off to the set-deslopper agent

[set-deslopper] Agent · tools: Read, Write, Edit, Grep, Glob, Agent, model: opus, effort: xhigh
  ├─does────► [set-auditor] Agent
  ├─writes──► local file    the fix for each finding into the set's members
  ├─never commits─►
  └─reports─► outcome: str    a minimal report: one line per member changed, and one line per finding left unfixed with the reason

[tics-remover] Agent · tools: Read, Edit, model: sonnet, effort: high
  ├─reads───► [slop-tics] Standard
  ├─writes──► local file    the target document in place
  ├ ╌ reads ╌ ► [writing-for-agents] Standard    if the target is an agent-facing instruction file
  ├─never commits─►
  ├ ╌ reports ╌ ► outcome: str    exactly `DONE` — nothing else    if you succeeded
  └ ╌ reports ╌ ► outcome: str    free text describing it    if you hit a problem

[agent-view-overwatch] Skill · model: sonnet, effort: xhigh, allowed-tools: Bash(gh issue *) Bash(gh pr *) Bash(gh api *) Bash(git *)
  ├─reads───► software-factory.md
  ├─reads───► factory-operations.md
  ├─reads───► GitHub    the labels for the phase
  └─reads───► GitHub    the issue's PR for the board's PR column

[candidate-promote] Skill · model: inherit, effort: xhigh
  ├─args────► candidate
  ├─reads───► [candidates] Standard    as the contract
  ├─does────► [intake] Skill    with the entry's name and prose as the free-form idea — the children's text too, when promoting a subtree
  ├ ╌ writes ╌ ► local file    the promoted entries out of `CANDIDATES.md`    if intake reports the issue number
  └─reports─► outcome: str    the issue number and which entries were removed

[clean-up-branch-worktree] Skill · model: sonnet, effort: low
  ├ ╌ reports ╌ ► outcome: str    the output    if it prints anything
  ├─reads───► GitHub    the merged PR for the branch, compared with the local `HEAD`
  ├ ╌ reports ╌ ► outcome: str    both outputs    if the SHAs differ, or the PR list is empty
  └─reports─► outcome: str    one line: worktree and branch removed, main at that commit

[commit-off] Skill · model: inherit, effort: low
  └─never commits─►

[commit] Skill · model: sonnet, effort: low, allowed-tools: Bash(git *)
  ├─args────► fast
  ├─args────► amend
  ├ ╌ reports ╌ ► outcome: str    that amend was downgraded to a fresh commit because HEAD was already on `<remote/branch>`    if it lists any remote branches
  └─reports─► outcome: str    tree clean or which files remain uncommitted, and that the push landed

[compact-prep] Skill · model: inherit, effort: xhigh
  ├─args────► important
  ├─does────► [commit] Skill
  └─reports─► outcome: str    what was committed, the one at-risk item from step 2 if there was one, and a plain ready verdict

[datasheet] Skill · model: opus, effort: xhigh
  ├─args────► subject
  ├─args────► scope
  ├─reads───► datasheet.md    end-to-end, before anything else
  ├─reads───► datasheet-example.html    end-to-end, before anything else
  ├ ╌ reports ╌ ► outcome: str    exactly what is needed    if either is missing or ambiguous
  ├ ╌ reports ╌ ► outcome: str    the overlap    if the new manifest overlaps another subject's manifest
  ├─writes──► scratch    a self-ignoring `.datasheet/` directory
  ├ ╌ does ╌ ► [griffe-outline] Script    over each package in scope, appending its outline to the scratch directory    if the scope holds a Python package
  ├─writes──► local file    the sheet to `readings/datasheet/<subject>.html`
  ├─does────► [check_datasheet.py] Script    against the sheet, from this skill's base directory
  ├ ╌ reports ╌ ► outcome: str    why the sheet is nonconformant    if a contract rule cannot be satisfied
  └─reports─► outcome: str    the sheet path, the checker's one-line summary, and the Behavior labels used

[design] Skill · model: inherit, effort: xhigh
  ├─args────► issue
  ├─reads───► [design] Standard
  ├─reads───► [issue-authoring] Standard    end-to-end
  ├─reads───► GitHub    the issue
  ├─does────► [grilling] Skill    to sharpen the approach against the codebase
  ├─does────► [domain-modeling] Skill    active throughout, capturing significant decisions as Decision Records as they crystallize
  ├─writes──► GitHub    the probe-record comment on the issue
  ├ ╌ reads ╌ ► design-it-twice.md    if §2 settled that the public surface is load-bearing
  ├ ╌ does ╌ ► [prototype] Skill    if a question survives the interview and the code can't answer it
  ├─does────► [user-intent-mini-interview] Skill
  ├─writes──► GitHub    the complete brief
  ├─reads───► decompose.md
  ├─does────► [issue-review-claims] Skill
  ├─does────► [issue-review-simulation] Skill
  ├ ╌ writes ╌ ► GitHub    the phase move    if the user approves, and only then
  ├ ╌ writes ╌ ► GitHub    the pointer /prototype asks for    if §5 opened a tree
  └─reports─► outcome: str    the phase result and next state

[diagnosing-bugs] Skill · model: inherit, effort: xhigh
  ├─reads───► `CONTEXT.md`    for a clear mental model of the relevant modules
  ├─reads───► `docs/decisions/`    for the Decision Records in the area you're touching
  ├ ╌ reports ╌ ► outcome: str    that redaction hid what's needed to diagnose it    if the redacted output is not enough to diagnose the bug
  ├ ╌ writes ╌ ► local file    a copy of the HITL script, edited with this bug's steps    if the user must click
  ├ ╌ does ╌ ► [hitl-loop.template.sh] Script    the edited copy    if the user must click
  ├ ╌ reports ╌ ► outcome: str    what you tried, and that no loop could be built    if you genuinely cannot build a loop
  ├ ╌ writes ╌ ► local file    a debug log at each boundary that distinguishes hypotheses    if a debugger or REPL isn't available
  ├ ╌ writes ╌ ► local file    the minimised repro as a failing test at that seam    if a correct seam exists
  └ ╌ does ╌ ► [improve-codebase-architecture] Skill    with the specifics    if the answer involves architectural change (no good test seam, tangled callers, hidden coupling)

[document-remove-tics] Skill · model: sonnet, effort: high
  ├─args────► doc-hint
  ├─does────► [tics-remover] Agent    the subagent, `model: sonnet`
  └─never commits─►

[domain-modeling] Skill · model: inherit, effort: xhigh
  ├─reads───► `CONTEXT.md`    for the existing language
  ├ ╌ reads ╌ ► [context-content] Standard    if a term is resolved
  ├ ╌ writes ╌ ► local file    CONTEXT.md in place with the resolved entry    if a term is resolved
  ├ ╌ reads ╌ ► [records] Standard    if a decision looks hard to reverse or would surprise a future reader
  └ ╌ writes ╌ ► local file    the new record under `docs/decisions/`    if every criterion holds

[enable-repo-governance] Skill · model: opus, effort: xhigh
  ├─reads───► [bootstrap] Standard
  ├ ╌ reports ╌ ► outcome: str    that the tree is not clean    if its working tree is not clean and on `main`
  ├ ╌ reports ╌ ► outcome: str    that it is already governed    if the repo is already in workspace-lint's `GOVERNED` roster
  ├─does────► [repo-lint] Script
  ├─reads───► [index] Standard
  ├─does────► [bootstrap-labels] Script
  ├─reads───► [repo-settings] Standard
  ├─writes──► local file    the target's name into the `GOVERNED` roster
  ├─does────► [workspace-lint] Script
  ├─writes──► git(~/workspace/dev-playbook: add, commit)    that dev-playbook edit separately, one line
  └─reports─► outcome: str    per-repo results

[grilling] Skill · model: inherit, effort: xhigh
  └─reports─► outcome: str    the whole frontier in one round: number each question and give your recommended answer

[handoff] Skill · model: opus, effort: medium
  ├─args────► focus
  ├─writes──► scratch    the handoff document
  ├─reports─► outcome: str    the absolute path of the handoff document
  └─reports─► outcome: str    a ready-to-paste resume line for the user to carry into the new session

[idea] Skill · model: sonnet, effort: xhigh
  ├─args────► material
  └─does────► [idea] Skill    verbatim

[improve-codebase-architecture] Skill · model: inherit, effort: xhigh
  ├─reads───► [design] Standard    for the architecture vocabulary and its principles, loaded first
  ├─reads───► `CONTEXT.md`    for the project's domain glossary
  ├─reads───► `docs/decisions/`    for the Decision Records in the area you're touching
  ├─reads───► html-report.md    for the full HTML scaffold, diagram patterns, and styling guidance
  ├─writes──► scratch    a self-contained HTML file
  ├─reports─► outcome: str    the finished report's absolute path, already opened for the user
  ├ ╌ does ╌ ► [grilling] Skill    to walk the decision tree with them    if the user picks a candidate
  ├ ╌ does ╌ ► [domain-modeling] Skill    to keep the domain model current as you go    if a new term surfaces that `CONTEXT.md` doesn't yet name, or a rejection deserves a Decision Record
  └ ╌ reads ╌ ► design-it-twice.md    if the user wants to explore alternative interfaces for the deepened module

[intake] Skill · model: inherit, effort: xhigh
  ├─reads───► software factory standard
  ├─reads───► [issue-authoring] Standard
  ├─reads───► GitHub    the issue's title, body, and comments as the raw idea
  ├─does────► [grilling] Skill    once to sharpen the raw idea
  ├─does────► [domain-modeling] Skill    active throughout
  ├─reads───► [factory-labels] Standard
  ├─does────► [user-intent-mini-interview] Skill    for that one
  ├─writes──► GitHub    the new issue at that phase
  ├─writes──► GitHub    the four-tuple and the overwritten body on the existing issue
  ├─writes──► GitHub    the probe-record comment §2 accumulated
  ├─does────► [issue-review-claims] Skill    `<issue>`
  ├─does────► [issue-review-simulation] Skill    `<issue>`
  ├ ╌ writes ╌ ► GitHub    the phase move    if the user approves, and only then
  └─reports─► outcome: str    the standard form: `<repo>#<issue> · phase: intake · <one-line summary> · routed to <phase> · brief in issue`

[issue-overwatch] Skill · model: inherit, effort: xhigh
  ├─args────► issue-number
  ├─never merges─►
  ├─reads───► software-factory.md
  ├─reads───► factory-operations.md
  ├─reads───► user-checkpoints.md
  ├─reads───► GitHub    the issue
  ├─reads───► GitHub    the open blockers
  ├─writes──► GitHub    the phase-label move along the edge the graph names
  ├─reads───► [issue-authoring] Standard    § readiness
  ├─reads───► GitHub    main's head sha
  ├─reads───► GitHub    every comment surface on the PR
  ├─writes──► scratch    every body you post here
  ├─writes──► GitHub    its tracker stub
  ├─writes──► GitHub    the ruling as one PR comment naming the stubs
  ├─writes──► GitHub    the merge message, regenerated from the whole PR record
  ├─writes──► GitHub    the user's deciding reason where the findings live
  ├─writes──► GitHub    the label move back along the rework edge
  └─reports─► outcome: str    the issue's state at the close of each turn

[issue-review-claims] Skill · model: sonnet, effort: xhigh, disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
  ├─args────► issue
  ├─never writes─►
  ├─never writes─► GitHub
  ├─reads───► GitHub    the issue under audit
  ├─reads───► GitHub    its parent epic, if it has one
  ├─reads───► [issue-authoring] Standard    for claim provenance
  ├─reads───► deviation contract
  └─reports─► outcome: str    raw: a numbered list of findings — each states the claim or quote at issue, what reality shows, and why it meets the wrong-or-halt bar — then one line per sweep performed that came back clean

[issue-review-simulation] Skill · model: sonnet, effort: xhigh, disallowed-tools: Edit MultiEdit NotebookEdit Write(/**)
  ├─args────► issue
  ├─never writes─►
  ├─never writes─► GitHub
  ├─reads───► GitHub    the issue
  ├─reads───► GitHub    its parent epic, if it has one
  ├─reads───► deviation contract
  └─reports─► outcome: str    findings grouped Q3–Q7

[judgments-sweep] Skill · model: opus, effort: xhigh
  ├─args────► roots
  ├─reads───► [declarations] Standard
  ├─does────► [judgments-run] Script    in `plan` mode
  ├─writes──► local file    the judgment cache
  ├─does────► [judgments-run] Script    again, with a `--skip` per set-aside id
  └─reports─► outcome: str    per root: already cached, judged, passed, fixed-then-passed (each id + the edit made), set aside (each id + its `opinion` or crash history + why), crashed-and-recovered

[log-friction] Skill · model: sonnet, effort: xhigh
  ├─args────► friction
  ├ ╌ reports ╌ ► outcome: str    that there is nothing to record    if there is genuinely nothing to record
  ├─reads───► friction/log.md
  ├ ╌ writes ╌ ► git(~/workspace/mission-control: add, commit, push)    and push    if there is something to record
  └─reports─► outcome: str    one line with the entry's short name, and that the push landed

[orchestrate] Skill · model: inherit, effort: xhigh
  ├─reports─► outcome: str    a single line confirming Fable orchestration mode is on
  └ ╌ reports ╌ ► outcome: str    that immediately    if you are not Fable

[prototype] Skill · model: inherit, effort: xhigh
  ├ ╌ reads ╌ ► logic.md    if the question is whether this logic / state model feels right
  ├ ╌ reads ╌ ► ui.md    if the question is what this should look like
  ├ ╌ writes ╌ ► scratch    a throwaway DB or file, with a clear "PROTOTYPE — wipe me" name    if the question explicitly involves a database
  ├─writes──► GitHub    a context pointer to that branch, on the implementation issue
  └─writes──► GitHub    the verdict and the question it settled, in the issue or a commit

[ralph-setup] Skill · model: inherit, effort: xhigh
  ├─args────► goal
  ├─reads───► ralph-loop.md    end-to-end, before anything else
  ├─does────► [grilling] Skill
  ├─does────► [domain-modeling] Skill    active throughout
  ├ ╌ writes ╌ ► local file    the plan file    if the user approved the criteria and the plan, and the gate is green
  ├ ╌ writes ╌ ► local file    the progress file    if the user approved the criteria and the plan, and the gate is green
  └─reports─► outcome: str    the full launch command for the user to run

[research] Skill · model: inherit, effort: xhigh
  └─writes──► local file    the findings to a single Markdown file, where the repo already keeps such notes, or somewhere sensible if there is no established convention

[rewind-compact] Skill · model: opus, effort: medium
  ├─args────► target
  ├─does────► [commit] Skill
  ├─reports─► outcome: str    the Tangential compaction summary
  └─reports─► outcome: str    the verbatim text of the rewind target

[runbook-creator] Skill · model: opus, effort: xhigh
  ├─args────► idea
  ├─reads───► [runbook-conventions] Standard    end-to-end
  ├─reads───► [writing-for-agents] Standard    end-to-end
  ├─writes──► local file    the new runbook
  └─does────► [playbook-lint] Script

[update-standards-pin] Skill · model: opus, effort: xhigh
  ├─reads───► [distribution] Standard
  ├─reads───► GitHub    main's head sha
  ├ ╌ reports ╌ ► outcome: str    that the release is unpushed    if the two values are unequal
  ├─reads───► [workspace_lint.py] Script    for the `GOVERNED` roster
  ├─does────► [bump-pins] Script    `--dry-run` first to see what would move, then run it again for real
  ├ ╌ reports ╌ ► outcome: str    the abort as the fault it is    if the script raises `the gate could not run`
  ├ ╌ writes ╌ ► local file    the retired requirement's adaptation and deletions out of the consumer repo    if the bump already reports green
  └─reports─► outcome: str    per-repo results — bumped, needs work, skipped, or faulted

[usage-report] Skill · model: sonnet, effort: low, allowed-tools: Bash(bash *usage-report/scripts/report.sh)
  └─does────► [report.sh] Script    from this skill's base directory

[user-intent-mini-interview] Skill · model: inherit, effort: xhigh
  ├─args────► issue
  ├─reads───► [issue-authoring] Standard    § the-build-leaf-brief-modedirect
  ├ ╌ reads ╌ ► GitHub    the body of the issue `issue` names, and treat that as the draft    if run with no draft in context
  ├─reports─► outcome: str    the cleaned `User intent` paragraph for the calling beat to write into the brief
  └─never writes─► GitHub

[wait-what] Skill · model: sonnet, effort: xhigh
  ├─reads───► `CONTEXT.md`    for its ubiquitous language
  └─reports─► outcome: str    the last message re-pitched

[wayfinder-to-build] Skill · model: inherit, effort: xhigh
  ├─args────► map
  ├─reads───► [issue-authoring] Standard    end-to-end
  ├─reads───► software factory    end-to-end
  ├─reads───► [design] Standard
  ├─reads───► [tracker-operations] Standard    § wayfinding-operations
  ├ ╌ reports ╌ ► outcome: str    exactly what is open    if anything is still open — a ticket, a fog patch
  ├─reads───► GitHub    the map body first
  ├─reads───► GitHub    every child ticket in full
  ├─does────► [grilling] Skill    and work these branches as its design tree
  ├─reads───► [issue-authoring] Standard    § vertical-slice-rules
  ├─reads───► the decompose exit
  ├─reads───► [issue-authoring] Standard    § the-epic-body
  ├─writes──► GitHub    the epic with the body defined there
  ├─writes──► GitHub    one issue per slice, in dependency order
  ├─reads───► [tracker-operations] Standard    for the commands that wire the native relationships
  ├─writes──► GitHub    the wiring
  └─reports─► outcome: str    the whole hand-off on screen

[wayfinder] Skill · model: inherit, effort: xhigh
  ├─args────► map-hint
  ├─reads───► [tracker-operations] Standard    for the Wayfinding operations section, which states how _this_ repo expresses them
  ├─does────► [prototype] Skill
  ├─does────► [grilling] Skill
  ├─does────► [domain-modeling] Skill
  ├ ╌ reports ╌ ► outcome: str    that no map is needed    if this surfaces no fog — the way to the destination is already clear, the whole journey small enough for one session
  ├─writes──► GitHub    the map issue
  ├─writes──► GitHub    the tickets you can specify now, as child issues of the map
  ├─does────► [research] Skill    to resolve it in parallel
  ├─reads───► GitHub    the map
  ├─writes──► GitHub    the claim
  ├─reads───► GitHub    the full body of any related or closed ticket, on demand
  ├─writes──► GitHub    the resolution
  └─writes──► GitHub    newly-surfaced tickets, create-then-wire

[working-doc-set-deslop] Skill · model: sonnet, effort: high
  ├─args────► set-hint
  ├─does────► [set-deslopper] Agent    the subagent, `model: opus`
  └─never commits─►

[working-doc-set-diagram] Skill · model: opus, effort: medium
  └─reports─► outcome: str    the diagram
]]></tool_result>
</message>
<message role="assistant" ordinal="33" timestamp="2026-08-30T14:32:27.818Z" has_tool_use="true">
<tool_call id="toolu_01TeP82DqXQGTLQjs28KhYVx" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"grep -ci 'primitive\\|ontolog' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chains.txt","description":"Count primitive/ontology occurrences per file"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ grep -ci 'primitive\|ontolog' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chains.txt
]]></tool_body>
<tool_result><![CDATA[
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md:19
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/index.md:0
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md:24
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/NO-MORE-SLOP.md:15
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md:2
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chains.txt:0
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py:2
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md:10
]]></tool_result>
</message>
<message role="assistant" ordinal="35" timestamp="2026-08-30T14:32:38.018Z">
Should have read, per objective:

**Recursion to the bedrock of determinism**
- `CLOA-ABSTRACTIONS.md` — the note develops inside § An EM loop / § Layer invariance.
- `REFERENCE-CHAIN-ENCODING.md` — the lower rung: grammar, certified transform, `--check`.
- `parser/chaingen.py` — the parser half of the grammar ↔ parser map; but only its docstring matters, not the 600-line body.

**Terminology sweep** — every file that uses the words, which the grep pins exactly:
- `CLOA-ABSTRACTIONS.md` (19 hits), `NO-MORE-SLOP.md` (15), `REFERENCE-CHAIN-ENCODING.md` (10), `RESIDUAL-LEDGER.md` (24 — but all one uniform sense, &#34;no primitive for X&#34;; a grep of the hit lines would have sufficed over a full read), `REFERENCE-CHAIN-DECLARATION.md` (2 — hit lines only), `chaingen.py` (2 — hit lines only).

**Need not have read at all**
- `index.md` — zero hits, no bearing on either item.
- `parser/chains.txt` — generated output, pinned by `--check`; reading it bought nothing. This was the expensive mistake: it&#39;s by far the largest file.

Net: full reads justified for three files (NO-MORE-SLOP.md, CLOA-ABSTRACTIONS.md, REFERENCE-CHAIN-ENCODING.md); targeted reads (docstring or grep hit-lines) for three (DECLARATION, LEDGER, chaingen.py); zero for two (index.md, chains.txt).
</message>
<message role="user" ordinal="36" timestamp="2026-08-30T14:33:32.161Z">
We&#39;re going to work on this part now:

## Documentation track — active

**Planned**

The ontology is settled in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md);
the encoding design and its parser sit in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
beneath
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
Two items remain:

- **Recursion to the bedrock of determinism.** Develop the note: the
  [EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#an-em-loop-for-primitive-construction)
  applies all the way down until the target stops being stochastic; maps
  recurse one rung further — grammar ↔ parser, the certified transform,
  pinned by `--check`.
- **Primitive and ontology terminology sweep.** &#34;Primitive&#34; and
  &#34;ontology&#34; are used loosely across these files; tighten every use.

In a fork, you said read these files: &#34;full reads justified for three files (NO-MORE-SLOP.md, CLOA-ABSTRACTIONS.md, REFERENCE-CHAIN-ENCODING.md); targeted
  reads (docstring or grep hit-lines) for three (DECLARATION, LEDGER, chaingen.py); zero for two (index.md, chains.txt).
&#34;

So, read those. Then let&#39;s talk. This will begin with me driving the conversation. You should just give short answers.
</message>
<message role="assistant" ordinal="37" timestamp="2026-08-30T14:33:35.386Z" has_tool_use="true">
<tool_call id="toolu_01DwrhgmVU3H98yvbr44vFco" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md","description":"Read CLOA-ABSTRACTIONS.md in full"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: CLOA Abstractions
description: The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
---

# CLOA Abstractions

The **CLOA primitives ontology**: the abstractions the user and the AI
share at the CLOA — each a noun with a small fixed verb set — and, as a
detail of method, the loop that generates them. An offshoot of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md). The
same speculative voice applies: a guess is written as a guess, and a
sentence is settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
entire repository — without having to read all of it.

## Documentation is code

Documentation is code: it does things because agents do things, and an agent
is just documentation, a harness, and permissions.

Unfortunately, documentation is also stochastic and extremely high-dimensional.
Parsimonious structure added on top constructs
high-level abstractions capturing the important parts the user cares about.
Keep the structure simple, lintable, deterministic, and high leverage.

Treat documentation as a special case
of code; pre-existing methods for code may work for documentation also,
with minimal modifications. When facing a difficult problem in documentation,
translate to the code form, solve it there, and port the analogy back. For
example, each document should probably have a typed signature.

Documentation abstractions change the
way codebases do — refactors are possible but costly.

## Three readers

Every structure decision must serve the readers below, in priority order:

1. **The executing agent** — the primary customer. Runbook prose commands
   the agent in natural imperative English; nothing may clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parsers that generate views and the lints
   that enforce grammars. Served by subtle helpers, never by machine
   notation embedded in prose.

## A noun with one or more verbs

One noun carrying a small fixed verb set. Nouns describe;
verbs act. Naming nouns and giving them verbs is deterministic
structure at the level of ideas.

Every abstraction carries a **provenance**: declared or imported. A
declared abstraction is invented here and declared in this corpus —
Standard, the Reference chain. An imported abstraction is someone
else's, taken as a dependency — GitHub, git, `str` — its contract as
given.

Implemented exemplars so far:

**Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from those verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts.

**Runbook Reference chain**: the noun is the
chain, the verbs are its edge labels, and its node types ride along as
one-verb nouns — both rosters declared in
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
It allows the user to understand a runbook's behavior without opening
the body.

## An EM loop for primitive construction

In code, the programming language comes first and the functionality second.
Thus, functionality may be expressed as code, constrained by the primitives
that were defined by the language in advance.

Expressing existing documentation as code hits a problem: documentation
has free-form, infinite possibilities. No constrained programming language
exists a priori: the language is English itself.

The solution is a backwards operation combining AI proposals with user
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
- **Convergence** is
  [the pandas standard](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#the-pandas-standard):
  the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal — good abstractions are a codebook the corpus gets short in,
  so functionality per character runs high.

Track residuals in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).
The loop's job is awareness of what
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
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
where the target is skill prose and the output is a grammar. Two adjacent
runs connect through a map between the lower level's generated primitives
and the higher level's existing ones, written to a stateful location.
One-to-one is the ideal — each higher
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
                                               │ the primitive map:
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
| Skill | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
| Agent definition | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
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

## Acronyms

None.
]]></tool_result>
</message>
<message role="assistant" ordinal="39" timestamp="2026-08-30T14:33:35.974Z" has_tool_use="true">
<tool_call id="toolu_01AM99jXJYGLDa5ws3GL2BKS" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md","description":"Read REFERENCE-CHAIN-ENCODING.md in full"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Encoding
description: The layer below the declaration — the spec a writer follows to encode chain edges in runbook prose
---

# Reference Chain Encoding

The layer below
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
how chain edges are written inside runbook prose, so deterministic
code can generate every chain. This file is the spec for the writer of
that prose. The primitive map below is the join between the two
layers — one lower expression per higher primitive. The parser is
`parser/chaingen.py`, which writes every chain to `parser/chains.txt`
and fails on drift via `--check`; everything the writer does not
need — how an edge draws, how a name resolves — lives in that code and
nowhere else. Same working-file conventions as the branch plan sets
out.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What binds 100% is
the small grammar below, to be specified as a standard card and enforced
by a lint.

## From prose to chain

A chain edge must come out of the same sentence that commands the
executing agent — no writer maintains two copies. The **span** is how
one sentence serves both readers: braces mark the one machine-readable
unit inside otherwise plain prose. The parser slices a span at fixed
cut points — the keyword, the links, the splitters — and every word
between cuts is an opaque string it carries but never reads, so the
payload stays natural language for the agent. The two mix freely in
one sentence, and the boundary cuts both ways: unmarked prose is never
an edge — unbraced `if` is the deliberate way to keep a condition out
of the chain — and prose never restates a span; a sentence that
shadows a primitive becomes the span or is reworded away.

Two live uses. In each, the span is the prose as it stands in the
runbook file, and the edge below it is what the deterministic parser
generates from that span. A simple read, from intake:

```
{Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md);
the brief formats, brief principles, and the readiness bar}

  ├─reads───► [issue-authoring] Standard
```

A condition nesting a read, from design:

```
{If §2 settled that the public surface is load-bearing,
{Read [design-it-twice.md](references/design-it-twice.md)} and work through it}

  ├ ╌ reads ╌ ► design-it-twice.md    if §2 settled that the public surface is load-bearing
```

The rest of this file builds that trip up piece by piece: which
primitives come from where, and the rules for writing each span.

## The primitive map

Every higher primitive is either **derived** from the runbook's file or
**declared** in its body as a span.

The derived primitives:

| Primitive | Source | Detail |
| --------- | ------ | ------ |
| node type | the file path | `agents/` is an Agent, `SKILL.md` a Skill, `scripts/` or a script extension a Script |
| node data | frontmatter, verbatim | — |
| runbook summary | frontmatter `description` | — |
| args | frontmatter `arguments` list | names only — the name carries the meaning; no placeholder in the body |

The declared primitives:

| Primitive | Span |
| --------- | ---- |
| reads | `{Read <one link>}` |
| reads — GitHub | `{Read from GitHub …}` |
| writes — local file | `{Write …}` |
| writes — GitHub | `{Write to GitHub …}` |
| writes — scratch | `{Write to scratch …}` |
| writes — git | `{Commit …}` + fenced command |
| does — Agent | `{Launch <one link>}` |
| does — Skill or Script | `{Run <one link>}` |
| overrides … with … | `{Override <link> … with <link> …}` |
| reports | `{Report …}` |
| condition | `{If <condition>, {…}}` |
| prohibition | `{Never {…}}` |

Keywords are imperative — commands to the executing agent; the chain's
edge labels are their third-person translation.

## Writing the spans

A span is `{keyword payload}`: flat by default, nested at most two
deep — `If` and `Never` spend the cap. The keyword matches
case-insensitively, a span may wrap across source lines, and spans
count only outside code spans and fenced blocks. The rules for each
declared form, refining the table above:

**Targets.** Where the table says `<one link>`, exactly one markdown
link in the payload names the target; every other word is annotation —
instruction to the executing agent, never read by the parser. One
target per span: two reads are two spans. A does-link points at the
live harness path (`~/.claude/skills/…`, `~/.claude/agents/…`). A
`#fragment` on any link must match a heading in the target file. A
linkless `{Read}` may instead carry one inline-code target
(`` {Read `CONTEXT.md` …} ``), taken verbatim.

```
{Run [/grilling](~/.claude/skills/grilling/SKILL.md) once to sharpen the raw idea}
```

The link is the target; "once to sharpen the raw idea" is annotation.

**Buckets.** The keyword picks the write bucket — `Commit` is git,
`Write` is local file — unless the payload opens with `to GitHub` or
`to scratch`; `from GitHub` does the same for `Read`. A `{Commit …}`
span requires a fenced git command block in the same step, and span
and block must agree.

```
{Write to scratch a self-ignoring `.datasheet/` directory}
```

The `to scratch` prefix picks the bucket; bare `{Write …}` would be
the local-file bucket.

**Splitters.** In `{If <condition>, {…}}`, the text before the first
nested span is the condition, lifted verbatim; every nested span fires
under it. In `{Override … with …}`, the word `with` splits the
payload — one link on each side, the overridden clause before, the
replacement after. In every payload, the first `;` ends what travels
to the chain: front the kernel, elaborate after the semicolon.

```
{Write the target document in place; it must say the same things
without committing any of the named tics}
```

"the target document in place" travels to the chain; everything after
the semicolon stays in the file.

**Prohibition.** `{Never {…}}` wraps exactly one span — inner keyword
`Write`, `Commit`, or `Merge` — and flips it from action to ban. A ban
the vocabulary cannot carry stays plain prose, recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

```
{Never {Commit}} — leave the changes in the working tree for review.
```

The span is the braces alone; the prose after the dash stays outside
it.

**Reports.** `{Report …}` reports the constant `outcome: str` — a
runbook's report is prose — with the payload as annotation.

```
{Report one line: worktree and branch removed, main at that commit}
```

The edge is `outcome: str`; the whole payload rides as annotation.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
]]></tool_result>
</message>
<message role="assistant" ordinal="41" timestamp="2026-08-30T14:33:42.324Z" has_tool_use="true">
<tool_call id="toolu_01GH2awXR5csj3u6h9tmB5Rw" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,84' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md","description":"Read REFERENCE-CHAIN-DECLARATION.md body"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,84' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md
]]></tool_body>
<tool_result><![CDATA[
Exit code 1
sed: -e expression #1, char 4: missing command
]]></tool_result>
<tool_call id="toolu_01X44h7qHjKFmEZmGQQRGD8b" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,30' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md; echo '---- docstring ----'; sed -n '1,40' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py","description":"Read ledger head and chaingen docstring"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,30' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md; echo '---- docstring ----'; sed -n '1,40' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py
]]></tool_body>
<tool_result><![CDATA[
Exit code 1
sed: -e expression #1, char 4: missing command
---- docstring ----
sed: -e expression #1, char 4: missing command
]]></tool_result>
</message>
<message role="assistant" ordinal="44" timestamp="2026-08-30T14:33:47.237Z" has_tool_use="true">
<tool_call id="toolu_018rwcRKARf67zTMiWps9g5h" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,84p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md","description":"Read REFERENCE-CHAIN-DECLARATION.md body"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,84p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Declaration
description: The Reference chain declared — a runbook's behavior and call signature as nodes and edges
---

# Reference Chain Declaration

The **Reference chain** is one CLOA abstraction: the construction
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
rules for the runbook family. This file declares the object itself — its
nodes and its edges. The mechanics that construct a
chain from runbook prose — the primitive map and the rules for
writing spans — sit one layer down in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md). Same
working-file conventions as the branch plan sets out.

## The chain

A Reference chain is abstractions and the actions that connect them:
**nodes** joined by labeled **edges**, rooted at one runbook.

The chain's origin: a runbook is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
contract. The Reference chain is that contract written down: the
signature (args in, reports out) plus the effects, in the coarse order
they fire. Not full fidelity — the chain is a collapse of the runbook's
program, and the fine-grained sequencing it drops stays below the CLOA.

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub, a
file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | reads                  | —           | Its own noun and verbs, in [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs) |
| Agent    | does                   | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | does                   | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | does                   | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under its
node.

## Edges

An edge is an action. The six labels:

| Label | The action | Detail |
| ----- | ---------- | ------ |
| does | run a runbook or a script | — |
| reads | consult | — |
| overrides … with … | substitute a previous clause | — |
| writes | change state | target is one of four buckets — `git(commit, push)` |
| args | take the caller's input | by name — `friction` |
| reports | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type.

How each edge is written in runbook prose is ruled in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#the-primitive-map),
and how it draws in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md).

Any edge may carry a **condition** — what must hold for it to fire. A
conditional edge draws dashed; an unconditional edge draws solid. The
condition never changes the edge's type.

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Acronyms
]]></tool_result>
</message>
<message role="assistant" ordinal="46" timestamp="2026-08-30T14:33:48.473Z" has_tool_use="true">
<tool_call id="toolu_01LwsLvUk8qdneHnRHdQoP2r" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,30p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md; echo '---- docstring ----'; sed -n '1,40p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py","description":"Read ledger head and chaingen docstring"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,30p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md; echo '---- docstring ----'; sed -n '1,40p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Residual Ledger
description: The system-wide record of what the current abstractions cannot express — one section per registry type ruled important
---

# Residual Ledger

The system-wide record of residuals: what the current abstractions
cannot express. One section per registry type ruled important in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)'s
registry dispositions — only Runbooks today. That is all an entry is —
a record.

## Runbooks

Per runbook ported to the
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
what the full rewrite could not express, recognized and written down at
the moment of porting. Entries name spans and keywords in the vocabulary
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
declares.

An entry is a couple of sentences, hard limit: name each specific
action the file could not express and why the map cannot say it —
nothing else. No inventories of what fit, no family taxonomies, no
cross-references to other entries, no history, no restating the map's
rules.

### Accepted classes
---- docstring ----
#!/usr/bin/env python3
"""chaingen — reconstruct a runbook's Reference chain from its encoded file.

Prototype implementing REFERENCE-CHAIN-ENCODING.md's certified transform: slice, never
interpret. Cut points are the keyword, the markdown
link(s), the `with` splitter, nested braces, and the first semicolon.
Everything between cut points is opaque verbatim text. A `#fragment` on a
read/launch/run link target splits off as a `§ fragment` annotation on the
edge, after failing loud unless it matches a heading slug in the target.
A `{Never {…}}` span wraps one primitive span and renders a prohibition
edge — `never <verb>`, the wrapped payload's kernel as target, possibly
empty. A bucket prefix opens a linkless payload and names the target
node: `{Write to GitHub …}` / `{Write to scratch …}` pick the write
bucket, `{Read from GitHub …}` the GitHub read.

Usage:
    chaingen.py            regenerate chains.txt — every runbook in the
                           corpus (dotfiles/dot-claude agents and
                           skills), blank-line separated
    chaingen.py --check    regenerate in memory and diff against
                           chains.txt; exit 1 on drift
"""

import difflib
import glob
import os
import re
import sys

LEXICON = {
    "read": "reads",
    "commit": "writes",
    "write": "writes",
    "report": "reports",
    "launch": "does",
    "run": "does",
    "override": "overrides",
    "if": "condition",
    "never": "never",
}
]]></tool_result>
</message>
<message role="assistant" ordinal="48" timestamp="2026-08-30T14:33:51.231Z">
Read. Full: NO-MORE-SLOP, CLOA-ABSTRACTIONS, ENCODING. Targeted: DECLARATION (whole body — it&#39;s short), LEDGER intro, chaingen.py docstring + lexicon. Ready — you drive.
</message>
<message role="user" ordinal="49" timestamp="2026-08-30T14:37:02.459Z">
We&#39;re going to work on this part now:

## Documentation track — active

**Planned**

The ontology is settled in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md);
the encoding design and its parser sit in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
beneath
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
Two items remain:

- **Recursion to the bedrock of determinism.** Develop the note: the
  [EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#an-em-loop-for-primitive-construction)
  applies all the way down until the target stops being stochastic; maps
  recurse one rung further — grammar ↔ parser, the certified transform,
  pinned by `--check`. But does it stop, truly? We just shift to software engineering tools. The abstractions continue, but the &#34;invent our own&#34; with EM Loop changes to &#34;decide which pre-existing tools to use.&#34;
- **Primitive and ontology terminology sweep.** &#34;Primitive&#34; and
  &#34;ontology&#34; are used loosely across these files; tighten every use.

In a fork, you said read these files: &#34;full reads justified for three files (NO-MORE-SLOP.md, CLOA-ABSTRACTIONS.md, REFERENCE-CHAIN-ENCODING.md); targeted
  reads (docstring or grep hit-lines) for three (DECLARATION, LEDGER, chaingen.py); zero for two (index.md, chains.txt).
&#34;

So, read those. Then let&#39;s talk. This will begin with me driving the conversation. You should just give short answers. Also make sure you&#39;re in the branch and worktree. Claude Code restarted you may have exited the worktree accidentally
</message>
<message role="assistant" ordinal="50" timestamp="2026-08-30T14:37:04.877Z" has_tool_use="true">
<tool_call id="toolu_013LSyrHrtbuCkBow5TPAWiG" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"pwd && git rev-parse --show-toplevel && git branch --show-current","description":"Check worktree and branch"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ pwd && git rev-parse --show-toplevel && git branch --show-current
]]></tool_body>
<tool_result><![CDATA[
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2
/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2
no-more-slop-2
]]></tool_result>
</message>
<message role="assistant" ordinal="52" timestamp="2026-08-30T14:37:07.869Z" has_tool_use="true">
<tool_call id="toolu_01FE7BzdAzbcEtJ16HHanvm5" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md","description":"Read CLOA-ABSTRACTIONS.md in full"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: CLOA Abstractions
description: The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
---

# CLOA Abstractions

The **CLOA primitives ontology**: the abstractions the user and the AI
share at the CLOA — each a noun with a small fixed verb set — and, as a
detail of method, the loop that generates them. An offshoot of
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md). The
same speculative voice applies: a guess is written as a guess, and a
sentence is settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
entire repository — without having to read all of it.

## Documentation is code

Documentation is code: it does things because agents do things, and an agent
is just documentation, a harness, and permissions.

Unfortunately, documentation is also stochastic and extremely high-dimensional.
Parsimonious structure added on top constructs
high-level abstractions capturing the important parts the user cares about.
Keep the structure simple, lintable, deterministic, and high leverage.

Treat documentation as a special case
of code; pre-existing methods for code may work for documentation also,
with minimal modifications. When facing a difficult problem in documentation,
translate to the code form, solve it there, and port the analogy back. For
example, each document should probably have a typed signature.

Documentation abstractions change the
way codebases do — refactors are possible but costly.

## Three readers

Every structure decision must serve the readers below, in priority order:

1. **The executing agent** — the primary customer. Runbook prose commands
   the agent in natural imperative English; nothing may clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parsers that generate views and the lints
   that enforce grammars. Served by subtle helpers, never by machine
   notation embedded in prose.

## A noun with one or more verbs

One noun carrying a small fixed verb set. Nouns describe;
verbs act. Naming nouns and giving them verbs is deterministic
structure at the level of ideas.

Every abstraction carries a **provenance**: declared or imported. A
declared abstraction is invented here and declared in this corpus —
Standard, the Reference chain. An imported abstraction is someone
else's, taken as a dependency — GitHub, git, `str` — its contract as
given.

Implemented exemplars so far:

**Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from those verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts.

**Runbook Reference chain**: the noun is the
chain, the verbs are its edge labels, and its node types ride along as
one-verb nouns — both rosters declared in
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md).
It allows the user to understand a runbook's behavior without opening
the body.

## An EM loop for primitive construction

In code, the programming language comes first and the functionality second.
Thus, functionality may be expressed as code, constrained by the primitives
that were defined by the language in advance.

Expressing existing documentation as code hits a problem: documentation
has free-form, infinite possibilities. No constrained programming language
exists a priori: the language is English itself.

The solution is a backwards operation combining AI proposals with user
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
- **Convergence** is
  [the pandas standard](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#the-pandas-standard):
  the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal — good abstractions are a codebook the corpus gets short in,
  so functionality per character runs high.

Track residuals in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).
The loop's job is awareness of what
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
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md),
where the target is skill prose and the output is a grammar. Two adjacent
runs connect through a map between the lower level's generated primitives
and the higher level's existing ones, written to a stateful location.
One-to-one is the ideal — each higher
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
                                               │ the primitive map:
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
| Skill | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
| Agent definition | **Yes** | A runbook — the [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md) construction |
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

## Acronyms

None.
]]></tool_result>
</message>
<message role="assistant" ordinal="54" timestamp="2026-08-30T14:37:08.35Z" has_tool_use="true">
<tool_call id="toolu_01QeNBGq9pigpwWoXqCPqWCi" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md","description":"Read REFERENCE-CHAIN-ENCODING.md in full"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ cat /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Encoding
description: The layer below the declaration — the spec a writer follows to encode chain edges in runbook prose
---

# Reference Chain Encoding

The layer below
[Reference Chain Declaration](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
how chain edges are written inside runbook prose, so deterministic
code can generate every chain. This file is the spec for the writer of
that prose. The primitive map below is the join between the two
layers — one lower expression per higher primitive. The parser is
`parser/chaingen.py`, which writes every chain to `parser/chains.txt`
and fails on drift via `--check`; everything the writer does not
need — how an edge draws, how a name resolves — lives in that code and
nowhere else. Same working-file conventions as the branch plan sets
out.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What binds 100% is
the small grammar below, to be specified as a standard card and enforced
by a lint.

## From prose to chain

A chain edge must come out of the same sentence that commands the
executing agent — no writer maintains two copies. The **span** is how
one sentence serves both readers: braces mark the one machine-readable
unit inside otherwise plain prose. The parser slices a span at fixed
cut points — the keyword, the links, the splitters — and every word
between cuts is an opaque string it carries but never reads, so the
payload stays natural language for the agent. The two mix freely in
one sentence, and the boundary cuts both ways: unmarked prose is never
an edge — unbraced `if` is the deliberate way to keep a condition out
of the chain — and prose never restates a span; a sentence that
shadows a primitive becomes the span or is reworded away.

Two live uses. In each, the span is the prose as it stands in the
runbook file, and the edge below it is what the deterministic parser
generates from that span. A simple read, from intake:

```
{Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md);
the brief formats, brief principles, and the readiness bar}

  ├─reads───► [issue-authoring] Standard
```

A condition nesting a read, from design:

```
{If §2 settled that the public surface is load-bearing,
{Read [design-it-twice.md](references/design-it-twice.md)} and work through it}

  ├ ╌ reads ╌ ► design-it-twice.md    if §2 settled that the public surface is load-bearing
```

The rest of this file builds that trip up piece by piece: which
primitives come from where, and the rules for writing each span.

## The primitive map

Every higher primitive is either **derived** from the runbook's file or
**declared** in its body as a span.

The derived primitives:

| Primitive | Source | Detail |
| --------- | ------ | ------ |
| node type | the file path | `agents/` is an Agent, `SKILL.md` a Skill, `scripts/` or a script extension a Script |
| node data | frontmatter, verbatim | — |
| runbook summary | frontmatter `description` | — |
| args | frontmatter `arguments` list | names only — the name carries the meaning; no placeholder in the body |

The declared primitives:

| Primitive | Span |
| --------- | ---- |
| reads | `{Read <one link>}` |
| reads — GitHub | `{Read from GitHub …}` |
| writes — local file | `{Write …}` |
| writes — GitHub | `{Write to GitHub …}` |
| writes — scratch | `{Write to scratch …}` |
| writes — git | `{Commit …}` + fenced command |
| does — Agent | `{Launch <one link>}` |
| does — Skill or Script | `{Run <one link>}` |
| overrides … with … | `{Override <link> … with <link> …}` |
| reports | `{Report …}` |
| condition | `{If <condition>, {…}}` |
| prohibition | `{Never {…}}` |

Keywords are imperative — commands to the executing agent; the chain's
edge labels are their third-person translation.

## Writing the spans

A span is `{keyword payload}`: flat by default, nested at most two
deep — `If` and `Never` spend the cap. The keyword matches
case-insensitively, a span may wrap across source lines, and spans
count only outside code spans and fenced blocks. The rules for each
declared form, refining the table above:

**Targets.** Where the table says `<one link>`, exactly one markdown
link in the payload names the target; every other word is annotation —
instruction to the executing agent, never read by the parser. One
target per span: two reads are two spans. A does-link points at the
live harness path (`~/.claude/skills/…`, `~/.claude/agents/…`). A
`#fragment` on any link must match a heading in the target file. A
linkless `{Read}` may instead carry one inline-code target
(`` {Read `CONTEXT.md` …} ``), taken verbatim.

```
{Run [/grilling](~/.claude/skills/grilling/SKILL.md) once to sharpen the raw idea}
```

The link is the target; "once to sharpen the raw idea" is annotation.

**Buckets.** The keyword picks the write bucket — `Commit` is git,
`Write` is local file — unless the payload opens with `to GitHub` or
`to scratch`; `from GitHub` does the same for `Read`. A `{Commit …}`
span requires a fenced git command block in the same step, and span
and block must agree.

```
{Write to scratch a self-ignoring `.datasheet/` directory}
```

The `to scratch` prefix picks the bucket; bare `{Write …}` would be
the local-file bucket.

**Splitters.** In `{If <condition>, {…}}`, the text before the first
nested span is the condition, lifted verbatim; every nested span fires
under it. In `{Override … with …}`, the word `with` splits the
payload — one link on each side, the overridden clause before, the
replacement after. In every payload, the first `;` ends what travels
to the chain: front the kernel, elaborate after the semicolon.

```
{Write the target document in place; it must say the same things
without committing any of the named tics}
```

"the target document in place" travels to the chain; everything after
the semicolon stays in the file.

**Prohibition.** `{Never {…}}` wraps exactly one span — inner keyword
`Write`, `Commit`, or `Merge` — and flips it from action to ban. A ban
the vocabulary cannot carry stays plain prose, recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

```
{Never {Commit}} — leave the changes in the working tree for review.
```

The span is the braces alone; the prose after the dash stays outside
it.

**Reports.** `{Report …}` reports the constant `outcome: str` — a
runbook's report is prose — with the payload as annotation.

```
{Report one line: worktree and branch removed, main at that commit}
```

The edge is `outcome: str`; the whole payload rides as annotation.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
]]></tool_result>
</message>
<message role="assistant" ordinal="56" timestamp="2026-08-30T14:37:11.794Z" has_tool_use="true">
<tool_call id="toolu_01PhT8zMKoMr51D23K5DoST9" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,90' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md","description":"Read DECLARATION (short file, targeted)"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,90' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md
]]></tool_body>
<tool_result><![CDATA[
Exit code 1
sed: -e expression #1, char 4: missing command
]]></tool_result>
</message>
<message role="assistant" ordinal="58" timestamp="2026-08-30T14:37:14.599Z" has_tool_use="true">
<tool_call id="toolu_01XySfz8bBSZzboT5TtfxFSv" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,60' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py \u0026\u0026 grep -n 'def \\|--check' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py","description":"Read chaingen.py docstring and structure"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,60' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py && grep -n 'def \|--check' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py
]]></tool_body>
<tool_result><![CDATA[
sed: -e expression #1, char 4: missing command
]]></tool_result>
<tool_call id="toolu_01XxvXindWAQyht5iuvs8V8b" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,25' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md","description":"Read LEDGER intro"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,25' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md
]]></tool_body>
<tool_result><![CDATA[
Exit code 1
sed: -e expression #1, char 4: missing command
]]></tool_result>
</message>
<message role="assistant" ordinal="61" timestamp="2026-08-30T14:37:20.406Z" has_tool_use="true">
<tool_call id="toolu_01TjmjdGXoGg5yzcu5hiy851" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,90p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md","description":"Read DECLARATION"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,90p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Reference Chain Declaration
description: The Reference chain declared — a runbook's behavior and call signature as nodes and edges
---

# Reference Chain Declaration

The **Reference chain** is one CLOA abstraction: the construction
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
rules for the runbook family. This file declares the object itself — its
nodes and its edges. The mechanics that construct a
chain from runbook prose — the primitive map and the rules for
writing spans — sit one layer down in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md). Same
working-file conventions as the branch plan sets out.

## The chain

A Reference chain is abstractions and the actions that connect them:
**nodes** joined by labeled **edges**, rooted at one runbook.

The chain's origin: a runbook is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
contract. The Reference chain is that contract written down: the
signature (args in, reports out) plus the effects, in the coarse order
they fire. Not full fidelity — the chain is a collapse of the runbook's
program, and the fine-grained sequencing it drops stays below the CLOA.

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub, a
file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | reads                  | —           | Its own noun and verbs, in [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#a-noun-with-one-or-more-verbs) |
| Agent    | does                   | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | does                   | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | does                   | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under its
node.

## Edges

An edge is an action. The six labels:

| Label | The action | Detail |
| ----- | ---------- | ------ |
| does | run a runbook or a script | — |
| reads | consult | — |
| overrides … with … | substitute a previous clause | — |
| writes | change state | target is one of four buckets — `git(commit, push)` |
| args | take the caller's input | by name — `friction` |
| reports | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type.

How each edge is written in runbook prose is ruled in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md#the-primitive-map),
and how it draws in
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md).

Any edge may carry a **condition** — what must hold for it to fire. A
conditional edge draws dashed; an unconditional edge draws solid. The
condition never changes the edge's type.

Whatever a runbook's prose cannot express as an edge is a residual,
recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Acronyms

None.
]]></tool_result>
</message>
<message role="assistant" ordinal="63" timestamp="2026-08-30T14:37:21.834Z" has_tool_use="true">
<tool_call id="toolu_01FSXU5bhRqy6JLHcH2WWknT" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,60p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py; grep -n 'def \\|--check' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py","description":"Read chaingen.py docstring and structure"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,60p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py; grep -n 'def \|--check' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/parser/chaingen.py
]]></tool_body>
<tool_result><![CDATA[
#!/usr/bin/env python3
"""chaingen — reconstruct a runbook's Reference chain from its encoded file.

Prototype implementing REFERENCE-CHAIN-ENCODING.md's certified transform: slice, never
interpret. Cut points are the keyword, the markdown
link(s), the `with` splitter, nested braces, and the first semicolon.
Everything between cut points is opaque verbatim text. A `#fragment` on a
read/launch/run link target splits off as a `§ fragment` annotation on the
edge, after failing loud unless it matches a heading slug in the target.
A `{Never {…}}` span wraps one primitive span and renders a prohibition
edge — `never <verb>`, the wrapped payload's kernel as target, possibly
empty. A bucket prefix opens a linkless payload and names the target
node: `{Write to GitHub …}` / `{Write to scratch …}` pick the write
bucket, `{Read from GitHub …}` the GitHub read.

Usage:
    chaingen.py            regenerate chains.txt — every runbook in the
                           corpus (dotfiles/dot-claude agents and
                           skills), blank-line separated
    chaingen.py --check    regenerate in memory and diff against
                           chains.txt; exit 1 on drift
"""

import difflib
import glob
import os
import re
import sys

LEXICON = {
    "read": "reads",
    "commit": "writes",
    "write": "writes",
    "report": "reports",
    "launch": "does",
    "run": "does",
    "override": "overrides",
    "if": "condition",
    "never": "never",
}

# A Never span wraps one primitive span and flips it from assertion to
# prohibition. Only these keywords can be prohibited; the label keeps each
# keyword's own verb — commit stays "commits", not the assertion fold to
# "writes", since no git block exists to disambiguate.
NEVER_LEXICON = {
    "write": "writes",
    "commit": "commits",
    "merge": "merges",
}

NODE_DATA_KEYS = ("tools", "model", "effort", "allowed-tools", "disallowed-tools")

# Bucket prefixes: a fixed literal opening a linkless payload picks the
# target node. Write buckets serve assertion and prohibition alike, so
# {Never {Write to GitHub}} draws the same GitHub node.
WRITE_BUCKETS = (("to GitHub", "GitHub"), ("to scratch", "scratch"))
READ_BUCKET = ("from GitHub", "GitHub")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
20:    chaingen.py --check    regenerate in memory and diff against
75:def split_frontmatter(text, path):
93:def parse_arguments(meta):
112:    def __init__(self, start):
119:def scan_spans(body):
157:def keyword_of(span):
171:def collapse(text):
176:def kernel(text):
187:def one_link(payload, where):
197:def split_bucket(payload, prefix):
206:def one_code(payload, where):
220:def repo_root(start):
230:def resolve(link_target, source_file):
263:def classify(link_text, link_target, source_file):
296:def github_slug(heading):
306:def heading_slugs(path):
325:def split_anchor(link_target, source_file, where):
340:def git_detail(body, after):
363:    def __init__(self, label, target, annotation="", condition=""):
371:def edge_from_span(key, payload, span, body, source_file):
424:def edges_of(body, source_file):
494:def render_edge(edge, last):
508:def render_unit(path):
529:def all_runbooks(claude_dir):
536:def unit_name(path):
544:def main(argv):
545:    """Write chains.txt, or with --check diff against it."""
556:    if argv == ["--check"]:
]]></tool_result>
</message>
<message role="assistant" ordinal="65" timestamp="2026-08-30T14:37:22.404Z" has_tool_use="true">
<tool_call id="toolu_01R8BvbPYcgCXWRAuR6hpYCz" name="Bash" category="Bash">
<arguments><![CDATA[
{"command":"sed -n '1,25p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md","description":"Read LEDGER intro"}
]]></arguments>
</tool_call>
<tool_body><![CDATA[
$ sed -n '1,25p' /home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-2/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md
]]></tool_body>
<tool_result><![CDATA[
---
type: General-Sheet
title: Residual Ledger
description: The system-wide record of what the current abstractions cannot express — one section per registry type ruled important
---

# Residual Ledger

The system-wide record of residuals: what the current abstractions
cannot express. One section per registry type ruled important in
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)'s
registry dispositions — only Runbooks today. That is all an entry is —
a record.

## Runbooks

Per runbook ported to the
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN-DECLARATION.md):
what the full rewrite could not express, recognized and written down at
the moment of porting. Entries name spans and keywords in the vocabulary
[Reference Chain Encoding](/no-more-slop-branch-working-files/REFERENCE-CHAIN-ENCODING.md)
declares.

An entry is a couple of sentences, hard limit: name each specific
action the file could not express and why the map cannot say it —
]]></tool_result>
</message>
<message role="assistant" ordinal="67" timestamp="2026-08-30T14:37:24.979Z">
Done. In the worktree on `no-more-slop-2`, and the reads are in: NO-MORE-SLOP.md, CLOA-ABSTRACTIONS.md, and REFERENCE-CHAIN-ENCODING.md in full; DECLARATION, the LEDGER intro, and chaingen.py&#39;s docstring/structure targeted. Ready — you drive.
</message>
<message role="user" ordinal="68" timestamp="2026-08-30T14:38:11.798Z">
I wanna understand the hierarchy and the levels of abstractions as we go between these files and the various concepts. First, list the various levels and abstraction concepts in some kind of hierarchy proceeding from high level to low level. Again, this should be a short response. We are tuning the conversation.
</message>
<message role="assistant" ordinal="69" timestamp="2026-08-30T14:38:17.299Z">
From high to low:

1. **Goal** — user understands the repo without reading it all (NO-MORE-SLOP.md).
2. **CLOA** — the shared level of abstraction; its principles (NO-MORE-SLOP.md).
3. **Ontology** — the roster of primitives: nouns with verb sets — Standard, Reference chain (CLOA-ABSTRACTIONS.md).
4. **One primitive declared** — the Reference chain object: nodes, six edge labels, buckets (REFERENCE-CHAIN-DECLARATION.md).
5. **Encoding** — the grammar that writes those edges in prose: spans, keywords, splitters (REFERENCE-CHAIN-ENCODING.md).
6. **Deterministic code** — the parser certifying the grammar (`parser/chaingen.py`, `--check`).

Orthogonal to the stack: the **EM loop** is the procedure that generated levels 3 and 5 (one run each), the **primitive map** joins adjacent runs, and the **Residual Ledger** records what any level fails to carry.
</message>
<message role="user" ordinal="70" timestamp="2026-08-30T14:39:19.602Z">
Yeah. So talk to me about primitive map. draw those levels on screen again and when there is a map in between layers, you should insert it in a way that is visually distinct. start to make this more of an ASCII art instead of a bulleted numbered list.
</message>
<message role="assistant" ordinal="71" timestamp="2026-08-30T14:39:29.1Z">
<code_block><![CDATA[
Goal ─────────── understand the repo without reading it all
CLOA ─────────── the shared vocabulary level (principles)

  ┌────────────────────────────────────────────────────────┐
  │ ontology       nouns + verbs                           │
  │                (Reference chain: reads, writes, …)     │
  └────────────────────────────────────────────────────────┘
        ▲
        ║  PRIMITIVE MAP — one lower expression per higher
        ║  primitive:  reads ↔ {Read …},  writes ↔ {Write …}
        ▼
  ┌────────────────────────────────────────────────────────┐
  │ encoding       grammar over runbook prose              │
  │                (braced spans: {Read …}, {If …, {…}})   │
  └────────────────────────────────────────────────────────┘
        ▲
        ║  MAP, one rung further — grammar ↔ parser,
        ║  the certified transform, pinned by --check
        ▼
  ┌────────────────────────────────────────────────────────┐
  │ deterministic  chaingen.py → chains.txt                │
  └────────────────────────────────────────────────────────┘
]]></code_block>
The primitive map is the join between two adjacent EM-loop runs: each higher primitive gets exactly one lower expression (the ideal — one-to-one). It&#39;s what makes the next run start from structure instead of conversation. Concretely it&#39;s the two tables in REFERENCE-CHAIN-ENCODING.md — derived primitives (from the file) and declared primitives (edge label ↔ span form).

The Declaration file sits *inside* the ontology box — it&#39;s one primitive written out — not a separate layer.
</message>
<message role="user" ordinal="72" timestamp="2026-08-30T14:43:08.111Z">
I don&#39;t understand the difference between derived primitives (from the file) and declared primitives (edge label ↔ span
  form)
</message>
<message role="assistant" ordinal="73" timestamp="2026-08-30T14:43:12.872Z">
The split is **where the parser gets each piece of the chain from**.

**Derived** — the parser computes it from the file itself; no writer action. Node type comes from the path (`agents/` → Agent), summary from frontmatter `description`, args from frontmatter `arguments`. These exist whether or not anyone writes a span.

**Declared** — the writer must put a span in the prose or the edge doesn&#39;t exist. `{Read …}` makes a reads edge, `{Commit …}` a git write. No span, no edge.

So: derived = free, extracted from structure the file already has; declared = authored, one brace-marked sentence per edge.
</message>
<message role="user" ordinal="74" timestamp="2026-08-30T14:44:00.363Z">
Oh ok. That distinction is too granular for what I&#39;m focusing on here: the hierarchy, levels, primitives, map, etc. That is an implementation detail. You can disregard that going forward.
</message>
<message role="assistant" ordinal="75" timestamp="2026-08-30T14:44:02.763Z">
Disregarded. The working picture stays: layers (ontology → encoding → deterministic code), one EM-loop run per layer, a primitive map joining each adjacent pair, residuals to the Ledger.
</message>
<message role="user" ordinal="76" timestamp="2026-08-30T14:44:33.4Z">
Now i see you only mentioned REFERENCE-CHAIN-ENCODING.md when talking about primitives. but don&#39;t we have two layers of primitives?
</message>
<message role="assistant" ordinal="77" timestamp="2026-08-30T14:44:38.877Z">
Yes — every loop run outputs its own primitives, so there&#39;s a roster at each layer:

- **Ontology-layer primitives** — the nouns and verbs: the Reference chain with its six edge labels (reads, writes, does, …). Rostered in CLOA-ABSTRACTIONS.md, and written out in full in REFERENCE-CHAIN-DECLARATION.md.
- **Encoding-layer primitives** — the span forms: `{Read …}`, `{If …, {…}}`, `{Never {…}}`. Rostered in REFERENCE-CHAIN-ENCODING.md.

The primitive map is exactly the join between those two rosters — edge label ↔ span form. My earlier answer collapsed the upper roster into the map&#39;s home file; the Declaration file is the upper layer&#39;s primitives.
</message>
<message role="user" ordinal="78" timestamp="2026-08-30T14:45:53.609Z">
I think you not mention primitives, in the ontology layer because the reference chain declaration file does not use the word primitive. It uses nodes and edges instead.

Would you agree that nodes and edges are actually the primitives? This may point to us wanting to rewrite the file to use the actual word primitive. Just thinking, do not do yet.
</message>
<message role="assistant" ordinal="79" timestamp="2026-08-30T14:46:04.088Z">
Agree, with one wrinkle. The primitive map&#39;s upper side is literally the edge labels (`reads ↔ {Read …}`), and CLOA-ABSTRACTIONS.md&#39;s layer-invariance diagram names the ontology run&#39;s output as &#34;nouns + verbs (Reference chain: reads, writes, reports, …)&#34; — so the edges are the verbs and the node types are the nouns. Nodes and edges are the ontology-layer primitives, and the Declaration file declares them without ever saying so.

The wrinkle: CLOA-ABSTRACTIONS.md also uses &#34;primitive&#34; one level coarser — the *Reference chain itself* is &#34;one primitive&#34; of the ontology, alongside Standard. So &#34;primitive&#34; currently means both a whole abstraction and its constituent nouns/verbs. That double use is exactly the terminology-sweep item in the branch plan; a rewrite of the Declaration to say &#34;primitive&#34; would force choosing one meaning.
</message>
<message role="user" ordinal="80" timestamp="2026-08-30T14:48:50.222Z">
My goal in this session is to tighten up our structure for this process, make sure we&#39;re using words in precise ways that align with their overall meaning in the English language and in computer science, etcetera, and to generalize our process so it can apply to any repository and any sort of functional behavior in a system described by documentation. Everything you&#39;re looking at now is our first attempt to do this. We&#39;re still smoothing out the rough parts.

Let&#39;s talk about the precise meanings of &#34;primitive&#34; and &#34;ontology&#34;. are the ways we are using these words today consistent with their actual meaning in language? When we&#39;re talking about this, I do not want to be extremely pedantic. You should scrutinize and keep me honest, but do not go full english professor on me
</message>
<message role="assistant" ordinal="81" timestamp="2026-08-30T14:49:17.208Z">
**Primitive** — the fine-grained use is sound. In CS a primitive is an atomic unit of composition within a system (int, line, MOV), and it&#39;s layer-relative — one layer&#39;s primitive is the layer below&#39;s composite, exactly like instruction sets. Edge labels and span forms fit that perfectly, and the primitive map is the standard &#34;higher construct → lower implementation&#34; move. The clash is only the coarse use: calling the Reference chain itself &#34;one primitive&#34; breaks the word, because the chain is a *composite* — nodes and edges assembled. The files already have the right word for that grain: &#34;abstraction&#34; (or &#34;construction&#34;). One fix: abstractions have primitives; the chain is an abstraction, its nodes and edges are its primitives.

**Ontology** — roughly right, mildly grandiose. An ontology is a specification of what exists in a domain — the categories and their relations. The registry pass is genuinely ontological: ruling each document type in or out of existence-at-the-CLOA. But the primitives table is closer to a *vocabulary* or *type system* — the formal-CS sense of ontology (OWL, knowledge graphs) implies properties, relations, and instances we don&#39;t model. It&#39;s tolerable if you keep one referent: the ontology is *what exists at the CLOA* (the registry rulings + the abstraction roster), and stop also using it as a layer name (&#34;the ontology level&#34; → the abstraction layer).

Net: &#34;primitive&#34; needs the one-meaning fix; &#34;ontology&#34; needs a single referent or a humbler word.
</message>
<message role="user" ordinal="82" timestamp="2026-08-30T14:53:57.201Z">
Okay. I definitely wanna lean into this computer science thing. In my mind, I&#39;m thinking we are indeed kind of constructing our own language here, and I want to model it around the idea of computer science terms in programming languages. We are programming with documentation here, but instead of using an existing language like Python, we are making our own, it just happens to be very very simple because constructing these abstractions is extremely expensive in terms of user thought, working sessions with models like you, and Also, we have to write deterministic code to support the entire structure of things we dream up.

By the way, this raises a point I wanna consider later: We are constructing the deterministic scaffolding of this hierarchy of ideas and fuzzy documentation. So our repository right now is this giant pile of fuzzy ideas and high dimensional stochastic documentation: we are building structure into that kind of like bones, and they are all based on deterministic code all the way up and down.

As for ontology, I do have a long term ambition to define properties and relations and apply some sort of deterministic ontology solver that validates or invalidates specific operations amongst abstractions. We have not built that yet, but I definitely plan on doing it. whether that means we leave ontology as a word to create room for later or if we change it now and know that we might put it back later remains to be decided.

And yet, also, I want to figure out how to fit the word &#34;abstraction&#34; in as well. would you say that &#34;abstraction layer&#34; is an alternative sibling name replacement for &#34;ontology&#34; in our use case here? are they the same thing, but one is larger scope than the other?
</message>
<message role="assistant" ordinal="83" timestamp="2026-08-30T14:54:15.575Z">
Not siblings — orthogonal, and one is scope-larger.

An **abstraction layer** is positional: a rung in the stack, defined by what it hides from the rung above. Layers are ordered — ontology-run above encoding-run above parser.

An **ontology** is an inventory: what exists and how it relates, with no inherent ordering. In your system that inventory spans layers — every abstraction, its primitives, the registry rulings — so it&#39;s larger-scope than any layer and can&#39;t be swapped in as a layer&#39;s name. The current &#34;at the ontology level&#34; phrasing is the conflation.

Your PL framing sorts it cleanly:

- The **layers** are language spec → grammar → compiler (Declaration → Encoding → chaingen.py).
- The nouns-with-verbs roster is the **type system** — what types exist and what operations each supports. That&#39;s what CLOA-ABSTRACTIONS.md&#39;s table actually is.
- Your future ontology solver is the **type checker** — deterministic validation of which operations among abstractions are legal. That ambition is exactly what makes &#34;ontology&#34; worth reserving: keep the word for the relation-bearing, solver-backed inventory you plan to build, and stop spending it on today&#39;s roster, which &#34;type system&#34; (or just &#34;the abstraction roster&#34;) names more honestly.

So: rename the layer (it&#39;s the abstraction layer, or the declaration layer), keep &#34;ontology&#34; parked for the solver-era artifact.
</message>
<message role="user" ordinal="84" timestamp="2026-08-30T15:01:30.497Z">
Let&#39;s begin to pivot to refactoring our terminology across all the groups and layers. When we are done, the functionality As described in the documentation and implemented in the system, will be the same, but we will have it better organized at a theoretical level in this chat terminal, and we will be generalized and standard as much as possible so that we can extend this further either in this particular use case or more importantly, to other use cases you have not yet seen in any of your context (other parts of this repo or other repos in general).

and we should use simple words that have analogies to deterministic code. Therefore, I like when you lean on &#34;type&#34;.

Further clarifying question: is it true that ontology contains a registry, but has other things as well such as valid combinations of operations on primitives?
</message>
<message role="assistant" ordinal="85" timestamp="2026-08-30T15:01:39.367Z">
Yes. In the formal sense an ontology has three parts, and the registry is only the first:

1. **Categories** — what kinds of things exist. That&#39;s the registry: the document-type rulings, the abstraction roster.
2. **Relations** — how kinds connect (a Skill *does* a Script, a chain *reads* a Standard).
3. **Axioms** — which combinations are valid: constraints a solver can check (&#34;a `Never` wraps exactly one write-family verb&#34;, &#34;a Commit requires a git block&#34;).

In code terms: the registry is the symbol table of declared types; relations plus axioms are the typing rules. Today you have 1 fully, 2 informally (the edge-label tables), and 3 scattered as prose rules the parser happens to enforce. The solver ambition is making 2 and 3 first-class and checkable — that&#39;s when the word &#34;ontology&#34; gets fully earned.
</message>
<message role="user" ordinal="86" timestamp="2026-08-30T15:02:28.771Z">
I don&#39;t understand how &#34;a skill does a script&#34; is differernt from &#34;which combinations are valid.&#34; You made them two distinct lines.
</message>
<message role="assistant" ordinal="87" timestamp="2026-08-30T15:02:38.818Z">
Fair hit — the line is blurry, and here&#39;s the actual distinction:

A **relation** declares an edge kind and its signature: `does: Runbook → Runbook | Script`. That already excludes some combinations (you can&#39;t *does* a Standard) — so yes, it does validity work.

An **axiom** is a constraint the signatures can&#39;t express — it spans multiple relations or counts things: &#34;a `Never` wraps exactly one span,&#34; &#34;nesting at most two deep,&#34; &#34;a Commit edge requires a git block in the same step.&#34;

Code analogy: relations are type signatures; axioms are the contracts a signature can&#39;t carry. The boundary between them is a design choice, not a fact — you can often enrich types until an axiom becomes a signature. So the honest version of my two lines: relations = validity that fits in a signature, axioms = validity that doesn&#39;t.
</message>
<message role="user" ordinal="88" timestamp="2026-08-30T15:03:29.621Z">
Does python type hinting define these things under the hood? Side question I&#39;ll rewind just curious
</message>
<message role="assistant" ordinal="89" timestamp="2026-08-30T15:03:40.138Z">
Only the relation half. A hint like `def run(r: Runbook) -&gt; Report` is exactly a relation signature, and mypy is the solver over that algebra. Python has no way to state axioms — constraints beyond signatures like &#34;arg2 must be shorter than arg1&#34; or &#34;this call requires that other call first.&#34; Languages with dependent or refinement types (Idris, Liquid Haskell) can push axioms into signatures; Python fakes it at runtime with validators (pydantic) or asserts, which is enforcement, not declaration.

The interesting edge: tricks like `Literal`, `@overload`, and generic bounds let you smuggle some axioms *into* signatures — the &#34;enrich types until the axiom becomes a signature&#34; move from a minute ago, live in mypy today.
</message>
<message role="user" ordinal="90" timestamp="2026-08-30T15:06:35.025Z">
Ok. Now continuing to pivot to a theoretical refactoring in this terminal, which terms conflicted, overloaded, or were ambiguous At the beginning of this conversation, and how would we sort them out to make the theory clean and general? This could involve specifically declining terms if we had too many at the start.
</message>
<message role="assistant" ordinal="91" timestamp="2026-08-30T15:07:02.035Z">
The starting inventory had five problem terms; here&#39;s the sort-out:

| Term | Conflict at start | Ruling |
|---|---|---|
| **primitive** | Two grains: whole abstractions (&#34;CLOA primitives&#34;) *and* their atoms (edge labels, spans) | Keep only the fine grain: a layer&#39;s atomic units. The **primitive map** keeps its name — it&#39;s genuinely primitive-to-primitive. |
| **ontology** | Three referents: the roster, a layer name, the future solver artifact | Park it. Reserved for the solver-era inventory (categories + relations + axioms). Today&#39;s roster → the **type system**; the layer gets renamed. |
| **abstraction** | Catch-all for &#34;noun with verb set&#34;; also does duty as file title and generic English | Decline as a term of art. &#34;A noun with operations&#34; is a **type**. Generic English use survives, uncapitalized and unloaded. |
| **noun / verb** | Informal duplicates of the same idea | Decline both: **type** and **operation**. Standard is a type with operations define, audit, enforce, adopt; edge labels are operations. |
| **level / layer** | &#34;Ontology level&#34; (loop stack) collides with NO-MORE-SLOP&#39;s &#34;Levels&#34; section (inside-a-file vs above-the-file) | **Layer** = the loop stack only (type layer → encoding layer → parser). The Levels section needs a different word — &#34;altitudes&#34; or a rewrite. |

One consequence worth noting: with &#34;type&#34; installed, the Reference chain gets a crisp identity — it&#39;s a runbook&#39;s *type signature* (args in, reports out, effects). CLOA-ABSTRACTIONS.md already gestures at this (&#34;each document should probably have a typed signature&#34;) without claiming it.

Unchanged and clean: CLOA, residual, registry, span, bucket, the loop, covering set.
</message>
<message role="user" ordinal="92" timestamp="2026-08-30T15:14:23.106Z">
&#34;  │             │ Two grains: whole abstractions (&#34;CLOA      │ Keep only the fine grain: a layer&#39;s atomic units. The     │
  │ primitive   │ primitives&#34;) and their atoms (edge labels, │ primitive map keeps its name — it&#39;s genuinely             │
  │             │  spans)                                    │ primitive-to-primitive.        &#34; agreed

&#34;  │             │ Three referents: the roster, a layer name, │ Park it. Reserved for the solver-era inventory            │
  │ ontology    │  the future solver artifact                │ (categories + relations + axioms). Today&#39;s roster → the   │
  │             │                                            │ type system; the layer gets renamed.        &#34; agreed but I want to write  short paragraph somewhere in NO-MORE-SLOP.md tracking our future idea for this.

&#34;  │             │ Catch-all for &#34;noun with verb set&#34;; also   │ Decline as a term of art. &#34;A noun with operations&#34; is a   │
  │ abstraction │ does duty as file title and generic        │ type. Generic English use survives, uncapitalized and     │
  │             │ English                                    │ unloaded.       &#34; agreed

&#34;  │             │                                            │ Decline both: type and operation. Standard is a type with │
  │ noun / verb │ Informal duplicates of the same idea       │  operations define, audit, enforce, adopt; edge labels    │
  │             │                                            │ are operations.      &#34; Agreed and very nice job, without you pushing me here I would have stuck to my guns because I think declaring Noun:Verbs as an idea is very clever. I would like to mention somewhere that the Noun:Verbs pattern is very useful and we should reach for it when it fits.

&#34;  │ level /     │ &#34;Ontology level&#34; (loop stack) collides     │ Layer = the loop stack only (type layer → encoding layer  │
  │ layer       │ with NO-MORE-SLOP&#39;s &#34;Levels&#34; section       │ → parser). The Levels section needs a different word —    │
  │             │ (inside-a-file vs above-the-file)          │ &#34;altitudes&#34; or a rewrite.        &#34; don&#39;t quite understand what you mean by &#34;layer applies to the loop stack only&#34;. What other places exist that you are saying it does not apply to? Also, I don&#39;t understand what you mean by &#34;The levels section needs a different word.&#34;

&#34;it&#39;s a runbook&#39;s type 
  signature (args in, reports out, effects)&#34; I would like to double check with you that a type signature can include effects. I look at the reference chain now as a parsimonious approximation of a run book as a function. I&#39;m not used to thinking of type signatures as including the code inside the function. I think of them as &#34;args in return out&#34; only.
</message>
<message role="assistant" ordinal="93" timestamp="2026-08-30T15:14:43.92Z">
**Level/layer.** The words currently point at two different axes. Axis one: the loop stack — the ontology run sits above the encoding run above the parser (CLOA-ABSTRACTIONS calls this &#34;the ontology level,&#34; &#34;one level down,&#34; &#34;layer invariance&#34;). Axis two: NO-MORE-SLOP&#39;s `## Levels` section — the zoom of user understanding: &#34;inside one file&#34; vs &#34;above the file.&#34; Those are unrelated axes sharing one vocabulary, so &#34;level&#34; is ambiguous on contact. My ruling: **layer** names loop-stack rungs only; the Levels section&#39;s axis gets a different word (or its section rewritten) so a reader never merges the two. &#34;Altitude&#34; was one candidate for the zoom axis.

**Effects in a type signature.** You&#39;re right for mainstream usage: a plain type signature is args in, return out — effects invisible. But there&#39;s real CS precedent for putting effects in types: effect systems (Koka), Haskell&#39;s `IO` in the return type, Java&#39;s checked exceptions. The established term is a **type-and-effect signature**. The chain is close to that but goes one step further — it keeps coarse *ordering* of effects, which effect systems typically don&#39;t (they carry an unordered effect set). So the honest naming: the chain is a runbook&#39;s **contract** — type signature plus effect summary — and &#34;type signature&#34; alone undersells it. Your &#34;parsimonious approximation of the runbook as a function&#34; is accurate; the chain is signature + which-state-it-touches, never the body.

Queued for the edit pass (not doing yet): the ontology-future paragraph in NO-MORE-SLOP.md, and a note that the noun-with-verbs pattern (now type-with-operations) is a reusable move to reach for.
</message>
<message role="user" ordinal="94" timestamp="2026-08-30T15:17:44.445Z">
Level/layer: Is it possible that the reason your responses here are confusing me is because I am focused entirely on the theoretical construction of how these words fit together? Meanwhile, you are combining both the theoretical construction and the specific way we wrote the documents? I&#39;m not thinking about writing the documents yet. Updating the documents is a separate step that we are not thinking about yet. Focus on the theoretical construction here in this terminal only.

I like contract. If you&#39;re willing to sign off that &#34;contract includes signature / signature is a subset of contract&#34;, in general, then we can use the word contract, and it simplifies and gives us flexibility for making this a general approach in the future to many unseen use cases we have not considered yet.
</message>
<message role="assistant" ordinal="95" timestamp="2026-08-30T15:17:57.439Z">
**Level/layer** — you&#39;re right, I was dragging the documents in. Theory only: there is one concept competing for the word — the loop stack — and **layer** names it: a rung where a loop run happened, joined to the next rung by a primitive map. Done. The understanding-zoom idea (inside a file vs above it) is a separate concept that isn&#39;t asking for a name right now; it only collided on paper, and paper is a later step.

**Contract ⊇ signature** — signed off, and it&#39;s standard usage, not a stretch. In design-by-contract and API-design terms, a contract is everything a caller may rely on: the signature (args in, results out) plus effects, preconditions, error behavior — whatever the promise includes. The signature is the machine-checkable subset. So: the Reference chain is a runbook&#39;s **contract**; today&#39;s chains carry signature + ordered effects, and the word leaves room for future use cases to include more or less without renaming.
</message>
<message role="user" ordinal="96" timestamp="2026-08-30T15:21:16.366Z">
Let&#39;s note our definition of contract and mention that signature is a component in our final deliverable.

I think we have deconflicted and aligned on all our terminology. So let&#39;s pivot now and produce our refactored theory. Begin by listing all the terms we have aligned on, only the ones included in the theory. If we decided to drop a term, do not include it. going to make this list now. We are not drawing the diagram yet. I expect to draw the diagram in the following turn.
</message>
<message role="assistant" ordinal="97" timestamp="2026-08-30T15:21:35.669Z">
The refactored theory&#39;s term list:

**The stack**
- **layer** — a rung in the loop stack; one loop run happened there.
- **primitive** — a layer&#39;s atomic units.
- **primitive map** — the join between adjacent layers: one lower expression per higher primitive.
- **the loop** — the EM procedure that generates a layer&#39;s primitives from a target artifact.
- **residual** — what a layer&#39;s primitives cannot express; recorded, never forced.

**The types**
- **CLOA** — the level of abstraction where user and AI communicate in identical terminology.
- **type** — a noun with a small fixed set of operations.
- **operation** — an action a type supports.
- **type system** — the roster of types at the CLOA and the operations each supports.
- **registry** — the inventory of document kinds, each ruled in or out of the type system.
- **registry pass** — the loop&#39;s first move: produce the registry&#39;s rulings.

**The contract**
- **contract** — everything a caller of a runbook may rely on; the signature is a component, alongside effects.
- **signature** — args in, results out; the machine-checkable core of a contract.
- **Reference chain** — a runbook&#39;s contract written as nodes and edges.
- **node** — a type instance an edge lands on.
- **edge** — an operation connecting nodes.
- **span** — the braced unit in prose that declares one edge.
- **bucket** — a write&#39;s target class: git, GitHub, local file, scratch.

**The target state**
- **the pandas standard** — convergence: the user predicts behavior without reading bodies.
- **covering set** — the smallest exemplar group exercising every rule of a design under test.

Reserved, not active: **ontology** — held for the future solver-era inventory (categories + relations + axioms); a tracking paragraph goes in NO-MORE-SLOP.md at edit time.
</message>
<message role="user" ordinal="98" timestamp="2026-08-30T15:29:39.458Z">
&#34;CLOA — the level of abstraction where user and AI communicate in identical terminology.&#34; Identical is true but only part of this. It&#39;s identical, but also our best effort approximation of the true latent CORRECT level that is the highest-level of abstraction the user can get away with, or alternatively, the lowest-level of abstraction that the AI needs the user for in order to match user intent. This is very important, so I am compelled to say it, but it is not a focus for refactoring our theory or drawing the diagram.

&#34;type system — the roster of types at the CLOA and the operations each supports.&#34; Isn&#39;t this more about the roster of types at the layer in question? CLOA is an ephemeral thing that moves dynamically based on user&#39;s zoom chosen level.

span and bucket are very low-level and specific only to the parsing layer. we should use them if we want specific examples of abstractions, but they are not in and of themselves general abstractions. is probably true for reference chain node and edge also, although they are higher in the layers.

we mentioned the PANDAS standard, we should point out both 1) that it is fully deterministic code ( which I am considering calling bedrock, although that inhibits our ability to continue the analogy deeper into deterministic code using industry-standard tools like call graphs, archicture diagrrams, etc.) 2) someone else made it, and we use it as a direct dependency. Meanwhile, the things we are talking about here tend to be things we invent ourselves at great expense.
</message>
<message role="assistant" ordinal="99" timestamp="2026-08-30T15:30:00.25Z">
All four taken. Amendments to the list:

- **CLOA** — definition enriched per your statement (best-effort approximation of the latent correct level: highest the user can get away with / lowest the AI needs the user at). Noted as important, not a refactoring focus.
- **type system** — corrected: the roster of types at *a given layer* and the operations each supports. Layer-relative, since the CLOA moves with the user&#39;s chosen zoom.
- **span, bucket, node, edge** — demoted from general theory to layer-resident examples: node/edge are the contract layer&#39;s primitives, span/bucket the encoding layer&#39;s. Cited as instances, never as theory vocabulary.

The pandas point resurfaces a term already in the files that my list wrongly dropped: **provenance** — declared vs imported. Pandas is an *imported* type system: deterministic all the way down, built by someone else, its contract taken as given, fluency cheap. Our types are *declared*: invented here at great expense in user thought, sessions, and supporting deterministic code. The pandas standard is then precise: make declared types feel like imported ones to their caller.

On **bedrock**: the risk you name is real but avoidable — define bedrock as the *boundary* where targets stop being stochastic, not as a claim of &#34;nothing below.&#34; Determinism keeps its own internal structure (call graphs, import graphs, architecture) and industry tools already serve it; bedrock just marks where our invented machinery stops being necessary and standard tooling takes over. That reading preserves the deeper analogy. Unsettled — your call.
</message>
<message role="user" ordinal="100" timestamp="2026-08-30T15:31:35.271Z">
Oh yes Indeed. In real life, we can proceed through bedrock. It just is super firm and strong, which is indeed the benefit of the deterministic code! The bedrock of determinism. I love it let&#39;s remember that.

Okay. Try to draw the diagram now of the layers.
</message>
<message role="assistant" ordinal="101" timestamp="2026-08-30T15:32:10.098Z">
<code_block><![CDATA[
     stochastic ▲            every layer, same algorithm:
                │            target ──the loop──► primitives (+ residual)
                │            the CLOA rides where the user zooms
 ┌───────────────────────────────────────────────────────────────────┐
 │ TYPE LAYER                                                        │
 │   target:      the documentation corpus                           │
 │   primitives:  the type system — types + operations               │
 │                (instance: contract — the Reference chain;         │
 │                 Standard)                                         │
 └───────────────────────────────────────────────────────────────────┘
       ▲
       ║  PRIMITIVE MAP — one lower expression per higher primitive
       ║  (instance: operation ↔ span form,  reads ↔ {Read …})
       ▼
 ┌───────────────────────────────────────────────────────────────────┐
 │ ENCODING LAYER                                                    │
 │   target:      runbook prose                                      │
 │   primitives:  the grammar — span forms                           │
 │                (instance: {Read …}, {If …, {…}}, {Never {…}})     │
 └───────────────────────────────────────────────────────────────────┘
       ▲
       ║  PRIMITIVE MAP — the maps recurse one rung past the loop:
       ║  grammar ↔ parser, the certified transform, pinned by --check
       ▼
 ═══════════════════ THE BEDROCK OF DETERMINISM ═════════════════════
 │   deterministic code: parser → chains                             │
 │   firm and strong, and it continues below — call graphs, import   │
 │   graphs, industry tooling all the way down                       │
 │                                                                   │
 │   imported type systems (pandas, git) already stand on it;        │
 │   declared ones are built down to it, at great expense            │
 ═════════════════════════════════════════════════════════════════════
  deterministic ▼
]]></code_block>
</message>
<message role="user" ordinal="102" timestamp="2026-08-30T15:37:55.664Z">
/model
</message>
</session>
