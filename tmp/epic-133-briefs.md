# Conformance epic + leaf briefs — compiled from the #133 triage

Transient working file, the creation script for GitHub. Like
`tmp/triage-133.md` it lives in `tmp/` (outside the OKF bundle) and is
DELETED before the #133 PR opens. Once the epic and its children exist on
GitHub, the issues are the single source of truth and this file has no
authority.

Creation plan (after user approval):

- Create the epic first, then the children **in chain order** — each child
  is created, linked as a sub-issue of the epic, and marked blocked-by its
  predecessor (the blocker must exist before the dependent links to it).
- The epic carries `category:enhancement` only — no mode, tests, or phase
  (epics are never built directly; the role is derived from having
  sub-issues).
- Every child is minted **ready**: full tuple as listed, body verbatim
  from this file.
- `tests:no` children carry `phase:build`; `tests:yes` children carry
  `phase:tdd` (mode:direct routing).

---

## EPIC — Make the standard cards true: audit fleet, gate vocabulary, and issue-overwatch dispatch

Labels: `category:enhancement`

**Outcome:**
Every one of the fifteen standard cards at `standards/*.md` becomes true
and enforced as ratified in the #133 triage: a renamed detector fleet
(`*-audit`) with card-namespaced rule ids and a common `--list-rules`
interface; a three-rung gate vocabulary (commit gate / push gate / CI
gate) defined once and cited by fixed name from every Enforce cell; three
new detectors (testing-audit, decisions-audit, standards-audit); the
workflow standard rewritten around issue-overwatch dispatch in Agent
view; the tracking contract rewritten around epics, readiness, and brief
formats; and the judgment suite split into targeted files with its bar
stated.

**Decomposition rationale:**
Strictly sequential chain — every child blocked-by its predecessor —
because the slices share surfaces (the cards, the catalog, the hook
configs, the canonical artifacts); parallel worktrees would conflict
rather than compose. Order inside the chain: the workflow harness first
(built by hand; every later slice is then dispatched through an issue
overwatch as its shakedown), vocabulary before detectors (Enforce cells
cite gate rungs by name), renames before rule work (later slices write
final names once), aggregate checks (standards-audit) after the fleet is
final, judgments last.

**Judgment suspension window:**
The first child suspends the judgment gate (`[tool.judgments].paths =
[]`) so the content-addressed cache doesn't force a judge-fleet re-run on
every slice's card edits; the last child re-declares the suite against
the finished state and re-enables the gate. Between those two merges,
semantic drift is unguarded — by choice, for this epic's duration only.

Source: the design triage recorded on #133.

---

## Leaf 1 — Rewrite the workflow standard around issue-overwatch dispatch

Labels: `category:enhancement`, `mode:direct`, `tests:no`, `phase:build`
Blocked-by: none (chain head)

**Summary:** Rewrite `workflow/workflow.md` around issue-level dispatch
(issue overwatch + Agent view), the AFK/HITL node taxonomy, the spike
mode, the design decompose exit, and PR conventions; state the subagent
return contract in `workflow/skill-authoring.md`; suspend the judgment
gate for the duration of the parent epic.

**Current behavior:**
workflow.md's dispatch is node-level: the human launches one node skill
at a time, hands-off nodes run under the human-only `/goal` wrapper, and
the node taxonomy is HITL/FOTW/mixed. It declares AFK operation
unavailable. PR title/body conventions are folklore in the open-pr skill
— nothing normative governs them. There is no spike concept: every issue
path ends in a PR. The judgment gate re-runs LLM judges whenever watched
bytes change, which this epic's card edits would trigger on every slice.

**Desired behavior:**

workflow.md rewritten:

- **Dispatch.** The unit of dispatch is the issue. The human launches one
  **issue overwatch** per issue in **Agent view** (the official name of
  the `claude agents` dashboard — replaces "claude agents dashboard"
  phrasing throughout). The issue overwatch owns the issue's whole
  traverse: it reads the graph from workflow.md and executes it — the
  node sequence is never hard-coded into any skill — delegating AFK nodes
  to subagents (each subagent gets a fresh context window) and switching
  to direct interview with the user at HITL nodes. Turn boundaries align
  with the human capability points: push tap, HITL node, merge.
- **Two overwatch terms defined.** Left screen = **Agent-view overwatch**
  (fleet scope, recommends what to launch next); right screen = **issue
  overwatch** (one per issue). Two terminals is the user's stated
  comprehension limit — written down as a design constraint.
- **Node taxonomy.** A node is **AFK** (delegated to a subagent) or
  **HITL** (issue overwatch interviews the user directly). FOTW and mixed
  dissolve; a review-style node is an AFK delegation followed by a HITL
  follow-up, sequenced by the issue overwatch. The "AFK: Not available"
  claim flips. AFK nodes stay skills: a subagent's prompt is
  "run /\<skill\> N".
- **`/goal` retired.** All `/goal` launch forms, re-drive prose, and
  goal-condition guidance removed; nothing replaces the wrapper — the
  issue overwatch supervises subagents directly.
- **Terminal report contract**, stated verbatim: a subagent's final
  message MUST begin at character one with exactly `DONE: <one-line
  outcome>` or `ESCALATE: <one-line reason>`; detail follows below; any
  non-matching final message is treated as ESCALATE — malformed fails
  safe, toward the human.
- **ESCALATE semantics.** An escalation always bubbles up to the human,
  with the issue overwatch adding context; the overwatch never overrides
  or self-fixes a node's escalation.
- **Single label writer.** The issue overwatch writes all label updates;
  node skills do work and report. (The skill edits land in the next
  slice; this slice states the contract.)
- **Spike mode.** `mode:spike` joins sdd/direct as a third mode with its
  own path `intake -> spike -> closed`: a timeboxed question whose
  deliverable is an answer, not merged code — findings land in the
  closing comment (plus a Decision Record if a one-way door was crossed);
  no PR; branch and worktree disposable; spikes carry `tests:no`, so the
  full-tuple invariant holds. The spike node runs AFK. If it needs a
  human interview mid-flight, it was design, not a spike. bootstrap-labels
  additionally mints `mode:spike` and the spike node's phase label so the
  "mints exactly these" sentence stays true.
- **Design decompose exit.** `design -->|decompose| epic + ready
  children`: the issue becomes an epic and never builds itself; the
  decomposing design session performs the children's intake, minting them
  as ready leaves with full tuples — no round-trip through intake.
- **Readiness rule.** An issue overwatch may launch on any unblocked
  issue — intake is its first HITL node. Crossing INTO an implementation
  node requires the issue be a leaf (epics never dispatch) with a
  brief-complete body per the tracking standard.
- **Permissions.** The `⟦AUTONOMOUS-COMMIT-AUTHORIZED⟧` token moves from
  per-node goal text to the issue overwatch's launch prompt, authorizing
  the commit skill for the issue's whole life. Subagent-level tool
  permissions are explicitly out of scope this pass: wide permissions,
  auto mode; the reviewer read-only guarantee is prompt-level for now,
  consciously accepted.
- **PR conventions** absorbed into workflow.md: squash-only merges make
  the PR title/body the permanent commit message on main, so the format
  is normative — title states the change; body = summary + mandatory
  `Closes #N`. The tracking standard's scope statement drops pull
  requests (workflow now owns them).

skill-authoring.md: the FOTW/goal escalation language is replaced by the
subagent return contract (the terminal report format above); escalation
remains a terminal state, not a pause.

pyproject.toml: `[tool.judgments].paths = []`, with a comment naming the
parent epic and the re-enabling final slice. `judgments/doc-consistency.yaml`
stays on disk as drafting reference for that slice.

**Key interfaces:**
- `workflow/workflow.md` — graph (gains spike node + decompose edge),
  label table (gains `mode:spike`), Dispatch, Permissions, node-skill
  contract sections all rewritten
- `workflow/skill-authoring.md` — return contract
- `scripts/bootstrap-labels` — one-line additions for the new labels
- `pyproject.toml` `[tool.judgments]` — suspension
- `standards/tracking/issues.md` — one-line scope ripple only

**Acceptance criteria:**
- [ ] workflow.md contains no FOTW, mixed, or `/goal` references; defines
      Agent view, issue overwatch, Agent-view overwatch, AFK/HITL, spike
      mode and path, decompose exit, readiness rule, PR conventions, and
      the terminal report format verbatim
- [ ] The tuple invariant survives in the doc: every post-intake leaf
      carries a full `(category, mode, tests, phase)`; spikes are
      `tests:no`
- [ ] skill-authoring.md states the subagent return contract
- [ ] Judgment gate suspended with a tracking comment; `make check` green
- [ ] Existing hook suite passes

**Out of scope:**
- The issue-overwatch skill and all node-skill edits (next slice)
- The label-scheme data file (policy-as-data lands with the
  tracking-contract slice)
- Any detector or card-cell changes

---

## Leaf 2 — Build the issue-overwatch skill and align the node skills

Labels: `category:enhancement`, `mode:direct`, `tests:no`, `phase:build`
Blocked-by: Leaf 1

**Summary:** Build the issue-overwatch skill — it reads the workflow
graph and executes it — and align the existing skills: node skills shed
label writing, workflow-overwatch becomes the Agent-view overwatch, the
review skills gain the semantic-contract lenses, and the native
`/code-review` invocation question is settled here.

**Current behavior:**
No issue-overwatch skill exists. The workflow-overwatch skill (fleet
scope) emits per-node launch commands with `/goal` wrappers per the old
dispatch model. Every node skill advances the phase label itself. The
review skills do not enumerate the semantic contracts they should review
against.

**Desired behavior:**
- New skill **issue-overwatch**, launched with an issue number (the
  launch prompt carries the `⟦AUTONOMOUS-COMMIT-AUTHORIZED⟧` token per
  workflow.md). Behavior: read workflow.md's graph and execute it —
  never hard-code the node sequence. Determine the issue's current node
  from its labels. For an AFK node, spawn a subagent prompted
  "run /\<skill\> \<N\>" and parse its terminal report; a final message
  not beginning with `DONE:`/`ESCALATE:` at character one is treated as
  ESCALATE. For a HITL node, do the node's work interviewing the user
  directly. It is the single label writer, updating the phase label at
  each transition. Every ESCALATE bubbles to the human with context
  added; the overwatch never overrides or self-fixes an escalation.
  Before crossing into an implementation node it checks readiness (leaf,
  brief-complete) and escalates if unmet. The capability boundary is
  unchanged: it never pushes, never merges.
- **Node skills** — every skill that serves a graph node (intake,
  design, tdd, build, the sdd skills, the review skills, open-pr, and
  any others workflow.md's node-skill table names): label-update steps
  removed — they do the work and report. Terminal lines conform to the
  return contract (begin at character one).
- **workflow-overwatch** updated to the Agent-view overwatch role: fleet
  scope, recommends the next launch, emits issue-overwatch launch
  commands; no `/goal`, no per-node forms.
- **Review flow settled** (deferred to this slice by explicit ruling):
  decide how the native `/code-review` is invoked under the new model —
  by the issue overwatch directly, by a review subagent, or left to the
  human half — and update `code-pr-review`/`sdd-code-pr-review`
  accordingly. The review skills also gain the ratified **review
  lenses**, enumerating the semantic contracts to review against:
  testing conventions' behavioral focus, Python style's fail-loud rule
  and helpers bar, module design, prose conventions on doc diffs.
- All `/goal` references gone from every skill.

**Key interfaces:**
- `dotfiles/dot-claude/skills/` — the authoring surface (symlink-mirrored
  per skill-management.md)
- workflow.md is read at run time by the issue-overwatch skill — its
  content is referenced, never duplicated into the skill body

**Acceptance criteria:**
- [ ] issue-overwatch SKILL.md exists and conforms to skill-conventions;
      it instructs reading the graph from workflow.md, not a hard-coded
      sequence
- [ ] No node skill writes labels; no skill mentions `/goal` or FOTW
- [ ] Review skills enumerate the semantic-contract lenses; the native
      `/code-review` invocation is decided and documented in the skills

**Out of scope:**
- Subagent-level tool permissions (explicitly deferred by ruling)
- `.claude/agents/` definitions — AFK nodes stay skills

---

## Leaf 3 — Establish the gate and detector vocabulary

Labels: `category:enhancement`, `mode:direct`, `tests:no`, `phase:build`
Blocked-by: Leaf 2

**Summary:** Rewrite `CONTEXT.md` as the repo's vocabulary
disambiguation center (Audit / Gate / Enforcement / Finding), rewrite
`standards/build/enforcement.md` around the three-rung gate ladder, add
the Detectors section to `standards/standard/format.md`, and sweep
"venue" out of the cards in favor of gate language.

**Current behavior:**
CONTEXT.md is an architecture glossary only; nothing defines the
governance terms, and the standards use "venue" informally for blocking
points. enforcement.md describes venues without fixed rung names. The
meta-standard's cell definitions don't distinguish enforcement from
review, and no document states the detector contract.

**Desired behavior:**
- **CONTEXT.md rewritten** as the repo's general vocabulary
  disambiguation center — reorganize freely; do not preserve the old
  structure for its own sake — KEEPING the module/architecture
  vocabulary (the modules card's Define cell points here) and ADDING the
  governance terms:
  - **Audit** — a read-only detector that inspects the repository
    against one standard and emits findings; it never mutates and never
    blocks by itself.
  - **Gate** — an automatic, unmanned blocking point on the path to
    main. Exactly three rungs, with fixed names: **commit gate** (the
    pre-commit suite), **push gate** (`make check`, via the pre-push
    stage), **CI gate** (thin CI).
  - **Enforcement** — an audit stationed at a gate.
  - **Finding** — one output line: `file:line  card.rule  message`.
- `standards/docs/context-content.md` updated in the same slice, so the
  contract keeps describing the actual artifact as the glossary broadens
  beyond architecture.
- **enforcement.md rewritten** around gate vocabulary — the word "venue"
  disappears from its frontmatter, headings, and tables. The three rungs
  are defined once, here; every card's Enforce cell cites them by these
  names. An **Outside the gates** section lists, as references, the two
  check-running non-gates: (a) the agent ritual — node skills run
  `make check` before committing and before opening a PR; the normative
  rule lives in workflow.md's node-skill contract, this row points
  there; (b) the workspace sweep tool — on demand and via the weekly
  ritual; reports, never blocks. GitHub sits outside every gate. The Map
  table keeps current detector names — renames are a later slice.
- **format.md** gains a **Detectors** section, the normative home of the
  detector contract: the north star — one detector script per card,
  explicitly not mandatory (a card may honestly audit `none`); scripts
  stay thin shims over `src/dev_playbook` modules; rule ids are
  namespaced by the card whose question they answer (`card.rule` — named
  after the question, never the tool); every detector answers
  `--list-rules`; findings use the format above. Cell definitions swap
  venue for gate language, and the Enforce definition gains: enforcement
  is automatic and continuously in effect; a code review is a one-time
  factory gate and never an Enforce pointer.
- **All fifteen cards**: "venue" wording replaced; Enforce cells cite
  rungs by fixed name, keeping current detector names.

**Key interfaces:**
- `CONTEXT.md`, `standards/docs/context-content.md`
- `standards/build/enforcement.md`, `standards/standard/format.md`
- `standards/*.md` — the fifteen cards

**Acceptance criteria:**
- [ ] The word "venue" no longer appears in `standards/`, `CONTEXT.md`,
      or the cards
- [ ] CONTEXT.md defines all four governance terms and retains the
      architecture vocabulary
- [ ] format.md's Detectors section states the north star, card
      namespacing, `--list-rules`, and the finding format; its Enforce
      definition carries the enforce-vs-review sentence
- [ ] Every card's Enforce cell cites gates by rung name
- [ ] context-content.md accurately describes the rewritten CONTEXT.md

**Out of scope:**
- Detector renames and enforcement.md Map re-rows (next slice)
- Any code changes

---

## Leaf 4 — Rename the detector fleet to the audit vocabulary

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 3

**Summary:** Rename six detectors — python-lint→python-audit,
okf-lint→okf-audit, ref-check→ref-audit, judgments-lint→judgments-audit,
internal-skill-audit→skill-audit, sweep→workspace-audit — across every
surface where the names appear.

**Current behavior:**
The fleet's naming is mixed (-lint, -check, sweep) and predates the
ratified vocabulary in which every read-only detector is an audit.
repo-audit is the only conformant name.

**Desired behavior:**
The six renames applied everywhere the names appear: script filenames
under `scripts/`, hook ids in `.pre-commit-hooks.yaml`, dev-playbook's
own `.pre-commit-config.yaml` local block, the canonical consumer config
`standards/build/canonical/.pre-commit-config.yaml`, the `scripts/README.md`
and `scripts/index.md` tables, enforcement.md's Map rows, every card's
Audit cell, Makefile and CI references, tests, and doc prose. `repo-audit`
keeps its name (already conformant); `judgments-run` keeps its name (a
runner, not a detector). format.md's Drift section names workspace-audit
where it said "workspace-level sweeps". Distribution: the renames ride
the existing pre-commit pin — consumer repos pick them up at their next
deliberate rev bump; no per-repo adoption steps, and breaking consumers
is accepted (they conform later).

**Key interfaces:**
- Hook ids are the public API consumer repos pin — the id set changes
  here, deliberately, all surfaces together.

**Acceptance criteria:**
- [ ] No live reference to any old name remains in the repo (decision
      records and other frozen history exempt)
- [ ] Hook-id sets across `.pre-commit-hooks.yaml`, the local block, and
      the canonical config remain mutually consistent
- [ ] Full test suite and hook suite green under the new names

**Out of scope:**
- Rule-id changes, new rules, `--list-rules` (next slice)
- Any behavior change in any detector

---

## Leaf 5 — Card-namespaced rule ids and --list-rules across the fleet

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 4

**Summary:** Give every detector card-namespaced rule ids and a
`--list-rules` flag, standardize the finding line, harden okf-audit's
registry parse, and add the `docs.description-shape` and
`docs.index-ordering` micro-rules.

**Current behavior:**
Rule ids are tool-flavored or bare (okf-audit's type and index rules;
python-audit's no-future-annotations, empty-init, and test-privacy
family). No detector enumerates its rules machine-readably. okf-audit's
registry parse silently skips a malformed row of document-types.md's
`## Types` table — the type drops out of the registry, so every doc
using it fails "not in the registry" in the wrong place while the actual
defect goes unreported. Nothing checks frontmatter description shape or
index ordering.

**Desired behavior:**
- Every detector under `scripts/` answers `--list-rules`: prints its
  rule ids, one per line, and exits 0. This is the interface the
  meta-standard's detector (a later slice) consumes to build the
  card↔rule matrix.
- Rule ids renamed after the card whose question each rule answers:
  - okf-audit → `docs.*` for bundle rules (frontmatter typing, index
    freshness) and `instrument.*` for instrument-spec rules
  - python-audit → `python.no-future-annotations`, `python.empty-init`;
    its test-privacy family is NOT renamed here — a later slice
    relocates it to the testing detector
  - repo-audit → `build.*`, with its harness-file rules as
    `claude-code.*`
  - judgments-audit → `judgments.*`; skill-audit → `claude-code.*`;
    workspace-audit's existing checks get card prefixes (settings →
    `tracking.*`, pin staleness → `build.*`)
- Finding lines everywhere: `file:line  card.rule  message`.
- okf-audit registry hardening: every non-header `|` row of the
  `## Types` table must match the exact row shape — backticked Title
  Case name in the first cell — or okf-audit emits `docs.registry-row`
  at the table itself. The silent skip is gone.
- New `docs.description-shape`: frontmatter `description` carries no
  trailing period — a few lines in okf-audit's existing frontmatter
  pass. The soft description rules (~20 words, one breath) stay prose.
- New `docs.index-ordering`: within each group of an `index.md`, entries
  are alphabetical by link title (case-insensitive, README first) unless
  the index's intro prose declares a meaningful order (e.g. "in reading
  order"); document-types.md's registry table ("Listed alphabetically")
  is checked the same way.

**Key interfaces:**
- `--list-rules` — new common flag on every detector, exit 0, one rule
  id per line
- Exit contract unchanged otherwise: 0 clean / 1 findings / 2 tool error

**Acceptance criteria:**
- [ ] Every detector answers `--list-rules`; every listed id is
      card-prefixed
- [ ] A malformed registry row produces a `docs.registry-row` finding at
      the table (test proves the silent skip is gone)
- [ ] `docs.description-shape` and `docs.index-ordering` implemented;
      dev-playbook clean under both at merge
- [ ] Full suite green

**Out of scope:**
- Relocating the test-privacy family (testing-detector slice)
- New detectors; the card↔rule matrix itself

---

## Leaf 6 — Require every instrument spec to name its consumer

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 5

**Summary:** Add the named-consumer rule to the instrument standard —
every Instrument Spec carries an "Employed by" line — and have okf-audit
check for it.

**Current behavior:**
`instruments/datasheet.md` and `instruments/file-graph.md` are
prescriptive contracts, but nothing records which standard, skill, or
ritual demands their readings; an orphaned instrument is
indistinguishable from a live one.

**Desired behavior:**
- `standards/instrument/format.md` requires every Instrument Spec to
  carry an **"Employed by"** line naming the standard, skill, or ritual
  that demands its readings, and states the cadence rule: reading
  cadence belongs to the consumer, never to the instrument standard —
  on-demand is the device's contract; a ritual wanting fresh readings
  states that in the ritual's own doc, which the Employed-by line points
  at. No instrument is bound to the weekly loop by this standard.
- Both existing specs gain the line.
- okf-audit gains `instrument.employed-by`: section presence in every
  `type: Instrument Spec` doc. ref-audit already verifies the link
  resolves.
- The instruments card's Audit cell annotation names the new rule.

**Acceptance criteria:**
- [ ] format.md states the Employed-by rule and cadence ownership
- [ ] Both specs carry the line; the links resolve
- [ ] `instrument.employed-by` appears in okf-audit `--list-rules`; a
      spec missing the section produces a finding (test)

**Out of scope:**
- A dedicated instruments detector (deliberately none — the north star
  is explicitly not mandatory)
- New instruments or changes to the specs' contracts

---

## Leaf 7 — Carve testing-audit out of python-audit; delegate docstrings to ruff

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 6

**Summary:** Build testing-audit — the test-privacy family moves over
from python-audit, plus mirror-layout and no-logic rules — and enable
ruff's pydocstyle rules in the canonical pyproject; re-cell the testing
and python cards.

**Current behavior:**
python-audit owns the test-privacy family, which answers the testing
standard's question, not Python's. Nothing checks test-tree mirroring or
logic in test bodies. The docstring conventions in
`standards/python/style.md` are unenforced prose. The testing card's
Enforce cell leans on green pytest, which is the build standard's
gate-ladder story, not test-writing style.

**Desired behavior:**
- New detector **testing-audit** (thin shim over `src/dev_playbook`),
  published hook wired into all pre-commit surfaces:
  - `testing.no-private-access` — moved from python-audit: a test file
    must not import or reach into a private name (`_foo`) of a non-test
    module; dunders are public.
  - `testing.mirror-layout` — pure path check of the mirror rule in
    `standards/testing/conventions.md`: `src/x/y.py` ↔
    `tests/x/test_y.py`.
  - `testing.no-logic` — AST rule: no `if`/`else` and no `try`/`except`
    inside test bodies — exactly the two constructs the contract bans;
    loops stay legal.
- python-audit keeps exactly `python.no-future-annotations` and
  `python.empty-init`.
- The canonical `pyproject.toml` enables ruff's pydocstyle rules (the
  `D` family) with a per-file ignore for `tests/`; dev-playbook's own
  pyproject adopts and the repo goes clean. Fail-loud, module layout,
  and the helpers bar get no detector — they are review lenses by
  ruling.
- Cards: **testing** — Audit = testing-audit (three rules); Enforce =
  commit gate; the pytest line leaves the Enforce cell. **python** —
  Audit = python-audit + ruff (check, format, D rules) + mypy; Enforce =
  commit gate; push gate (mypy via `make check`).

**Acceptance criteria:**
- [ ] testing-audit exists with the three card-prefixed rules and
      `--list-rules`; wired at every hook surface
- [ ] The privacy family is gone from python-audit
- [ ] D rules enabled canonically and locally; repo clean
- [ ] Both cards re-celled; full suite green

**Out of scope:**
- Detectors for the semantic testing rules (behavioral focus etc.) —
  review lenses only

---

## Leaf 8 — Broaden ADRs to Decision Records; add decisions-audit

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 7

**Summary:** Generalize the record kind — `docs/decisions/`,
`records.md`, registry row "Decision Record" — state the immutability
rule, and add decisions-audit (sequential numbering + status vocabulary)
as a published hook for all repos.

**Current behavior:**
The record kind is ADR-specific: `docs/adr/`,
`standards/decisions/adrs.md`, registry row `ADR`. Numbering and status
vocabulary are unchecked; nothing states when a record's body freezes.

**Desired behavior:**
- One generic record kind, `type: Decision Record`: directory
  `docs/adr/` → `docs/decisions/`; contract `adrs.md` → `records.md`;
  the `## Types` registry row `ADR` → `Decision Record`, with one line
  mapping the industry term ADR to the architectural subset. Same
  `0001-slug` numbering, same bar for what merits a record, same
  template. Scope rule: repo decisions live in that repo; workspace
  decisions live in dev-playbook. Existing records migrate (paths +
  frontmatter); all references updated.
- **Immutability rule** stated in records.md: a record's body is frozen
  once merged via PR — development-branch edits before merge are fine;
  after merge only the `status` key may change; reversal means a new
  record plus `superseded by 0NNN` on the old one. Deliberately no
  deterministic check for immutability.
- New detector **decisions-audit**, published hook in the canonical
  suite (all repos):
  - `decisions.sequential-numbering` — contiguous `0001..N`,
    zero-padded, no duplicates
  - `decisions.status-vocabulary` — status values from the contract's
    vocabulary
  Frontmatter shape and index freshness remain okf-audit's.
- decisions card: Audit = decisions-audit; Enforce = commit gate
  (canonical suite); Adopt = none.

**Acceptance criteria:**
- [ ] Migration complete: no `docs/adr/` remains; registry row updated;
      references resolve
- [ ] records.md states the immutability rule and the ADR mapping
- [ ] decisions-audit with the two card-prefixed rules and
      `--list-rules`, wired at all hook surfaces
- [ ] Card re-celled; full suite green

**Out of scope:**
- CONTEXT.md rejected framings — explicitly not Decision Records
- Retro-editing any existing record's body

---

## Leaf 9 — Build standards-audit, the meta-standard's detector

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 8

**Summary:** Build standards-audit — card layout, catalog ordering, the
bidirectional card↔rule matrix, multi-surface hook consistency, and
concept-doc coverage — wired in dev-playbook's local pre-commit block
only.

**Current behavior:**
The meta-standard's deterministic rules are enforced piecemeal or not at
all: okf-audit carries catalog rules that answer the meta-standard's
question; nothing checks that a card's Audit cell and the detectors'
actual rules agree in either direction; nothing checks the hook surfaces
agree with each other; an orphaned concept doc — normative prose no card
reaches — sits in the bundle undetected.

**Desired behavior:**
New detector **standards-audit** (rules `standard.*`), wired in
dev-playbook's local block only — it has no meaning in consumer repos
(precedent: skill-audit's local wiring):

- `standard.card-layout` — every `standards/<name>.md` is a card with
  the four cells in order; contracts live in sub-directories (the
  flat=card layout).
- `standard.catalog-order` — the catalog `standards/index.md` ordering
  rule; okf-audit sheds its catalog rules to here.
- `standard.rule-matrix` — the bidirectional card↔rule check, derived
  from every detector's `--list-rules`: each `card.*` prefix belongs to
  a card whose Audit cell cites the detector carrying it, and each
  Audit-cell detector citation is backed by at least one rule carrying
  that card's prefix. Non-detector Audit-cell pointers (e.g. a judgment
  file) sit outside the matrix.
- `standard.hook-surfaces` — hook-id sets equal across
  `.pre-commit-hooks.yaml`, the dev-playbook local block, and the
  canonical consumer config (modulo the declared local-only set);
  `scripts/README.md` table complete; every hook cited by at least one
  card's Audit cell. (One detector may carry several cards' rules and
  so be cited by several cards — okf-audit serves both docs and
  instruments.)
- `standard.doc-coverage` — every concept doc in the OKF bundle is
  reachable from at least one standard card, directly or transitively
  through cell pointers; the reachability definition — which edges
  count, which doc types are exempt (READMEs, indexes, and similar
  structural types) — is documented with the rule.

Meta card `standards/standard.md`: Audit = standards-audit. okf-audit
and ref-audit are deliberately NOT cited here — they cover the cards as
ordinary docs under `docs.*` rules, accounted on the docs card; citing
them here would fail the rule-matrix's second direction. Enforce =
commit gate via the local block. (The epic's final slice adds a
judgments pointer to this cell; non-detector pointers sit outside the
matrix.)

**Acceptance criteria:**
- [ ] Five card-prefixed rules with `--list-rules`; local-block wiring
- [ ] okf-audit no longer carries catalog rules
- [ ] Matrix check proven by tests in both directions (an uncited rule
      prefix fails; an unbacked Audit citation fails)
- [ ] dev-playbook clean under all five rules at merge — zero orphan
      docs
- [ ] Full suite green

**Out of scope:**
- Consumer-repo wiring
- Card-cell honesty semantics — the judgments' territory

---

## Leaf 10 — Rewrite the tracking contract; add the workspace-audit rules

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 9

**Summary:** Reorganize `standards/tracking/issues.md` around roles
(epic/leaf), readiness, and brief formats; make the label scheme
policy-as-data; give workspace-audit the tracking and workflow rules.

**Current behavior:**
issues.md covers the brief format, vertical slices, and relationships
but predates the roles/readiness model. The label scheme is hard-coded
inside bootstrap-labels. workspace-audit checks GitHub settings drift
and stale pins only; nothing checks label schemes, tuple validity,
brief shape, or epic shape in live repos.

**Desired behavior:**
- **issues.md reorganized** around:
  - **Roles** — exactly two: **epic** and **leaf**. An epic is never
    built directly — no branch, no PR, no phase label; category label
    only; the role is DERIVED from having sub-issues (no epic label —
    same principle as blocked being derived, never a label). Epic body
    = outcome + decomposition rationale; it never duplicates the native
    sub-issue list. "A design session produces an epic" is named as a
    pattern.
  - **Readiness** — a lifecycle position, not a kind: work is
    dispatched only on a leaf whose body meets the brief standard
    (industry: Definition of Ready); the refinement interview is the
    promotion step.
  - **Brief formats** — the build-leaf brief (current format), the
    spike brief (timeboxed question; deliverable is an answer; findings
    in the closing comment), and the epic body.
  - **Relationships and vertical slices** — kept as-is, explicitly.
  - The settings contract stays; settings repairs stay manual — the
    audit reports, the weekly ritual fixes, and no repair tool is ever
    built (admin permissions are too broad to automate).
- **Label scheme as policy-as-data**: a canonical scheme data file
  (home and format at the implementer's discretion) that
  bootstrap-labels mints from. workflow.md's graph and label table
  remain the semantic authority — the node set IS the phase-label
  inventory. Scheme-file-vs-graph consistency is deliberately left to a
  judgment (declared in the epic's final slice), not a parser.
- **workspace-audit** (categorical responsibility: workspace-scope
  facts readable over `gh api`; it reports and never blocks — GitHub
  sits outside every gate) gains:
  - `tracking.label-scheme` — live repos carry exactly the scheme
  - `tracking.no-blocked-label` — no repo mints a blocked label
  - `tracking.issue-brief-shape` — ready leaves carry the brief's
    required headings
  - `tracking.epic-shape` — an issue with children carries no phase
    label
  - `workflow.tuple-valid` — every open post-intake leaf carries a
    full valid tuple; its phase names a real graph node
  The final rule list settles as the contract lands.
- Cards: tracking and workflow Audit cells updated; Enforce stays
  `none` for both — structural: GitHub sits outside every gate; the
  human dispatcher and the escalation contract are the integrity
  mechanism.

**Acceptance criteria:**
- [ ] issues.md states roles, readiness, all three brief formats,
      relationships, and slices
- [ ] Scheme data file exists; bootstrap-labels mints from it (including
      `mode:spike` and the spike phase label)
- [ ] workspace-audit `--list-rules` shows the tracking and workflow
      rules; each is exercised by a test
- [ ] Both cards updated; full suite green

**Out of scope:**
- The scheme-vs-graph judgment (final slice)
- Repairing any repo's labels or settings

---

## Leaf 11 — Author the shell conventions; add shfmt to the canonical suite

Labels: `category:enhancement`, `mode:direct`, `tests:no`, `phase:build`
Blocked-by: Leaf 10

**Summary:** Fill the shell card's Define gap with
`standards/shell/conventions.md` — boundary, strict mode, declared bash,
shellcheck-clean — and add shfmt beside shellcheck in the canonical
suite.

**Current behavior:**
The shell card's Define cell is an admitted gap. Shell exists in the
workspace only as glue: sourced `.bashrc.d` fragments,
`bin/sync-dotfiles.sh`, the box `gate.sh`, Make recipes, CI `run:`
lines. shellcheck is in the canonical suite; shfmt is not; the boundary
rule is stated nowhere.

**Desired behavior:**
- New contract `standards/shell/conventions.md`, four rules:
  1. **Boundary** — shell is glue only; code needing a function, an
     array, or parsing becomes a Python `scripts/` shim over `src/`.
  2. **Strict mode** — every executable script opens
     `#!/usr/bin/env bash` + `set -euo pipefail`; sourced fragments
     (`.bashrc.d/*`) carry neither, since strict mode in a sourced file
     kills the parent shell.
  3. **Bash, declared** — bashisms are fine; POSIX-sh portability is a
     non-goal.
  4. **shellcheck-clean** — any `# shellcheck disable=` carries a
     same-line reason comment.
- **shfmt** joins shellcheck in the canonical
  `.pre-commit-config.yaml` and dev-playbook's own — the shell mirror
  of the ruff check + ruff format pairing. Existing shell formatted.
- Card: Define = conventions.md; Audit = shellcheck + shfmt, explicitly
  marked third-party-only — rules 1–3 are prose-only by choice, so the
  gap reads as chosen, not forgotten; Enforce = commit gate; Adopt =
  none.

**Acceptance criteria:**
- [ ] conventions.md exists in the bundle (frontmatter, index row) and
      states the four rules
- [ ] shfmt wired in both configs; existing shell passes both tools
- [ ] Executable scripts carry strict mode; sourced fragments don't
- [ ] Card re-celled with the third-party-only marking

**Out of scope:**
- A first-party shell detector
- Rewriting any existing shell into Python

---

## Leaf 12 — Add the skill-mirror rule to skill-audit; retype skill-management

Labels: `category:enhancement`, `mode:direct`, `tests:yes`, `phase:tdd`
Blocked-by: Leaf 11

**Summary:** Give skill-audit the `claude-code.skill-mirror` rule — the
symlink-correspondence check over the committed dotfiles tree — and
retype `skill-management.md` from Guide to Standard.

**Current behavior:**
skill-management.md (type Guide) states a SHALL — every
`.agents/skills/` entry symlinked in `dot-claude/skills/` — but it is
enforced only when `bin/sync-dotfiles.sh` happens to run. A Guide is
read to learn; a Standard is measured against.

**Desired behavior:**
- skill-audit gains **`claude-code.skill-mirror`**, checking the
  committed dotfiles tree for the same three conditions
  sync-dotfiles.sh repairs: every `.agents/skills/` entry is mirrored
  in `dot-claude/skills/`; no stale symlinks; no authored/installed
  name collisions. Auditor/repairer split (precedent:
  bootstrap-labels): the audit reports at the commit gate;
  sync-dotfiles.sh stays the repairer.
- Wired where skill-audit already runs: dev-playbook's local block and
  skill-authoring repos' local blocks.
- skill-management.md retyped Guide → Standard.
- claude-code card cells confirmed: Audit = repo-audit + skill-audit
  including skill-mirror; Enforce = commit gate. Deliberate non-action,
  by ruling: AFK nodes stay skills, so no `.claude/agents/` registry
  row is added to the harness-files contract.

**Acceptance criteria:**
- [ ] `claude-code.skill-mirror` in skill-audit `--list-rules`; each of
      the three conditions produces a finding when violated (tests)
- [ ] skill-management.md is `type: Standard`; okf-audit clean
- [ ] Card updated; full suite green

**Out of scope:**
- Changing sync-dotfiles.sh
- Governance of `.claude/agents/` definitions

---

## Leaf 13 — Reorganize the judgments: split the monolith, state the bar, re-enable the gate

Labels: `category:enhancement`, `mode:direct`, `tests:no`, `phase:build`
Blocked-by: Leaf 12

**Summary:** Split the judgment monolith into `standard-cards.yaml` and
`docs-match-code.yaml`, state the judgment bar and family rule in the
declarations contract, declare the three new judgments, revalidate
everything against the epic's finished state, and re-enable the gate.

**Current behavior:**
The gate has been suspended since the epic's first slice
(`[tool.judgments].paths = []`). All judgments sit in one file,
`judgments/doc-consistency.yaml`: the card-honesty checks plus a
handful of doc-vs-code drift guards. declarations.md does not state
what merits a judgment. The subset pattern exists exactly once
(`repo-audit-subset-of-standard`).

**Desired behavior:**
- **Split** by claim family: the card-honesty judgments →
  `judgments/standard-cards.yaml`; the doc-vs-code drift guards →
  `judgments/docs-match-code.yaml` (the renamed remainder). Discovery
  already globs `judgments/*.yaml` once the paths glob is restored —
  the split is config-free.
- **Revalidate every judgment against the finished state**: the epic
  changed cards, detectors, and contracts under them — claims and
  evidence paths are updated to match reality before the cache fill.
- **declarations.md** gains the **bar** — a judgment is targeted
  semantic glue at a high-risk point; never a catch-all, never a
  blanket family over a doc population — and the **family rule**: one
  YAML file per claim family.
- **Three new judgments**:
  - script-responsibility — every script under `scripts/` has one
    categorical responsibility aligned with one standard; evidence:
    the `scripts/README.md` ownership tables.
  - scheme-vs-graph — the label-scheme data file stays consistent with
    workflow.md's graph and label table (docs-match-code family).
  - claude-md-subset — dev-playbook's CLAUDE.md content is a subset of
    what the claude-content contract permits.
- **Subset-pattern disposition**: two instances now exist
  (repo-audit-subset-of-standard, claude-md-subset). Either restate
  both under a documented claim template with a home in the judgments
  standard, or land a Decision Record that two instances don't warrant
  one. One of the two outcomes must merge.
- **Cards**: the judgments card's Audit cell states the division —
  judgments-audit is the deterministic detector (declaration shape);
  judgments-run is the semantic detector (it dispatches judges;
  verdicts are its findings) — the one card where an audit is an LLM.
  Enforce cites fixed rungs: judgments-audit at the commit gate; the
  pytest cache gate at the push gate (`make check`). Adopt keeps
  consuming.md. The meta card's Audit cell gains the
  `judgments/standard-cards.yaml` pointer.
- **Gate re-enabled**: the paths glob restored; the cache filled (one
  judge-fleet run); `make check` green.

**Acceptance criteria:**
- [ ] Two family files; `doc-consistency.yaml` gone
- [ ] declarations.md states the bar and the family rule
- [ ] Three new judgments declared and passing
- [ ] Subset disposition landed — template or Decision Record
- [ ] Gate live: paths restored, cache filled, `make check` green
- [ ] Judgments and meta cards updated

**Out of scope:**
- New blanket judgment families (the bar forbids them)
- Changes to the cache-gate mechanism itself

---

## Appendix — decision coverage

Traceability from the triage ledger's numbered decisions to the leaves
above. Split decisions land where each artifact lands.

| Decision | Leaf |
|---|---|
| 1 north star | 3 (stated in format.md Detectors) |
| 2 renames | 4 |
| 3 standards-audit | 9 |
| 4 testing-audit split | 7 |
| 5 okf sheds catalog rules | 9 |
| 6 card-namespaced ids + --list-rules | 3 (contract), 5 (implementation), 9 (matrix) |
| 7 monolith split | 13 |
| 8 bar + family rule | 13 |
| 9 enforce-vs-review | 3 |
| 10 CONTEXT.md rewrite | 3 |
| 11 policy-as-data | 10 (label scheme); registry half resolved as stay-in-doc (see 28) |
| 12 gate vocabulary named once | 3 |
| 13 script-responsibility judgment | 13 |
| 14 workspace-audit ↔ weekly review | PARKED post-epic (handoff paragraph for select-measure-learn) |
| 15 distribution default | 4 (stated in brief; no doc change ordered) |
| 16–18 Decision Records | 8 |
| 19–25 tracking redesign | 10 (21's design-session pattern included) |
| 26–27 instruments | 6 |
| 28 registry hardening / ADR row | 28a → 5, 28b → 8 |
| 29–31 shell | 11 |
| 32 venue→gate sweep | 3 |
| 33–35 semantic-cluster detectors | 7 |
| 36 review lenses | 2 |
| 37 modules (CONTEXT.md vocabulary preserved) | 3 |
| 38 prose all-none | non-action, card already honest |
| 39–40 enforcement.md rewrite + Map | 3 (rewrite); Map rows ride 4, 7, 8, 9, 11 |
| 41 repo-audit build.* | 5 |
| 42 canonical-artifact ripples | 7 (pyproject), 11 (shfmt), 4/7/8 (hook defs) |
| 43–45 meta-standard | 3 (43, 44), 9 (45; judgments pointer lands in 13) |
| 46–48 docs | 5 (46, 47), 3 (48) |
| 49–51 judgments bookkeeping | 5 (49), 13 (50, 51) |
| 52 legibility all-none | non-action, card already honest |
| 53–55 claude-code | 12 (53, 54), 5 (55 namespacing; non-action note in 12) |
| W1–W11, Q1–Q5 workflow redesign | 1 (contract), 2 (skills); W5 → 10; W6 → 10 |
| Q6 /code-review invocation | 2 (resolved at build time, by ruling) |
| Seed drafts (#133 comment) | 1 → 9 (doc-coverage), 2 → 5 (index-ordering), 3 → 13 (subset judgment + disposition) |
