---
type: Standard
title: Agentic Box
description: The delegation boundary for autonomous agent work — walls, charter, checks, and emissions around a sealed black box
---

# Agentic Box

A **box** is the unit of full delegation to an autonomous agent: a directory
that defines a boundary — what to build, what may be touched, what verifies
the work, and what must be handed back. Inside the boundary the agent owns
everything. Intent enters through frozen artifacts the agent consults;
results exit through artifacts the human audits. Neither direction is a
conversation, and the run transcript is not part of the interface.

Alignment happens before launch, in machine-checkable artifacts. Audit
happens after the run, on emitted artifacts. During the run the agent
resolves ambiguity from the box's own rules, never by asking.

A worked greenfield-CLI box lives at
[templates/greenfield-cli](/standards/agentic-box/templates/greenfield-cli/box/README.md).

## The four buckets

Every element of a box works by exactly one of four mechanisms. Place each
requirement in the strongest bucket that can hold it.

### Walls — enforced by the harness

What the agent cannot do even when it convinces itself it should: permission
denies, tool restrictions, file fences, iteration and budget caps. Walls are
deterministic and never decay, but they only forbid — they cannot guide. A
box session runs only box work, so its walls are severe: a dedicated worktree,
a `deny Edit(box/**)` freezing the box definition, and whatever tool denials
the mission permits.

### Charter — read by the agent

Prose and structured objects the agent reads: goal, non-goals, tie-breaker
rules, escalation triggers, and a conformance list — paths to the workspace
standards the work product must satisfy (dev-playbook is checked out on every
machine, so standards are referenced by path, never copied). The conformance
list is selected per box type. This is the least reliable bucket: compliance
depends on the agent retaining and applying text, and retention degrades with
run length. Place a requirement here only when no other bucket can hold it.
Every MUST in the charter names the check that enforces it; a requirement
that is not enforced deterministically is unreliable.

### Checks — push back on the work

One function — verifying the box's input→output contract — at three
latencies:

| Tier | Runs | Examples |
|---|---|---|
| Inner loop | continuously during the run | compilers, tests, linters, schemas |
| Gate | at phase and box boundaries | acceptance suites, `gate.sh`, LLM judges |
| Post-hoc | after the run, by the human | audit of emissions |

Push every check as early and as mechanical as it can go. Whatever cannot be
mechanized flows up to the human tier, which emissions exist to feed
cheaply. Check quality is the dominant input to delegation quality: an agent
with real back pressure self-corrects; an agent with only prose guidance
compounds its errors.

### Emissions — produced by the agent

Artifacts the box must hand back besides the work product, with the same
standing as passing tests: the gate fails if they are missing. Emissions are
self-reports, so their formats force falsifiable claims (file:line references,
test IDs — things checkable against the diff). The agent never describes its
own design: describing what is inside a finished box is the job of a separate
describer agent with no stake in the story.

## Box anatomy

A box is a directory, committed on the issue branch of a dedicated worktree:

```
worktree/
├── .claude/settings.json        # walls
├── box/                         # frozen: deny Edit(box/**)
│   ├── README.md                # engine, launch, done, stuck, audit procedure
│   ├── prompt.md                # what the agent is told
│   ├── contract.md              # the external surface: the boundary itself
│   ├── charter.md               # non-goals, tie-breakers, escalation triggers
│   ├── emissions.md             # required deliverables spec
│   ├── gate.sh                  # executable definition of done
│   ├── tests/acceptance/        # frozen boundary tests
│   └── fixtures/                # sample inputs and expected outputs
└── <target>/                    # the agent's territory; all output lands here
```

`gate.sh` exit 0 is the definition of done — nothing else counts. It runs the
frozen boundary tests, runs the agent's own test suite, and asserts every
required emission exists. Because done-ness is a script, it is
engine-independent: nothing under `box/` may assume which engine runs the box.

## Design rules

1. **Boundary tests are frozen.** The agent may draft them, a human reviews
   them, then the wall seals them; the agent never edits them afterward. An
   agent that grades itself against tests it can rewrite is verifying its own
   misunderstanding. Human review effort concentrates here: a short
   declarative test suite is reviewable where an implementation is not.
2. **Internal tests are agent-owned.** They must exist and pass in the gate,
   but no human reviews them. The describer agent reads them afterward as
   evidence of where the agent saw risk.
3. **Pin only bug-worthy behavior.** Boundary tests assert structure, not
   bytes, wherever the human is indifferent; one byte-exact anchor fixture
   exists to catch drift, not to pin style. Overpinning turns harmless agent
   choices into failures; underpinning lets defects through silently.
4. **Emissions are DEVIATIONS and UPSTREAM.** `DEVIATIONS.md` records every
   notable behavior the contract left unpinned, with file:line and the
   resolution rule applied. `UPSTREAM.md` is the upward channel —
   recommendations, untested risks, proposed contract changes the agent may
   not act on itself. Empty sections are valid; absent files fail the gate.
5. **Escalation is a file, not a conversation.** When the box itself is
   defective (contract contradicts a fixture, an acceptance test looks wrong),
   the agent writes `BLOCKED.md` and halts. The human picks it up
   asynchronously. There is no mid-run exchange.
6. **The transcript is not an interface.** Audits read emissions and run the
   gate. Needing to open the transcript is a defect in the emissions spec —
   fix the spec, don't read harder.
7. **The engine is not part of the box.** Ralph loop, one-shot session,
   scatter-gather, chained boxes — a per-mission choice recorded in
   `box/README.md` and swappable without touching anything else. When a
   mission has no plan yet, that is two boxes, not one: an explore box whose
   emission becomes the build box's charter input.

## Audit procedure

The post-hoc check is bounded and artifact-only:

1. Run `box/gate.sh` — a trustless re-check.
2. Exercise the work product on one real input.
3. Read `DEVIATIONS.md` and `UPSTREAM.md`.
4. Run the describer workflow over the agent's territory and diff its account
   against the emissions. Divergence between the agent's story and an outside
   reader's is the highest-value audit signal.

## When a box pays

A box carries setup cost: frozen tests, walls, a gate, an emissions spec. It
earns that cost only when three conditions hold together:

- the agent writes with blast radius, so walls matter;
- done-ness is mechanically checkable, so a gate matters;
- the mission repeats or runs unattended, so a sealed template beats a fresh
  conversation each time.

Work that fails the test is cheaper run as an ordinary supervised agent. A
read-only survey has no blast radius and no mechanical definition of done — its
acceptance test is a human's eye — so it is fan-out agent work, not a box.

Authoring a standard is never box work. The standard is the contract, and the
human's judgment is its only acceptance test; there is no gate for "the owner
likes it now." A box executes against a ratified contract, it does not produce
one. The standard document and the box charter are the same move at different
scales — alignment crystallized once into a referenceable artifact, then
consumed many times without further conversation.

## Open questions

Unresolved. Recorded for future revisions and worked examples to close, not
because the answers are known.

- **Multi-repo boxes.** A box lives in one worktree, which is one repository. A
  mission spanning repositories is decomposed instead: a read-only pass reads
  across all of them (walls are trivial — read anywhere, write only to a
  report), a human ratifies the result, and a single-writable-repo box is
  instantiated per repository and run in parallel. Whether an atomic cross-repo
  write ever forces one box over many worktrees is open; none has appeared in
  this workspace.
- **Empirical ground truth.** A gate built on CI passing across many
  repositories, rather than on a local suite. Unspecified.
- **Emission-quality gating.** Emissions are gated on existence today. An
  LLM-judge check on their substance — that `DEVIATIONS` and `UPSTREAM` say
  something real rather than filling the format — would raise the floor. The
  workspace has a judgments library for exactly this; not yet integrated.
- **Box-type template library.** Which box types earn a committed template, and
  where the instantiation tooling lives. One template exists (greenfield-cli).
- **Consumer-repo instantiation debt.** An instantiated box's `box/*.md` files
  owe `index.md` entries in the consumer repo; that is the instantiation
  tooling's job, and the tooling does not exist yet.
- **Operator-dotfiles leak.** A box session inherits the operator's global
  `~/.claude/CLAUDE.md`. A box aims to be self-contained, so this ambient
  context is an unstated dependency that eventually needs a wall or a stated
  assumption.
- **Prototype-box shakedown.** Run a sealed box once with a cheap model before
  the expensive run. The throwaway output is not the point; the run surfaces
  box defects — an ambiguous contract, a missing wall — while they are cheap to
  fix.