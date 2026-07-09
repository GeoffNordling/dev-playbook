# Issue #133 — per-card triage checkpoint

Transient session working notes, committed as a crash checkpoint. Lives in
`tmp/` because `md.classify` excludes the root `tmp/` scratch tree from the
OKF bundle (no frontmatter/index/type rules apply). DELETE THIS FILE before
the PR for #133 opens.

Branch state at checkpoint: `issue-133` at d1aa5d1 (pushed), tree otherwise
clean, all gates green (473 pytest, 21 judgments cached). PR not opened; no
epic or sub-issues created yet (deliberately held). Seed issue drafts live
verbatim in a comment on GitHub issue #133.

## Standing directives (user rulings, hold for the whole issue)

1. Do NOT worry about breaking consumer repos — set the best standard at
   this level; the other repos conform later. (Overrules any
   pin/compatibility caution, including hook renames.)
2. Enforce = automatic, runs repeatedly, constantly in effect. A code
   review is a one-time factory gate — never an Enforce pointer. Different
   kinds of things.
3. Judgments are limited, targeted semantic glue at high-risk points
   (origin: section-citation staleness). Never a catch-all, never blanket
   families over doc populations.
4. Empty card cells are bare `none` — no accepted/deferred annotations, no
   issues minted for gaps we choose not to build. "We won't forget — we can
   always look and see what's none."
5. Talk intention and high-level design before implementation.
6. Write this ledger for its real reader: a fresh-context agent
   implementing forward from current state. State what IS and what to
   DO; never narrate proposals, withdrawals, or who said what in a
   conversation the reader never saw.

## Ratified design decisions

1. North star: ONE detector script per card (not mandatory — prose keeps
   bare `none` today). Scripts stay thin shims over `src/dev_playbook`
   modules, so splits duplicate no logic.
2. One word for detectors: **audit**. Renames: python-lint -> python-audit,
   okf-lint -> okf-audit, ref-check -> ref-audit, judgments-lint ->
   judgments-audit, internal-skill-audit -> skill-audit (proposed), sweep ->
   workspace-audit; repo-audit keeps its name; new testing-audit,
   standards-audit, decisions-audit (pending Card 1 answers). All five hook
   surfaces update together.
3. New `standards-audit` owns the meta-standard's deterministic rules:
   flat=card layout, catalog ordering, bidirectional card<->detector
   coverage, and multi-surface hook consistency (hook-id sets equal across
   `.pre-commit-hooks.yaml`, the local block, and the canonical consumer
   config; README table complete; every hook cited by exactly one card's
   audit cell). Wired only in dev-playbook's local block (precedent:
   internal-skill-audit in skill-authoring repos). Supersedes the three
   seed-issue tool placements sketched in the #133 comment.
4. `testing-audit` split out of python-lint; takes the no-private-access
   rule (it belongs to the testing card, not Python).
5. okf-audit sheds catalog rules to standards-audit; keeps OKF bundle rules
   (docs card) and instrument-spec typing (instruments card).
6. Rule ids namespaced by card — `testing.no-private-access`,
   `decisions.sequential-numbering`. Every detector grows `--list-rules`;
   standards-audit derives the card->rule matrix and checks it against the
   cards' audit cells, both directions.
7. Judgment monolith split: the 20 card-honesty judgments move to
   `judgments/standard-cards.yaml`; the 5 remaining doc-vs-code drift
   guards stay in a file renamed `docs-match-code.yaml`. Discovery already
   globs `judgments/*.yaml` (pyproject `[tool.judgments].paths`), so the
   split is config-free. The meta card's audit pointer updates.
8. `standards/judgments/declarations.md` gains the judgment bar (targeted
   glue, never catch-all) and the family rule (one YAML per claim family).
9. `standards/standard/format.md` gains the audit/enforce-vs-review
   distinction (enforce is automatic and continuous; review is one-time).
10. `CONTEXT.md` is REWRITTEN as the repo's general vocabulary
    disambiguation center (user: "You are in charge — don't accept the way
    it was written before"). Gains governance terms: **Audit** (read-only
    detector, inspects against one standard, emits findings, never mutates
    or blocks by itself), **Gate** (automatic, unmanned blocking point on
    the path to main — commit gate, push gate, CI gate; ratified over
    "venue"), **Enforcement** (an audit stationed at a gate), **Finding**
    (one output line: `file:line  card.rule  message`).
11. Policy-as-data: the label scheme moves out of bootstrap-labels into a
    canonical data file shared by auditor and repairer; same lens applies
    to the okf type registry (a judge flagged its imprecision).
12. Gate vocabulary named once in the build standard's enforcement doc;
    enforce cells cite rungs by fixed names.
13. New targeted judgment: every script under `scripts/` has one
    categorical responsibility aligned with one standard (evidence:
    `scripts/README.md` ownership tables).
14. workspace-audit (ex-sweep) binds to the select-measure-learn weekly
    review ritual. PARKED until after implementation: draft a short
    paragraph for that repo's agent telling it it owns running
    workspace-audit during the weekly review (wait so the paragraph names
    the renamed tool).
15. Distribution default: every new detector rides the existing pre-commit
    pin (consumers get it on rev bump); only judgment declarations and
    label bootstrapping need per-repo adoption steps.

## Presentation rule (user)

Name categories by the question they govern — a short phrase, never a bare
tracking label like "Card 1".

## RESOLVED: Decision Records — how are hard-to-reverse decisions recorded?

16. The record kind broadens beyond ADRs: one generic **Decision Record**
    (`type: Decision Record`), directory `docs/decisions/` (ex `docs/adr/`),
    contract renamed `standards/decisions/records.md` (ex adrs.md), same
    0001-slug numbering, same bar, same template; one line mapping the
    industry term ADR to the architectural subset. Scope: repo decisions in
    that repo, workspace decisions in dev-playbook. CONTEXT.md rejected
    framings are NOT Decision Records (current-state vs why-at-a-time).
17. Immutability rule (to be stated in records.md): body frozen once
    MERGED via PR — development-branch edits before merge are fine; only
    the `status` key may change after; reversal = new record +
    `superseded by 0NNN`. NO deterministic check — overkill, per user.
18. `decisions-audit` (new, published hook, all repos): owns
    decisions.sequential-numbering (contiguous 0001..N, no dupes, padding)
    and decisions.status-vocabulary. Frontmatter shape + index freshness
    stay with okf-audit under knowledge-organization.

Card lands as: Define records.md / Audit decisions-audit / Enforce commit
gate (canonical hook suite) / Adopt none.

## RESOLVED: Tracking — how is work tracked? (way-of-working redesigned)

Meta-rule (user): every category starts with a zoom-out redesign of the way
of working; implementation triage only after.

19. Word ratified: **epic**. The role: an issue never built directly — no
    branch, no PR, no phase label; category label only. DERIVED from having
    sub-issues (per the existing "blocked is derived, never a label"
    principle) — no epic label. Epic body = outcome + decomposition
    rationale; never duplicates the native sub-issue list.
20. Two roles only: epic and leaf. Readiness is a lifecycle position (phase
    label), not a kind. THE DISPATCH RULE: the factory only dispatches a
    leaf whose body meets the brief standard (industry: Definition of
    Ready). HITL refinement interview = the promotion step (user's
    experiment validated as industry norm: backlog refinement).
21. No RFC machinery (right-sized for solo): design sessions are ephemeral;
    durable outputs = Decision Records (one-way doors) + epic body
    (coordination) + ready leaf briefs (work). "Design session produces an
    epic" named as a pattern; #133 is the worked example.
22. **Spike** ratified as the second leaf brief format (XP term): timeboxed
    question, deliverable = an ANSWER not merged code, closes without a PR;
    typically a child of an epic with the implementation leaf blocked-by
    the spike; findings land in the closing comment (+ Decision Record if
    one-way door); prototype branches die with the spike.
23. Vertical slices kept (user, explicitly). Settings contract kept;
    settings repairs stay manual/by-hand (admin perms too broad) — audit
    reports, weekly ritual fixes, no repair tool ever.
24. Audit candidates once the contract is rewritten (workspace-audit, gh
    api scope — serves both build and tracking cards; its categorical
    responsibility = "workspace-scope facts readable over gh api"):
    tracking.settings-drift (exists), tracking.no-blocked-label,
    tracking.issue-brief-shape (ready leaves carry required headings),
    tracking.epic-shape (issue with children has no phase label). Final
    list when contract lands. Enforce: none — GitHub sits outside every
    gate, permanently honest.
25. Contract rewrite: standards/tracking/issues.md reorganized around
    roles (epic/leaf), readiness, brief formats (build leaf / spike /
    epic body), relationships, slices.

PARKED for the Workflow category: PR conventions ownership (tracking card
claims PRs, no contract governs them; open-pr node produces them); label
scheme ownership (tuple semantics = workflow; scheme-intact-in-repo =
tracking?); the dispatch rule's enforcement (it's a workflow-side rule).

## RESOLVED: Workflow — how does an idea become a merged PR?

W1–W6 RATIFIED (user accepted, incl. embedded recommendations: W1 spikes
carry tests:no to preserve the tuple invariant; W2 the decomposing
design session does the children's intake, minting them as ready leaves
with full tuples — no round-trip back through intake).

W1. Spike = a third **mode** (mode:spike beside sdd/direct): its own path
    `intake -> spike -> closed`, exits with an answer, never a PR. Spike
    node runs FOTW (delegated learning; DONE: carries findings to the
    closing comment). If it needs a human interview it was design, not a
    spike. Worktree optional, branch disposable, tests: dimension moot.
W2. Design node gains a second exit: `design ->|decompose| epic + ready
    children` — the issue becomes an epic and never builds itself.
    Formalizes the user's HITL-interview->briefs practice and the #133
    pattern with an existing node; no new "plan" node.
W3. Dispatch readiness rule: dispatch requires unblocked AND a leaf (epics
    never dispatch) AND brief-complete. /tdd + /build already escalate on
    bad briefs; the dispatcher checks before burning a session.
W4. PR conventions move INTO workflow/workflow.md (squash-only makes PR
    title/body the permanent commit message on main; today the format is
    folklore in the open-pr skill). Title = the change; body = summary +
    mandatory `Closes #N`. Tracking's governing sentence drops "pull
    requests".
W5. Label scheme: workflow.md's graph + table stay the semantic authority
    ("the set of graph nodes IS the phase-label inventory"); policy-as-data
    canonical scheme file minted by bootstrap-labels and checked in live
    repos by workspace-audit (tracking.label-scheme). Scheme-file-vs-graph
    consistency = a small docs-match-code judgment, not a parser.
W6. Workflow audit: workflow.tuple-valid over gh api (every open
    post-intake leaf carries a full valid tuple, phase names a real node).
    Enforce: none — structural (human dispatcher, GitHub outside gates);
    the skills' escalation lines are the real integrity mechanism.

### Dispatch redesign (RATIFIED with modifications — see each item)

User discovery: AFK nodes ARE possible inside interactive sessions via
subagents. Right screen = one ISSUE-LEVEL agent per issue (not one agent
per node); it walks the graph, delegating AFK nodes to subagents and
switching to interview mode for HITL nodes. Left screen stays
/workflow-overwatch (fleet scope). Two terminals = the user's stated
comprehension limit — a design constraint, write it down.

Facts verified against official docs (code.claude.com):
- Dashboard's official name: **Agent view** (`claude agents`) — use this
  term everywhere; workflow.md's "claude agents dashboard" updates.
- Subagents CANNOT talk to the terminal user (AskUserQuestion blocked);
  only channel = final message to parent. Platform enforces HITL-stays-
  at-issue-agent.
- Each subagent gets a fresh context window (replaces /clear-between-
  nodes for AFK nodes; /clear remains for the issue agent itself).
- Agent definitions (.claude/agents/*.md) support tools allowlist,
  disallowedTools, and model choice — per-node denies become agent
  definitions (reviewer = structurally read-only).
- Nesting possible to depth 5, but standard caps delegation at ONE level
  below the issue agent (user: never plan to dive into layer two).
- No headless requirement; works in subscription-billed interactive
  sessions — the constraint that ruled AFK out is preserved.

W7. RATIFIED. Unit of dispatch = issue. Human launches one issue-level
    agent per issue in Agent view; it owns the issue's whole traverse.
    Turn boundaries align with the human capability points (push tap,
    HITL node, merge) — the agent chains AFK nodes within a turn and
    stops at exactly the boundaries that were already the human's
    rituals.
W8. RATIFIED. Mode taxonomy redraw: nodes are AFK (delegated to a
    subagent) or HITL (issue overwatch interviews the user directly).
    FOTW dissolves. workflow.md's "AFK: Not available" sentence flips.
W9. RATIFIED, modified: /goal retires ENTIRELY (user: "I don't think we
    need goal anymore"). Subagents must EMIT terminal reports in a
    simple, highly standardized, difficult-to-miss format —
    DONE:/ESCALATE: survives as the subagent return contract; the exact
    format gets specified in workflow.md.
W10. RATIFIED, narrowed: token widens — the issue overwatch's single
    launch prompt carries ⟦AUTONOMOUS-COMMIT-AUTHORIZED⟧ for the issue's
    whole life. Subagent-level permissions are OUT OF SCOPE this pass
    (user: wide permissions, rely on auto mode; don't add complexity).
    Consequence, consciously accepted: the reviewer read-only guarantee
    becomes prompt-level, not tool-enforced, for now.
W11. RATIFIED, modified: expand the term, don't replace it. Left screen
    = **Agent-view overwatch** (fleet scope). Right screen = **issue
    overwatch** (one per issue). Both terms defined in workflow.md.

Nesting: NOT strictly capped at one level. User intent: don't go crazy,
but the future direction is that the issue overwatch can "run" an
arbitrary mermaid workflow graph — if the graph nests, fine. Design
principle now (cheap, no engine built): the issue-overwatch skill reads
the graph from workflow.md and executes it, rather than hard-coding the
node sequence.

Ripples: W1–W6 all survive, landing in the rewritten Dispatch prose
(spike node = AFK delegation; design stays HITL at issue-overwatch
level; W3's rule reframed — see open questions). W1–W6 still awaiting
explicit ratification (user skimmed twice, called them reasonable).

### Holistic re-check questions — ALL RESOLVED (user ratified)

Q1. AFK nodes STAY SKILLS (subagent prompt = "run /<skill> N"). One
    authoring surface; "skills are simple, stay simple this pass."
Q2. The issue-overwatch skill is the SINGLE label writer; node skills
    shed their label-update step; subagents do work and report.
Q3. ESCALATE: always bubbles up to the human, context added; the issue
    overwatch never overrides or self-fixes a node's escalation.
Q4. Launch an issue overwatch on any unblocked issue (incl. untriaged —
    intake is its first HITL node); the readiness rule (leaf +
    brief-complete) gates crossing INTO implementation nodes.
Q5. Mixed dissolves: a review node = AFK delegation then HITL follow-up,
    sequenced by the issue overwatch. Taxonomy = two modes; a node may
    sequence them.
Q6. DEFERRED to build time: how the native /code-review gets invoked
    (issue overwatch directly vs review subagent vs human half).

Terminal report format (to state verbatim in workflow.md): the
subagent's final message MUST begin at character one with exactly
`DONE: <one-line outcome>` or `ESCALATE: <one-line reason>`; detail
follows below; any non-matching final message is treated as ESCALATE
(malformed fails safe, toward the human).

Principle endorsed (user: "always a principle we try to maintain
everywhere"): reference-and-read rather than duplicate — the
issue-overwatch skill reads the graph from workflow.md and executes it;
node sequence never hard-coded.

### Card resolution

Define: workflow/workflow.md REWRITTEN — Dispatch around issue
overwatches + Agent view, Skills taxonomy AFK/HITL (FOTW and mixed
dissolve, /goal removed), spike mode + path (W1), design decompose exit
(W2), readiness rule per Q4 (W3), PR conventions absorbed (W4),
terminal report format, both overwatch terms defined.
skill-authoring.md updates for the subagent return contract.
Audit: workflow.tuple-valid via workspace-audit (gh api scope) — open
post-intake leaves carry full valid tuples, phase names a real graph
node, epics carry category only. Label-scheme data file per W5
(bootstrap-labels mints from it; tracking.label-scheme checks live
repos; scheme-vs-graph = one docs-match-code judgment).
Enforce: none — structural (GitHub outside every gate; human dispatcher
+ escalation contract are the integrity mechanism).
Adopt: node skills (updated per Q1/Q2) + NEW issue-overwatch skill +
bootstrap-labels.

## RESOLVED: Instruments — how are purpose-built devices specified and kept conformant?

No way-of-working redesign: spec as prescriptive contract,
invoked-not-adopted, and the deliberate staleness contract for readings
all stand as written in standards/instrument/format.md.

26. Named-consumer rule: format.md requires every Instrument Spec to
    carry an "Employed by" line naming the standard, skill, or ritual
    that demands its readings. okf-audit checks section presence;
    ref-audit covers the link. Both existing specs (datasheet,
    file-graph) gain the line.
27. Reading cadence belongs to the consumer, never the instrument
    standard: on-demand is the device's contract; a ritual wanting
    fresh readings states that in the ritual's own doc (which
    "Employed by" points at). Do not bind any instrument to the weekly
    loop.
28. okf type registry: scripts/okf-lint:76-100 already treats
    document-types.md's `## Types` table as the single source of truth.
    Do NOT extract a separate data file — it would strip the doc's
    table or duplicate it. Two changes: (a) harden the parse — today a
    malformed row (e.g. name missing backticks) is silently skipped,
    dropping its type from the registry so every doc using that type
    fails "not in the registry" at the wrong place; instead, every
    non-header `|` row in `## Types` must match the exact row shape
    (backticked Title Case name, first cell) or okf-audit emits
    docs.registry-row at the table itself. (b) Update the `ADR` row to
    `Decision Record` (see decisions 16–18).

Card resolution: Define format.md + named-consumer rule / Audit
okf-audit (spec typing via registry, catalog freshness, Employed-by
presence — no dedicated instruments-audit; north-star's not-mandatory
clause) / Enforce commit gate via canonical suite (unchanged) / Adopt
none.

## RESOLVED: Shell — how is shell code kept correct?

The workspace is Python-first: scripts/ is all Python; shell exists
only as glue (two sourced .bashrc.d fragments, sync-dotfiles.sh, the
box gate.sh, Make recipes, CI run: lines). The contract's core is the
boundary rule, not style.

29. New contract standards/shell/conventions.md (fills the Define
    cell's admitted gap), four rules: (1) boundary — shell is glue
    only; code needing a function, an array, or parsing becomes a
    Python scripts/ shim over src/; (2) strict mode — every executable
    script opens `#!/usr/bin/env bash` + `set -euo pipefail`; sourced
    fragments (.bashrc.d/*) carry neither, since strict mode in a
    sourced file kills the parent shell; (3) bash, declared — bashisms
    fine, sh portability a non-goal; (4) shellcheck-clean; any
    `# shellcheck disable=` carries a same-line reason comment.
30. shfmt joins shellcheck in the canonical .pre-commit-config.yaml —
    the shell mirror of the ruff check + ruff format pairing.
31. No first-party shell detector: rules 1–3 are prose-only, and the
    Audit cell says so explicitly (third-party tools only) so the gap
    reads as chosen, not forgotten.
32. Sweep all 15 cards replacing the word "venue" with "gate" (the
    ratified vocabulary; CONTEXT.md rewrite defines Gate, decision 10).

Card resolution: Define conventions.md (new) / Audit shellcheck + shfmt
(third-party only, marked as such) / Enforce commit gate via canonical
suite / Adopt none.

## RESOLVED: Semantic cluster — Testing, Python, Modules, Prose

Shared principle: semantic contracts get their teeth at authoring time
(the agent reads the contract) and at PR review — never as Enforce
pointers. The deterministic slivers below are the whole audit story;
every remaining cell is bare none by choice.

33. testing-audit (new detector, split from python-lint) owns three
    rules: testing.no-private-access (the existing privacy.* family
    moves over), testing.mirror-layout (src/x/y.py <-> tests/x/
    test_y.py, pure path check), testing.no-logic (AST: no if/else or
    try/except inside test bodies — exactly the two constructs the
    contract bans; loops stay legal).
34. Testing card's Enforce cell = commit gate (testing-audit in the
    canonical suite). The pytest line leaves the cell: green tests are
    the build card's gate-ladder story, not test-writing style.
35. python-audit keeps python.no-future-annotations and
    python.empty-init. The docstring rule (style.md) is delegated to
    ruff's pydocstyle `D` family, enabled in the canonical
    pyproject.toml with a per-file ignore for tests/ — third-party
    detector over custom code. Fail-loud, module layout, and the
    helpers bar have no detector: review lenses.
36. Review-node skill lists the semantic contracts as its review
    lenses: testing behavioral focus, python fail-loud + helpers bar,
    modules design, prose conventions on doc diffs. (Implementation
    note for the review skill, not a card cell.)
37. Modules card: all-none stands. Its Define cell points at
    CONTEXT.md, so the CONTEXT.md rewrite (decision 10) must preserve
    the architecture vocabulary.
38. Prose card: all-none stands.

Card resolutions: Testing — Define conventions.md / Audit testing-audit
(3 rules) / Enforce commit gate / Adopt none. Python — Define style.md /
Audit python-audit + ruff (check, format, D rules) + mypy / Enforce
commit gate + make check (mypy at the push gate) / Adopt none. Modules
and Prose — Define only, all other cells none.

## RESOLVED: Build — how is a repository laid out, built, and checked?

No redesign — the strongest category; residuals are the vocabulary
rewrite and mechanical ripples of earlier decisions.

39. enforcement.md is rewritten around the ratified Gate vocabulary
    (frontmatter, headings, tables — the word "venue" disappears).
    The gate ladder has exactly three rungs with fixed names every
    card's Enforce cell cites: **commit gate** (pre-commit suite),
    **push gate** (make check via pre-push stage), **CI gate** (thin
    CI). An **Outside the gates** section lists, as references, the
    two check-running non-gates: (a) the agent ritual — node skills
    run make check before committing and before opening a PR; the
    normative rule lives in workflow.md's node-skill contract, this
    row points there; (b) workspace-audit — on demand / weekly
    ritual, reports and never blocks; GitHub sits outside every gate.
40. enforcement.md's Map table re-rows for the detector fleet:
    renames (python-audit, okf-audit, ref-audit, judgments-audit,
    skill-audit, workspace-audit), new rows (testing-audit,
    standards-audit, decisions-audit, shfmt).
41. repo-audit keeps its name; rule ids namespaced build.* and it
    grows --list-rules like every detector.
42. Canonical-artifact ripples land here: pyproject.toml gains the
    ruff pydocstyle config (decision 35), .pre-commit-config.yaml
    gains shfmt + the renamed/new hooks, .pre-commit-hooks.yaml gains
    the new hook definitions.

Card resolution: Define unchanged (build/ + canonical.md) / Audit
repo-audit + workspace-audit / Enforce the three gate rungs cited by
fixed name / Adopt none.

## RESOLVED: Meta-Standard — how are standards declared, cataloged, and kept honest?

43. standards/standard/format.md gains a **Detectors** section — the
    normative home for the detector contract this triage invented:
    the north star (one detector script per card, explicitly not
    mandatory), rule ids namespaced by card (`card.rule`), every
    detector answers `--list-rules`, and the finding line format
    (`file:line  card.rule  message`, matching CONTEXT.md's Finding).
    This is what makes standards-audit's bidirectional card<->rule
    matrix a documented contract.
44. format.md mechanical updates: cell definitions swap "venue" for
    gate language; the Enforce cell definition gains the
    enforce-vs-review sentence (decision 9); Drift item 2's
    "workspace-level sweeps" becomes workspace-audit.
45. Card cells: Audit = standards-audit (principal) + okf-audit +
    ref-audit + judgments/standard-cards.yaml. Enforce = commit gate
    via the canonical suite, with standards-audit wired in
    dev-playbook's LOCAL pre-commit block only (it has no meaning in
    consumer repos). Adopt none.

## RESOLVED: Docs — how is knowledge organized in markdown?

46. okf-audit's rule ids are re-namespaced by CARD, not tool, per
    decision 6: `okf.type` -> `docs.type`, index freshness ->
    `docs.index-freshness`, the registry-row rule (decision 28) ->
    `docs.registry-row`, the Employed-by presence check (decision 26)
    -> `instrument.employed-by`. One detector carries several cards'
    rules; the prefix is what standards-audit's card<->rule matrix
    keys on.
47. New micro-rule `docs.description-shape` in okf-audit: frontmatter
    `description` carries no trailing period. A few lines in the
    existing frontmatter pass (scripts/okf-lint:127-152); the soft
    description rules (~20 words, one breath) stay prose.
48. context-content.md moves together with the CONTEXT.md rewrite
    (decision 10): the contract keeps describing the actual artifact
    as the glossary broadens to governance terms.

Card resolution: Define standards/docs/ unchanged in structure /
Audit okf-audit + ref-audit, card-namespaced rule ids / Enforce
commit gate via canonical suite / Adopt none.

## Remaining agenda

- Per-card pass: Decisions (answers pending) -> Tracking -> Workflow ->
  Instruments (incl. the named-consumer rule, still no verdict) -> Shell
  (define contract must be written) -> semantic cluster (Prose, Testing,
  Modules, Python residual) -> solid-tier residuals (Build, Meta-Standard,
  Docs, Judgments, Claude Code) -> Legibility (likely all-none, fine).
- Each card resolves to: detector rules (namespaced ids), gate, owner
  script, adopt path — or bare `none`.
- Then: conformance epic + sub-issues compiled from this ledger and the
  per-card requirements (seed drafts in the #133 comment fold into the
  standards-audit issue per decision 3). Epic MUST be open before the PR
  merges (PR will carry "Closes #133").
- Then /open-pr 133. User pushes (YubiKey); agent never pushes or merges.
