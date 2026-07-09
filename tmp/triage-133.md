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

## PROPOSED, NOT YET RATIFIED: Workflow — how does an idea become a merged PR?

User has only SKIMMED these six; discuss before treating as decided.
Category taken out of agenda order because tracking's rulings ripple in.

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
