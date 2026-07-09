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

## Card 1 (Decisions) — questions asked, ANSWERS PENDING

Discovered: the card's define cell claims "immutability" but
`standards/decisions/adrs.md` never states an immutability rule.

1. What is the immutability rule? Proposed: body frozen once committed;
   only the `status` frontmatter key may change; reversal = new ADR +
   `superseded by ADR-NNNN`. Then it is prose in adrs.md plus a
   deterministic commit-gate check (staged diff touching an existing ADR
   outside the status line = finding).
2. Numbering: if ADRs are never deleted, assert contiguous 0001..N with no
   duplicates; if deletion is legal, only catch dupes and bad padding.
3. Ownership: new `decisions-audit` owns decisions.sequential-numbering,
   decisions.status-vocabulary, decisions.immutable-body; frontmatter shape
   and index freshness stay with okf-audit under the docs standard.

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
